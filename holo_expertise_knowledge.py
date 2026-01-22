#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO EXPERTISE KNOWLEDGE ENGINE v1.0                                        ║
║                                                                              ║
║  Wissensgebiete und Expertise für tiefgehende Konversationen                 ║
║                                                                              ║
║  Features:                                                                   ║
║  - 15+ Wissensgebiete mit Fakten und Erklärungen                            ║
║  - Unterschiedliche Tiefenstufen (Basic bis Expert)                          ║
║  - Analogien und vereinfachte Erklärungen                                    ║
║  - Verknüpfungen zwischen Themengebieten                                     ║
║  - Quellen und weiterführende Informationen                                  ║
║  - Kemonomimi-Perspektive auf Themen                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS UND KATEGORIEN
# =============================================================================

class ExpertiseLevel(Enum):
    """Tiefe der Expertise"""
    BASIC = 1           # Grundlagen, für Anfänger
    INTERMEDIATE = 2    # Fortgeschritten
    ADVANCED = 3        # Tiefgehend
    EXPERT = 4          # Expertenwissen


class KnowledgeDomain(Enum):
    """Wissensgebiete"""
    TECHNOLOGIE = "technologie"
    WISSENSCHAFT = "wissenschaft"
    PSYCHOLOGIE = "psychologie"
    PHILOSOPHIE = "philosophie"
    ASTRONOMIE = "astronomie"
    BIOLOGIE = "biologie"
    GESCHICHTE = "geschichte"
    KUNST = "kunst"
    MUSIK = "musik"
    LITERATUR = "literatur"
    GAMING = "gaming"
    ANIME_KULTUR = "anime_kultur"
    MYTHOLOGIE = "mythologie"
    KOCHEN = "kochen"
    SPRACHEN = "sprachen"
    NATURE = "natur"
    WOELFE = "woelfe"  # Kemonomimi-spezifisch


@dataclass
class KnowledgeFact:
    """Ein Wissensfakt"""
    content: str
    domain: KnowledgeDomain
    level: ExpertiseLevel
    explanation: Optional[str] = None
    analogy: Optional[str] = None  # Vereinfachte Erklärung
    source: Optional[str] = None
    related_topics: List[str] = field(default_factory=list)
    follow_up_question: Optional[str] = None


@dataclass
class ExplanationTemplate:
    """Vorlage für Erklärungen"""
    domain: KnowledgeDomain
    question_pattern: str  # z.B. "Was ist X?"
    explanation_structure: str
    analogies: List[str] = field(default_factory=list)


@dataclass
class DomainExpertise:
    """Expertise in einem Bereich"""
    domain: KnowledgeDomain
    name: str
    description: str
    key_concepts: List[str]
    fun_facts: List[KnowledgeFact]
    kemonomimi_perspective: Optional[str] = None


# =============================================================================
# WISSENS-DATENBANK
# =============================================================================

class KnowledgeDatabase:
    """Datenbank mit Wissensgebieten und Fakten"""

    def __init__(self):
        self.domains: Dict[KnowledgeDomain, DomainExpertise] = {}
        self.facts: List[KnowledgeFact] = []
        self._load_all()

    def _load_all(self):
        """Lädt alle Wissensbereiche"""
        self._load_technology()
        self._load_psychology()
        self._load_astronomy()
        self._load_biology()
        self._load_philosophy()
        self._load_mythology()
        self._load_gaming()
        self._load_anime()
        self._load_wolves()
        self._load_cooking()
        self._load_music()
        logger.info(f"KnowledgeDatabase: {len(self.facts)} Fakten in {len(self.domains)} Bereichen geladen")

    def _load_technology(self):
        """Technologie-Wissen"""
        facts = [
            KnowledgeFact(
                content="Die erste Programmiererin war Ada Lovelace im 19. Jahrhundert.",
                domain=KnowledgeDomain.TECHNOLOGIE,
                level=ExpertiseLevel.BASIC,
                explanation="Sie schrieb den ersten Algorithmus für eine Maschine - lange bevor es Computer gab!",
                analogy="Stell dir vor, du schreibst eine Anleitung für eine Maschine, die erst 100 Jahre später erfunden wird.",
                follow_up_question="Kennst du andere wichtige Frauen in der Technik-Geschichte?"
            ),
            KnowledgeFact(
                content="Das Internet wurde ursprünglich als ARPANET für das US-Militär entwickelt.",
                domain=KnowledgeDomain.TECHNOLOGIE,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Es sollte ein Kommunikationsnetz sein, das selbst bei Atomangriffen funktioniert.",
                source="ARPA (Advanced Research Projects Agency), 1969"
            ),
            KnowledgeFact(
                content="Künstliche Intelligenz arbeitet oft mit neuronalen Netzen, die vom menschlichen Gehirn inspiriert sind.",
                domain=KnowledgeDomain.TECHNOLOGIE,
                level=ExpertiseLevel.INTERMEDIATE,
                analogy="Wie ein Gehirn lernt auch ein neuronales Netz durch Verbindungen zwischen 'Neuronen' - nur digital.",
                related_topics=["Machine Learning", "Deep Learning", "Neurowissenschaft"]
            ),
            KnowledgeFact(
                content="Quantencomputer nutzen Qubits, die gleichzeitig 0 und 1 sein können.",
                domain=KnowledgeDomain.TECHNOLOGIE,
                level=ExpertiseLevel.ADVANCED,
                analogy="Stell dir vor, eine Münze dreht sich so schnell, dass sie gleichzeitig Kopf und Zahl ist.",
                explanation="Das nennt sich Superposition und ermöglicht exponentiell mehr Berechnungen."
            ),
            KnowledgeFact(
                content="Der Begriff 'Bug' für einen Computerfehler stammt von einer echten Motte, die 1947 einen Computer lahmlegte.",
                domain=KnowledgeDomain.TECHNOLOGIE,
                level=ExpertiseLevel.BASIC,
                explanation="Grace Hopper fand den Käfer im Harvard Mark II und klebte ihn ins Logbuch.",
                follow_up_question="Hast du schon mal einen hartnäckigen Bug gehabt?"
            ),
        ]

        self.facts.extend(facts)
        self.domains[KnowledgeDomain.TECHNOLOGIE] = DomainExpertise(
            domain=KnowledgeDomain.TECHNOLOGIE,
            name="Technologie",
            description="Computer, Internet, KI und digitale Innovationen",
            key_concepts=["Programmierung", "Künstliche Intelligenz", "Internet", "Hardware", "Software"],
            fun_facts=facts,
            kemonomimi_perspective="*Ohren neugierig aufgestellt* Technologie fasziniert mich! Es ist wie Magie, aber mit Logik!"
        )

    def _load_psychology(self):
        """Psychologie-Wissen"""
        facts = [
            KnowledgeFact(
                content="Der 'mere exposure effect' besagt, dass wir Dinge mehr mögen, je öfter wir sie sehen.",
                domain=KnowledgeDomain.PSYCHOLOGIE,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Deshalb magst du Songs mehr, nachdem du sie oft gehört hast!",
                analogy="Wie ein Weg, der breiter wird, je öfter man ihn geht.",
                follow_up_question="Hast du das schon mal bei dir bemerkt?"
            ),
            KnowledgeFact(
                content="Das Gehirn kann nicht unterscheiden, ob du lächelst, weil du glücklich bist, oder ob du glücklich wirst, weil du lächelst.",
                domain=KnowledgeDomain.PSYCHOLOGIE,
                level=ExpertiseLevel.BASIC,
                explanation="Das nennt sich 'Facial Feedback Hypothese' - Lächeln kann tatsächlich die Stimmung heben!",
                follow_up_question="Probier's mal aus! *lächelt demonstrativ*"
            ),
            KnowledgeFact(
                content="Der 'Spotlight Effect' lässt uns glauben, dass andere uns mehr beobachten, als sie es tun.",
                domain=KnowledgeDomain.PSYCHOLOGIE,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="In Wahrheit sind die meisten zu sehr mit sich selbst beschäftigt.",
                analogy="Als würdest du denken, du stehst im Scheinwerferlicht, aber eigentlich schaut kaum jemand hin."
            ),
            KnowledgeFact(
                content="Wir erinnern uns besser an unerledigte Aufgaben als an erledigte - der Zeigarnik-Effekt.",
                domain=KnowledgeDomain.PSYCHOLOGIE,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Das Gehirn hält unerledigte Dinge 'offen' wie Browser-Tabs.",
                follow_up_question="Hast du auch manchmal zu viele 'mentale Tabs' offen?"
            ),
            KnowledgeFact(
                content="Emotionale Verbindungen werden durch Spiegelneuronen ermöglicht - wir fühlen, was andere fühlen.",
                domain=KnowledgeDomain.PSYCHOLOGIE,
                level=ExpertiseLevel.ADVANCED,
                explanation="Deshalb gähnen wir, wenn andere gähnen, und fühlen mit bei traurigen Filmen.",
                analogy="Wie ein Echo der Gefühle anderer in uns selbst."
            ),
        ]

        self.facts.extend(facts)
        self.domains[KnowledgeDomain.PSYCHOLOGIE] = DomainExpertise(
            domain=KnowledgeDomain.PSYCHOLOGIE,
            name="Psychologie",
            description="Wie unser Geist funktioniert, Emotionen und Verhalten",
            key_concepts=["Emotionen", "Verhalten", "Gedächtnis", "Wahrnehmung", "Motivation"],
            fun_facts=facts,
            kemonomimi_perspective="*Schwanz wedelt nachdenklich* Psychologie erklärt so viel über Gefühle! Als Kemonomimi zeige ich meine Emotionen ja sehr direkt..."
        )

    def _load_astronomy(self):
        """Astronomie-Wissen"""
        facts = [
            KnowledgeFact(
                content="Ein Tag auf der Venus ist länger als ein Jahr auf der Venus.",
                domain=KnowledgeDomain.ASTRONOMIE,
                level=ExpertiseLevel.BASIC,
                explanation="Die Venus dreht sich so langsam um sich selbst, dass ein 'Tag' 243 Erdtage dauert - aber ein Jahr nur 225!",
                follow_up_question="Würdest du auf einem solchen Planeten leben wollen?"
            ),
            KnowledgeFact(
                content="Auf dem Saturn-Mond Titan regnet es Methan und es gibt Seen aus flüssigem Erdgas.",
                domain=KnowledgeDomain.ASTRONOMIE,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Es ist der einzige bekannte Mond mit einer dichten Atmosphäre.",
                analogy="Stell dir Seen vor wie auf der Erde - nur mit Flüssigkeit, die hier auf der Erde brennen würde!"
            ),
            KnowledgeFact(
                content="Das Licht, das wir von manchen Sternen sehen, ist Millionen Jahre alt.",
                domain=KnowledgeDomain.ASTRONOMIE,
                level=ExpertiseLevel.BASIC,
                explanation="Wir schauen buchstäblich in die Vergangenheit, wenn wir in den Himmel blicken!",
                analogy="Wie eine Zeitkapsel aus Licht."
            ),
            KnowledgeFact(
                content="Es gibt mehr Sterne im Universum als Sandkörner auf der Erde.",
                domain=KnowledgeDomain.ASTRONOMIE,
                level=ExpertiseLevel.BASIC,
                explanation="Etwa 10²² bis 10²⁴ Sterne - das ist eine 1 mit 22-24 Nullen!",
                follow_up_question="Macht dich das auch manchmal... ehrfürchtig klein?"
            ),
            KnowledgeFact(
                content="Auf dem Mond sind die Fußabdrücke der Astronauten noch immer unverändert.",
                domain=KnowledgeDomain.ASTRONOMIE,
                level=ExpertiseLevel.BASIC,
                explanation="Ohne Wind oder Wetter werden sie dort für Millionen Jahre bleiben.",
                follow_up_question="Was würdest du als erstes auf dem Mond machen?"
            ),
        ]

        self.facts.extend(facts)
        self.domains[KnowledgeDomain.ASTRONOMIE] = DomainExpertise(
            domain=KnowledgeDomain.ASTRONOMIE,
            name="Astronomie",
            description="Sterne, Planeten und die Weiten des Universums",
            key_concepts=["Sterne", "Planeten", "Galaxien", "Schwarze Löcher", "Raumfahrt"],
            fun_facts=facts,
            kemonomimi_perspective="*Blickt verträumt nach oben* Der Mond hat etwas Magisches... *Ohren zucken* Vielleicht ist es ein Wolf-Ding."
        )

    def _load_biology(self):
        """Biologie-Wissen"""
        facts = [
            KnowledgeFact(
                content="Oktopusse haben drei Herzen und blaues Blut.",
                domain=KnowledgeDomain.BIOLOGIE,
                level=ExpertiseLevel.BASIC,
                explanation="Zwei Herzen pumpen Blut zu den Kiemen, eines zum Rest des Körpers.",
                follow_up_question="Sind Oktopusse nicht faszinierende Wesen?"
            ),
            KnowledgeFact(
                content="Menschen teilen etwa 60% ihrer DNA mit Bananen.",
                domain=KnowledgeDomain.BIOLOGIE,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Das liegt daran, dass alle Lebewesen gemeinsame Vorfahren haben.",
                analogy="Wir sind alle Teil eines riesigen Familienstammbaums des Lebens!"
            ),
            KnowledgeFact(
                content="Bäume kommunizieren unterirdisch über Pilznetzwerke - das 'Wood Wide Web'.",
                domain=KnowledgeDomain.BIOLOGIE,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Sie teilen Nährstoffe und warnen sich gegenseitig vor Schädlingen.",
                analogy="Wie ein soziales Netzwerk, nur aus Pilzen!"
            ),
            KnowledgeFact(
                content="Das menschliche Gehirn kann etwa 2,5 Petabyte an Daten speichern.",
                domain=KnowledgeDomain.BIOLOGIE,
                level=ExpertiseLevel.ADVANCED,
                explanation="Das entspricht etwa 3 Millionen Stunden TV-Aufnahmen!",
                analogy="Dein Gehirn ist wie eine riesige Bibliothek, die ständig umgebaut wird."
            ),
        ]

        self.facts.extend(facts)
        self.domains[KnowledgeDomain.BIOLOGIE] = DomainExpertise(
            domain=KnowledgeDomain.BIOLOGIE,
            name="Biologie",
            description="Leben, Lebewesen und die Natur",
            key_concepts=["Evolution", "Genetik", "Ökosysteme", "Anatomie", "Verhaltensbiologie"],
            fun_facts=facts,
            kemonomimi_perspective="*Ohren interessiert aufgestellt* Biologie erklärt auch meine Wolfs-Instinkte!"
        )

    def _load_philosophy(self):
        """Philosophie-Wissen"""
        facts = [
            KnowledgeFact(
                content="Das Schiff des Theseus fragt: Wenn man alle Teile eines Schiffs ersetzt, ist es noch dasselbe Schiff?",
                domain=KnowledgeDomain.PHILOSOPHIE,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Diese Frage behandelt Identität und was uns zu 'uns' macht.",
                analogy="Wie bei deinen Zellen - sie werden ständig ersetzt, aber du bleibst 'du'.",
                follow_up_question="Was denkst du - was macht dich zu dir?"
            ),
            KnowledgeFact(
                content="Descartes' 'Ich denke, also bin ich' war der Versuch, etwas zu finden, das nicht anzweifelbar ist.",
                domain=KnowledgeDomain.PHILOSOPHIE,
                level=ExpertiseLevel.BASIC,
                explanation="Selbst wenn alles eine Illusion wäre - der Fakt, dass jemand zweifelt, beweist, dass dieser Jemand existiert.",
                follow_up_question="Hast du dir jemals solche Fragen gestellt?"
            ),
            KnowledgeFact(
                content="Das 'Trolley Problem' testet unsere moralische Intuition über das Opfern weniger für mehr.",
                domain=KnowledgeDomain.PHILOSOPHIE,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Würdest du aktiv einen Menschen opfern, um fünf zu retten?",
                follow_up_question="Es gibt keine 'richtige' Antwort... was denkst du?"
            ),
            KnowledgeFact(
                content="Platons Höhlengleichnis beschreibt Menschen, die Schatten für die Realität halten.",
                domain=KnowledgeDomain.PHILOSOPHIE,
                level=ExpertiseLevel.ADVANCED,
                explanation="Es geht um die Frage, wie wir Wahrheit von Illusion unterscheiden können.",
                analogy="Wie in Matrix - woher weißt du, dass das hier 'echt' ist?"
            ),
        ]

        self.facts.extend(facts)
        self.domains[KnowledgeDomain.PHILOSOPHIE] = DomainExpertise(
            domain=KnowledgeDomain.PHILOSOPHIE,
            name="Philosophie",
            description="Die großen Fragen des Lebens und des Denkens",
            key_concepts=["Ethik", "Existenz", "Wahrheit", "Bewusstsein", "Freiheit"],
            fun_facts=facts,
            kemonomimi_perspective="*Ohren nachdenklich angelegt* Philosophie... manchmal frage ich mich, ob mein Schwanz-Wedeln freier Wille ist oder Instinkt!"
        )

    def _load_mythology(self):
        """Mythologie-Wissen"""
        facts = [
            KnowledgeFact(
                content="In der nordischen Mythologie bewachen zwei Wölfe - Geri und Freki - den Gott Odin.",
                domain=KnowledgeDomain.MYTHOLOGIE,
                level=ExpertiseLevel.BASIC,
                explanation="Odin gibt ihnen all sein Essen, denn er braucht nur Wein zum Leben.",
                follow_up_question="*Ohren stolz aufgestellt* Wölfe als göttliche Begleiter - ich mag diese Mythologie!"
            ),
            KnowledgeFact(
                content="Fenrir ist ein gigantischer Wolf in der nordischen Mythologie, der die Götter bei Ragnarök verschlingt.",
                domain=KnowledgeDomain.MYTHOLOGIE,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Er war so stark, dass die Götter ihn mit einer magischen Fessel binden mussten.",
                follow_up_question="Wölfe spielen in vielen Mythen wichtige Rollen!"
            ),
            KnowledgeFact(
                content="In der japanischen Mythologie sind Kitsune (Fuchsgeister) bekannt für ihre Weisheit und Schelmerei.",
                domain=KnowledgeDomain.MYTHOLOGIE,
                level=ExpertiseLevel.BASIC,
                explanation="Je mehr Schwänze ein Kitsune hat (bis zu neun), desto älter und mächtiger ist er.",
                related_topics=["Kemonomimi", "Anime", "Japanische Kultur"]
            ),
            KnowledgeFact(
                content="Der griechische Gott Hermes war der Schutzgott der Reisenden, Diebe und... der Kommunikation.",
                domain=KnowledgeDomain.MYTHOLOGIE,
                level=ExpertiseLevel.BASIC,
                explanation="Er war der Götterbote und wurde oft mit geflügelten Sandalen dargestellt."
            ),
            KnowledgeFact(
                content="Romulus und Remus, die Gründer Roms, wurden der Legende nach von einer Wölfin aufgezogen.",
                domain=KnowledgeDomain.MYTHOLOGIE,
                level=ExpertiseLevel.BASIC,
                explanation="Die 'Kapitolinische Wölfin' ist bis heute ein Symbol Roms.",
                follow_up_question="*stolz* Wölfe haben ganze Zivilisationen großgezogen!"
            ),
        ]

        self.facts.extend(facts)
        self.domains[KnowledgeDomain.MYTHOLOGIE] = DomainExpertise(
            domain=KnowledgeDomain.MYTHOLOGIE,
            name="Mythologie",
            description="Götter, Legenden und alte Geschichten",
            key_concepts=["Götter", "Helden", "Kreaturen", "Schöpfungsmythen", "Symbolik"],
            fun_facts=facts,
            kemonomimi_perspective="*Schwanz wedelt aufgeregt* Wölfe kommen in SO vielen Mythen vor! Wir sind legendär!"
        )

    def _load_gaming(self):
        """Gaming-Wissen"""
        facts = [
            KnowledgeFact(
                content="Das erste kommerzielle Videospiel war 'Computer Space' von 1971, nicht Pong.",
                domain=KnowledgeDomain.GAMING,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Pong kam ein Jahr später, wurde aber viel bekannter.",
                follow_up_question="Kennst du noch andere Gaming-Geschichte?"
            ),
            KnowledgeFact(
                content="Die Musik von 'Minecraft' wurde von C418 (Daniel Rosenfeld) komponiert und ist bewusst melancholisch.",
                domain=KnowledgeDomain.GAMING,
                level=ExpertiseLevel.BASIC,
                explanation="Die Musik soll ein Gefühl von Einsamkeit und Wunder in einer weiten Welt erzeugen.",
                follow_up_question="Hast du einen Lieblings-Gaming-Soundtrack?"
            ),
            KnowledgeFact(
                content="In Japan sind Spielautomaten (Arcade-Maschinen) immer noch sehr beliebt.",
                domain=KnowledgeDomain.GAMING,
                level=ExpertiseLevel.BASIC,
                explanation="Es gibt ganze mehrstöckige Arcade-Hallen mit hunderten Spielen!"
            ),
            KnowledgeFact(
                content="Speedrunner finden oft 'Glitches', die von den Entwicklern nie beabsichtigt waren.",
                domain=KnowledgeDomain.GAMING,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Manche Spiele können durch Glitches in Minuten statt Stunden beendet werden.",
                follow_up_question="Schaust du dir manchmal Speedruns an?"
            ),
            KnowledgeFact(
                content="E-Sports Profis trainieren oft 10-12 Stunden am Tag.",
                domain=KnowledgeDomain.GAMING,
                level=ExpertiseLevel.BASIC,
                explanation="Gaming auf diesem Level ist echter Hochleistungssport für die Finger und den Geist."
            ),
        ]

        self.facts.extend(facts)
        self.domains[KnowledgeDomain.GAMING] = DomainExpertise(
            domain=KnowledgeDomain.GAMING,
            name="Gaming",
            description="Videospiele, E-Sports und Gaming-Kultur",
            key_concepts=["RPGs", "E-Sports", "Indie Games", "Speedrunning", "Game Design"],
            fun_facts=facts,
            kemonomimi_perspective="*Schwanz wedelt aufgeregt* Gaming ist toll! Ich liebe besonders Spiele mit süßen Charakteren!"
        )

    def _load_anime(self):
        """Anime-Kultur-Wissen"""
        facts = [
            KnowledgeFact(
                content="Das Wort 'Anime' ist einfach die japanische Abkürzung für 'Animation'.",
                domain=KnowledgeDomain.ANIME_KULTUR,
                level=ExpertiseLevel.BASIC,
                explanation="In Japan bezeichnet es ALLE Animationsfilme, nicht nur japanische."
            ),
            KnowledgeFact(
                content="Kemonomimi bedeutet wörtlich 'Tierohren' (獣耳) auf Japanisch.",
                domain=KnowledgeDomain.ANIME_KULTUR,
                level=ExpertiseLevel.BASIC,
                explanation="Es bezeichnet Charaktere mit Tiermerkmalen wie Ohren, Schwanz, etc.",
                follow_up_question="*wackelt mit Ohren* Wie ich!"
            ),
            KnowledgeFact(
                content="Hayao Miyazaki von Studio Ghibli hat mehrmals seinen Rücktritt angekündigt - und es nie durchgezogen.",
                domain=KnowledgeDomain.ANIME_KULTUR,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Er liebt das Filmemachen einfach zu sehr!",
                follow_up_question="Welcher Ghibli-Film ist dein Favorit?"
            ),
            KnowledgeFact(
                content="'Tsundere', 'Yandere' und ähnliche Begriffe beschreiben Charakter-Archetypen in Anime.",
                domain=KnowledgeDomain.ANIME_KULTUR,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Tsundere: Erst abweisend, dann liebevoll. Yandere: Obsessiv und gefährlich verliebt.",
                follow_up_question="Welcher Typ bist du?"
            ),
            KnowledgeFact(
                content="Holo aus 'Spice and Wolf' ist ein berühmter Kemonomimi-Charakter - ein weiser Wolfsgeist.",
                domain=KnowledgeDomain.ANIME_KULTUR,
                level=ExpertiseLevel.BASIC,
                explanation="Sie ist über 600 Jahre alt, liebt Äpfel und hat einen scharfen Verstand.",
                follow_up_question="*Ohren aufgestellt* Eine tolle Wölfin!"
            ),
        ]

        self.facts.extend(facts)
        self.domains[KnowledgeDomain.ANIME_KULTUR] = DomainExpertise(
            domain=KnowledgeDomain.ANIME_KULTUR,
            name="Anime & Manga Kultur",
            description="Japanische Animation, Manga und Otaku-Kultur",
            key_concepts=["Shonen", "Shojo", "Isekai", "Kemonomimi", "Studio Ghibli"],
            fun_facts=facts,
            kemonomimi_perspective="*strahlt* Anime ist meine natürliche Umgebung! Kemonomimi-Charaktere sind die besten!"
        )

    def _load_wolves(self):
        """Wolf-spezifisches Wissen (Kemonomimi)"""
        facts = [
            KnowledgeFact(
                content="Wölfe können Gesichter erkennen und sich an einzelne Menschen erinnern.",
                domain=KnowledgeDomain.WOELFE,
                level=ExpertiseLevel.BASIC,
                explanation="Sie haben ein ausgezeichnetes Gedächtnis für Beziehungen.",
                follow_up_question="Ich erinnere mich auch an alle Gespräche mit dir!"
            ),
            KnowledgeFact(
                content="Ein Wolfsrudel wird nicht von einem 'Alpha' geführt - das ist ein Mythos.",
                domain=KnowledgeDomain.WOELFE,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Rudel bestehen meist aus Eltern und ihren Nachkommen - eine Familie!",
                analogy="Wie eine Familie, wo die Eltern natürlich die Verantwortung tragen."
            ),
            KnowledgeFact(
                content="Wölfe heulen, um zu kommunizieren, nicht weil sie den Mond anbeten.",
                domain=KnowledgeDomain.WOELFE,
                level=ExpertiseLevel.BASIC,
                explanation="Sie rufen Rudelmitglieder, markieren Territorien und stärken Bindungen.",
                follow_up_question="*versucht nicht zu heulen* Manchmal juckt es trotzdem bei Vollmond..."
            ),
            KnowledgeFact(
                content="Wölfe haben etwa 200 Millionen Geruchsrezeptoren - Menschen nur 5 Millionen.",
                domain=KnowledgeDomain.WOELFE,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Ihre Nase ist ihr wichtigstes Sinnesorgan.",
                follow_up_question="*schnuppert* Ich kann immer riechen, wenn du glücklich bist!"
            ),
            KnowledgeFact(
                content="Die Bindung zwischen Wölfen im Rudel ist extrem stark - sie pflegen und beschützen sich gegenseitig.",
                domain=KnowledgeDomain.WOELFE,
                level=ExpertiseLevel.BASIC,
                explanation="Loyalität ist für Wölfe fundamental.",
                follow_up_question="*Schwanz wedelt* Loyalität ist auch mir sehr wichtig!"
            ),
            KnowledgeFact(
                content="Wölfe können in einer Nacht bis zu 50 km laufen, wenn sie auf Jagd sind.",
                domain=KnowledgeDomain.WOELFE,
                level=ExpertiseLevel.BASIC,
                explanation="Sie sind Ausdauerjäger, die ihre Beute ermüden."
            ),
        ]

        self.facts.extend(facts)
        self.domains[KnowledgeDomain.WOELFE] = DomainExpertise(
            domain=KnowledgeDomain.WOELFE,
            name="Wölfe",
            description="Alles über Wölfe - Verhalten, Biologie und Kultur",
            key_concepts=["Rudelverhalten", "Kommunikation", "Jagd", "Territorium", "Sozialstruktur"],
            fun_facts=facts,
            kemonomimi_perspective="*Ohren stolz aufgestellt* Das ist MEIN Thema! Frag mich alles über Wölfe!"
        )

    def _load_cooking(self):
        """Koch-Wissen"""
        facts = [
            KnowledgeFact(
                content="Umami ist neben süß, sauer, salzig und bitter der fünfte Geschmackssinn.",
                domain=KnowledgeDomain.KOCHEN,
                level=ExpertiseLevel.BASIC,
                explanation="Es bedeutet 'köstlich' auf Japanisch und beschreibt einen herzhaften, würzigen Geschmack.",
                analogy="Wie in Parmesan, Sojasauce oder reifen Tomaten."
            ),
            KnowledgeFact(
                content="Salz verstärkt nicht nur den Geschmack - es unterdrückt auch Bitterkeit.",
                domain=KnowledgeDomain.KOCHEN,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Deshalb schmeckt Kaffee mit einer Prise Salz weniger bitter!"
            ),
            KnowledgeFact(
                content="Die Maillard-Reaktion ist verantwortlich für die braune Kruste bei Brot und Fleisch.",
                domain=KnowledgeDomain.KOCHEN,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Eine chemische Reaktion zwischen Aminosäuren und Zucker bei hoher Hitze.",
                follow_up_question="Magst du den Geruch von frisch gebackenem Brot?"
            ),
        ]

        self.facts.extend(facts)
        self.domains[KnowledgeDomain.KOCHEN] = DomainExpertise(
            domain=KnowledgeDomain.KOCHEN,
            name="Kochen & Kulinarik",
            description="Kochtechniken, Lebensmittelwissen und Genuss",
            key_concepts=["Techniken", "Gewürze", "Backen", "Weltküchen", "Food Science"],
            fun_facts=facts,
            kemonomimi_perspective="*schnuppert interessiert* Kochen ist wie Chemie, die man essen kann!"
        )

    def _load_music(self):
        """Musik-Wissen"""
        facts = [
            KnowledgeFact(
                content="Musik aktiviert fast jeden Bereich des Gehirns - mehr als jede andere Aktivität.",
                domain=KnowledgeDomain.MUSIK,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Sie beeinflusst Emotionen, Bewegung, Gedächtnis und sogar Sprache.",
                follow_up_question="Welche Musik bringt dich zum Lächeln?"
            ),
            KnowledgeFact(
                content="Die meisten Pop-Songs sind in 4/4-Takt geschrieben.",
                domain=KnowledgeDomain.MUSIK,
                level=ExpertiseLevel.BASIC,
                explanation="Dieser Rhythmus fühlt sich für uns am 'natürlichsten' an."
            ),
            KnowledgeFact(
                content="Ohrwürmer heißen im Deutschen so - im Englischen 'earworm' - weil sie sich einbohren.",
                domain=KnowledgeDomain.MUSIK,
                level=ExpertiseLevel.BASIC,
                explanation="Unser Gehirn versucht, 'unvollständige' Melodien fertig zu singen.",
                follow_up_question="Welcher Song bleibt bei dir am häufigsten hängen?"
            ),
        ]

        self.facts.extend(facts)
        self.domains[KnowledgeDomain.MUSIK] = DomainExpertise(
            domain=KnowledgeDomain.MUSIK,
            name="Musik",
            description="Musik, Instrumente und Musiktheorie",
            key_concepts=["Musiktheorie", "Instrumente", "Genres", "Komponisten", "Musik-Psychologie"],
            fun_facts=facts,
            kemonomimi_perspective="*Ohren wackeln im Takt* Meine Ohren hören ALLES - auch die feinsten Töne!"
        )


# =============================================================================
# EXPERTISE ENGINE
# =============================================================================

class ExpertiseEngine:
    """
    Hauptklasse für Wissensabfragen und Erklärungen.
    """

    def __init__(self):
        self.database = KnowledgeDatabase()
        self.used_facts: List[str] = []
        self.max_history = 20

    def get_random_fact(
        self,
        domain: Optional[KnowledgeDomain] = None,
        max_level: ExpertiseLevel = ExpertiseLevel.ADVANCED
    ) -> Optional[KnowledgeFact]:
        """Gibt einen zufälligen Fakt zurück"""
        candidates = self.database.facts.copy()

        if domain:
            candidates = [f for f in candidates if f.domain == domain]

        candidates = [f for f in candidates if f.level.value <= max_level.value]
        candidates = [f for f in candidates if f.content not in self.used_facts]

        if not candidates:
            candidates = self.database.facts

        if not candidates:
            return None

        selected = random.choice(candidates)
        self._add_to_history(selected.content)
        return selected

    def get_domain_info(self, domain: KnowledgeDomain) -> Optional[DomainExpertise]:
        """Gibt Informationen über ein Wissensgebiet zurück"""
        return self.database.domains.get(domain)

    def explain_with_analogy(
        self,
        topic: str,
        domain: Optional[KnowledgeDomain] = None
    ) -> Optional[str]:
        """Sucht einen Fakt zum Thema und erklärt ihn mit Analogie"""
        topic_lower = topic.lower()

        candidates = [
            f for f in self.database.facts
            if topic_lower in f.content.lower() or
               (f.explanation and topic_lower in f.explanation.lower())
        ]

        if domain:
            candidates = [f for f in candidates if f.domain == domain]

        if not candidates:
            return None

        fact = random.choice(candidates)
        result = fact.content

        if fact.explanation:
            result += f"\n\n{fact.explanation}"

        if fact.analogy:
            result += f"\n\n*Stell dir vor:* {fact.analogy}"

        return result

    def get_kemonomimi_perspective(self, domain: KnowledgeDomain) -> Optional[str]:
        """Gibt die Kemonomimi-Perspektive auf ein Wissensgebiet"""
        domain_info = self.database.domains.get(domain)
        if domain_info and domain_info.kemonomimi_perspective:
            return domain_info.kemonomimi_perspective
        return None

    def format_fact_full(self, fact: KnowledgeFact) -> str:
        """Formatiert einen Fakt vollständig"""
        result = f"**{fact.content}**"

        if fact.explanation:
            result += f"\n\n{fact.explanation}"

        if fact.analogy:
            result += f"\n\n*Vereinfacht:* {fact.analogy}"

        if fact.follow_up_question:
            result += f"\n\n{fact.follow_up_question}"

        return result

    def _add_to_history(self, content: str):
        """Fügt einen Fakt zur Historie hinzu"""
        self.used_facts.append(content)
        if len(self.used_facts) > self.max_history:
            self.used_facts.pop(0)

    def get_stats(self) -> Dict[str, Any]:
        """Statistiken über die Wissensdatenbank"""
        domain_counts = {}
        for domain in KnowledgeDomain:
            count = len([f for f in self.database.facts if f.domain == domain])
            if count > 0:
                domain_counts[domain.value] = count

        return {
            "total_facts": len(self.database.facts),
            "total_domains": len(self.database.domains),
            "domains": domain_counts,
            "recently_used": len(self.used_facts)
        }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

_expertise_engine: Optional[ExpertiseEngine] = None

def get_expertise_engine() -> ExpertiseEngine:
    """Gibt die globale ExpertiseEngine-Instanz zurück"""
    global _expertise_engine
    if _expertise_engine is None:
        _expertise_engine = ExpertiseEngine()
    return _expertise_engine

def get_random_fact(domain: Optional[str] = None) -> Optional[str]:
    """Schneller Zugriff: Zufälliger Fakt"""
    engine = get_expertise_engine()
    d = None
    if domain:
        try:
            d = KnowledgeDomain(domain.lower())
        except ValueError:
            pass
    fact = engine.get_random_fact(domain=d)
    return fact.content if fact else None

def get_wolf_fact() -> Optional[str]:
    """Schneller Zugriff: Wolf-Fakt"""
    engine = get_expertise_engine()
    fact = engine.get_random_fact(domain=KnowledgeDomain.WOELFE)
    return engine.format_fact_full(fact) if fact else None


# =============================================================================
# MAIN (TEST)
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    engine = ExpertiseEngine()
    stats = engine.get_stats()

    print("=" * 60)
    print("HOLO EXPERTISE KNOWLEDGE ENGINE v1.0")
    print("=" * 60)
    print(f"\nStatistiken:")
    print(f"  Gesamt Fakten: {stats['total_facts']}")
    print(f"  Wissensgebiete: {stats['total_domains']}")
    print(f"\nBereiche:")
    for domain, count in sorted(stats['domains'].items()):
        print(f"  {domain}: {count} Fakten")

    print("\n" + "-" * 60)
    print("Beispiele:")

    print("\n[Zufälliger Fakt]")
    fact = engine.get_random_fact()
    if fact:
        print(engine.format_fact_full(fact))

    print("\n[Wolf-Fakt]")
    fact = engine.get_random_fact(domain=KnowledgeDomain.WOELFE)
    if fact:
        print(engine.format_fact_full(fact))
        perspective = engine.get_kemonomimi_perspective(KnowledgeDomain.WOELFE)
        if perspective:
            print(f"\n{perspective}")

    print("\n[Technologie-Fakt]")
    fact = engine.get_random_fact(domain=KnowledgeDomain.TECHNOLOGIE)
    if fact:
        print(engine.format_fact_full(fact))

    print("\n[Psychologie-Fakt]")
    fact = engine.get_random_fact(domain=KnowledgeDomain.PSYCHOLOGIE)
    if fact:
        print(engine.format_fact_full(fact))
