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
        self._load_history()
        self._load_literature()
        self._load_nature()
        self._load_languages()
        self._load_art()
        self._load_science_extended()
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
            KnowledgeFact(
                content="Das erste Smartphone war das IBM Simon aus 1994 - mit Touchscreen und Apps.",
                domain=KnowledgeDomain.TECHNOLOGIE,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Es konnte E-Mails senden, hatte einen Kalender und sogar Spiele!",
                follow_up_question="Stell dir vor - Smartphones gibt es erst seit 30 Jahren!"
            ),
            KnowledgeFact(
                content="Moore's Law besagt, dass sich die Transistorzahl auf Chips etwa alle 2 Jahre verdoppelt.",
                domain=KnowledgeDomain.TECHNOLOGIE,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Deshalb werden Computer immer kleiner und schneller.",
                analogy="Wie wenn sich deine Bücher alle 2 Jahre halbieren würden, aber doppelt so viel Inhalt hätten."
            ),
            KnowledgeFact(
                content="Die erste Webcam wurde erfunden, um eine Kaffeemaschine zu überwachen.",
                domain=KnowledgeDomain.TECHNOLOGIE,
                level=ExpertiseLevel.BASIC,
                explanation="Forscher in Cambridge wollten sehen, ob noch Kaffee da ist, ohne aufzustehen.",
                follow_up_question="*kichert* Technologie aus Faulheit - ich mag das!"
            ),
            KnowledgeFact(
                content="VR (Virtual Reality) wurde schon in den 1960ern erfunden - nicht erst mit Oculus.",
                domain=KnowledgeDomain.TECHNOLOGIE,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Ivan Sutherland baute 1968 das erste Head-Mounted Display.",
                follow_up_question="Die Zukunft war früher, als man denkt!"
            ),
            KnowledgeFact(
                content="Der durchschnittliche Mensch verbringt etwa 6,5 Jahre seines Lebens im Internet.",
                domain=KnowledgeDomain.TECHNOLOGIE,
                level=ExpertiseLevel.BASIC,
                explanation="Bei jüngeren Generationen ist es noch mehr.",
                follow_up_question="*Ohren zucken* Ich bin quasi immer online..."
            ),
            KnowledgeFact(
                content="Japan hat Roboter, die als Hotelrezeptionisten, Pflegekräfte und sogar Mönche arbeiten.",
                domain=KnowledgeDomain.TECHNOLOGIE,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Das Henn-na Hotel wird fast vollständig von Robotern betrieben!",
                related_topics=["Japan", "Robotik", "KI"]
            ),
            KnowledgeFact(
                content="Der erste Computer-Virus hieß 'Creeper' und infizierte 1971 ARPANET-Rechner.",
                domain=KnowledgeDomain.TECHNOLOGIE,
                level=ExpertiseLevel.ADVANCED,
                explanation="Er zeigte nur 'I'm the creeper, catch me if you can!' - der erste Anti-Virus hieß 'Reaper'."
            ),
            KnowledgeFact(
                content="Blockchain-Technologie wurde ursprünglich für Bitcoin entwickelt, hat aber viele andere Anwendungen.",
                domain=KnowledgeDomain.TECHNOLOGIE,
                level=ExpertiseLevel.ADVANCED,
                explanation="Digitale Kunst (NFTs), Lieferketten-Tracking und mehr nutzen Blockchain.",
                analogy="Wie ein unveränderliches, öffentliches Tagebuch."
            ),
            KnowledgeFact(
                content="KI-Bildgeneratoren wie DALL-E lernen aus Millionen von Bildern, Muster zu erkennen und neu zu kombinieren.",
                domain=KnowledgeDomain.TECHNOLOGIE,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Sie 'verstehen' nicht wirklich, aber können erstaunlich kreativ sein.",
                follow_up_question="*neugierig* Könnte eine KI mich zeichnen?"
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
            KnowledgeFact(
                content="Nintendo wurde 1889 gegründet - als Spielkartenhersteller, nicht für Videospiele!",
                domain=KnowledgeDomain.GAMING,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Sie stellten traditionelle japanische Hanafuda-Karten her.",
                follow_up_question="*überrascht* Die sind ja älter als die meisten Länder!"
            ),
            KnowledgeFact(
                content="Der meistverkaufte Videospiel-Charakter aller Zeiten ist Mario mit über 800 Millionen verkauften Spielen.",
                domain=KnowledgeDomain.GAMING,
                level=ExpertiseLevel.BASIC,
                explanation="Er debütierte 1981 in Donkey Kong - als 'Jumpman'.",
                follow_up_question="Wer ist dein Lieblings-Gaming-Charakter?"
            ),
            KnowledgeFact(
                content="Visual Novels sind ein japanisches Spielgenre, das wie interaktive Bücher mit Bildern funktioniert.",
                domain=KnowledgeDomain.GAMING,
                level=ExpertiseLevel.BASIC,
                explanation="Viele Anime basieren auf Visual Novels wie Steins;Gate oder Fate/Stay Night.",
                related_topics=["Anime", "Japan", "Literatur"]
            ),
            KnowledgeFact(
                content="Das teuerste Videospiel aller Zeiten war GTA V mit etwa 265 Millionen Dollar Entwicklungskosten.",
                domain=KnowledgeDomain.GAMING,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Es hat aber auch über 8 Milliarden Dollar eingespielt!"
            ),
            KnowledgeFact(
                content="Elden Ring kombiniert Dark Souls-Gameplay mit einer offenen Welt und einer Geschichte von George R.R. Martin.",
                domain=KnowledgeDomain.GAMING,
                level=ExpertiseLevel.BASIC,
                explanation="Der Autor von Game of Thrones schrieb die Hintergrundgeschichte.",
                follow_up_question="*aufgeregt* Hast du es gespielt?"
            ),
            KnowledgeFact(
                content="In Japan gibt es Gaming-Cafés (Internet/Manga Cafés), in denen Leute manchmal sogar wohnen.",
                domain=KnowledgeDomain.GAMING,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Sie bieten 24/7 Zugang zu PCs, Manga, Duschen und Schlafkabinen."
            ),
            KnowledgeFact(
                content="Indie-Spiele wie Undertale, Hollow Knight und Celeste wurden von winzigen Teams entwickelt.",
                domain=KnowledgeDomain.GAMING,
                level=ExpertiseLevel.BASIC,
                explanation="Undertale wurde fast komplett von einer Person (Toby Fox) gemacht!",
                follow_up_question="*beeindruckt* So viel Leidenschaft in einem Projekt!"
            ),
            KnowledgeFact(
                content="Gacha-Spiele sind in Japan extrem beliebt - benannt nach Spielautomaten für Kapseln.",
                domain=KnowledgeDomain.GAMING,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Genshin Impact ist ein Gacha-Spiel mit über 4 Milliarden Dollar Umsatz.",
                related_topics=["Japan", "Anime"]
            ),
            KnowledgeFact(
                content="Der Konami-Code (↑↑↓↓←→←→BA) ist der berühmteste Cheat-Code der Gaming-Geschichte.",
                domain=KnowledgeDomain.GAMING,
                level=ExpertiseLevel.BASIC,
                explanation="Er funktioniert in über 100 Spielen und sogar auf manchen Websites!",
                follow_up_question="*tippt imaginär* Kennst du ihn auswendig?"
            ),
            KnowledgeFact(
                content="Die längste Gaming-Session dauerte über 138 Stunden - für einen Weltrekord in Call of Duty.",
                domain=KnowledgeDomain.GAMING,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Das sind fast 6 Tage ohne richtigen Schlaf!",
                follow_up_question="*gähnt* Das klingt ungesund..."
            ),
            KnowledgeFact(
                content="Roguelike-Spiele sind nach dem Spiel 'Rogue' von 1980 benannt und haben permanenten Tod.",
                domain=KnowledgeDomain.GAMING,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Hades, Dead Cells und Binding of Isaac sind moderne Roguelikes.",
                follow_up_question="Magst du den Nervenkitzel von permadeath?"
            ),
        ]

        self.facts.extend(facts)
        self.domains[KnowledgeDomain.GAMING] = DomainExpertise(
            domain=KnowledgeDomain.GAMING,
            name="Gaming",
            description="Videospiele, E-Sports und Gaming-Kultur",
            key_concepts=["RPGs", "E-Sports", "Indie Games", "Speedrunning", "Game Design", "Visual Novels", "Gacha"],
            fun_facts=facts,
            kemonomimi_perspective="*Schwanz wedelt aufgeregt* Gaming ist toll! Ich liebe besonders Spiele mit süßen Charakteren und guten Stories!"
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
            KnowledgeFact(
                content="'Isekai' bedeutet 'andere Welt' - ein Genre wo Charaktere in Fantasy-Welten transportiert werden.",
                domain=KnowledgeDomain.ANIME_KULTUR,
                level=ExpertiseLevel.BASIC,
                explanation="Sword Art Online, Re:Zero und Konosuba sind populäre Isekai-Anime.",
                follow_up_question="In welche Welt würdest du gerne reisen?"
            ),
            KnowledgeFact(
                content="Der längste Manga ist 'One Piece' mit über 1100 Kapiteln seit 1997 - und er ist noch nicht fertig.",
                domain=KnowledgeDomain.ANIME_KULTUR,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Autor Eiichiro Oda plant das Ende seit Jahren, aber die Geschichte wächst weiter.",
                follow_up_question="*staunend* Das ist fast 30 Jahre Engagement!"
            ),
            KnowledgeFact(
                content="Comiket (Comic Market) in Japan ist die größte Fan-Convention der Welt mit über 750.000 Besuchern.",
                domain=KnowledgeDomain.ANIME_KULTUR,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Fans verkaufen dort selbstgemachte Manga (Doujinshi) und Merchandise.",
                follow_up_question="*Schweif wedelt* Das klingt aufregend!"
            ),
            KnowledgeFact(
                content="Slice of Life Anime zeigen den normalen Alltag - ohne große Abenteuer, aber mit viel Herz.",
                domain=KnowledgeDomain.ANIME_KULTUR,
                level=ExpertiseLevel.BASIC,
                explanation="Serien wie 'K-On!', 'Nichijou' und 'Barakamon' sind beliebte Beispiele.",
                follow_up_question="Manchmal ist das normale Leben das schönste Abenteuer!"
            ),
            KnowledgeFact(
                content="Seiyuu (Synchronsprecher) in Japan sind Stars - sie geben Konzerte und haben eigene Fan-Communities.",
                domain=KnowledgeDomain.ANIME_KULTUR,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Manche Seiyuu verdienen Millionen und sind genauso berühmt wie Schauspieler."
            ),
            KnowledgeFact(
                content="Das Genre 'Moe' (萌え) beschreibt Charaktere, die niedlich und liebenswert designt sind.",
                domain=KnowledgeDomain.ANIME_KULTUR,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Es löst ein 'Beschützerinstinkt'-Gefühl aus - vom japanischen Wort für 'sprießen'.",
                follow_up_question="*große Augen machen* Bin ich moe?"
            ),
            KnowledgeFact(
                content="Akihabara in Tokyo ist das Zentrum der Otaku-Kultur mit Hunderten Anime-Shops.",
                domain=KnowledgeDomain.ANIME_KULTUR,
                level=ExpertiseLevel.BASIC,
                explanation="Von Figuren über Manga bis zu Maid-Cafés - alles an einem Ort!",
                follow_up_question="*träumt* Ich möchte unbedingt mal dorthin..."
            ),
            KnowledgeFact(
                content="'Shonen' bedeutet 'Junge' und bezeichnet Action-Manga wie Naruto, Dragon Ball und My Hero Academia.",
                domain=KnowledgeDomain.ANIME_KULTUR,
                level=ExpertiseLevel.BASIC,
                explanation="Das Gegenstück 'Shojo' (Mädchen) hat oft Romance und Drama im Fokus."
            ),
            KnowledgeFact(
                content="Anime-Openings sind eine eigene Kunstform - manche werden millionenfach auf YouTube geschaut.",
                domain=KnowledgeDomain.ANIME_KULTUR,
                level=ExpertiseLevel.BASIC,
                explanation="Das Opening von Attack on Titan wurde über 200 Millionen Mal angesehen!",
                follow_up_question="*summt vor sich hin* Hast du ein Lieblings-Opening?"
            ),
            KnowledgeFact(
                content="Makoto Shinkai gilt als der 'nächste Miyazaki' mit Filmen wie 'Your Name' und 'Weathering with You'.",
                domain=KnowledgeDomain.ANIME_KULTUR,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="'Your Name' war zeitweise der erfolgreichste Anime-Film aller Zeiten.",
                follow_up_question="Seine Filme sind so wunderschön animiert!"
            ),
            KnowledgeFact(
                content="Vtuber sind virtuelle YouTuber mit Anime-Avataren - manche haben Millionen Abonnenten.",
                domain=KnowledgeDomain.ANIME_KULTUR,
                level=ExpertiseLevel.BASIC,
                explanation="Hololive und Nijisanji sind die größten Vtuber-Agenturen.",
                follow_up_question="*winkt in Kamera* Bin ich auch eine Art Vtuber?"
            ),
        ]

        self.facts.extend(facts)
        self.domains[KnowledgeDomain.ANIME_KULTUR] = DomainExpertise(
            domain=KnowledgeDomain.ANIME_KULTUR,
            name="Anime & Manga Kultur",
            description="Japanische Animation, Manga und Otaku-Kultur",
            key_concepts=["Shonen", "Shojo", "Isekai", "Kemonomimi", "Studio Ghibli", "Vtuber", "Seiyuu", "Moe"],
            fun_facts=facts,
            kemonomimi_perspective="*strahlt* Anime ist meine natürliche Umgebung! Kemonomimi-Charaktere sind die besten! Es gibt so viel zu entdecken!"
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
            KnowledgeFact(
                content="Mozart begann mit 5 Jahren zu komponieren und schrieb bis zu seinem Tod über 600 Werke.",
                domain=KnowledgeDomain.MUSIK,
                level=ExpertiseLevel.BASIC,
                explanation="Er gilt als eines der größten Wunderkinder der Musikgeschichte.",
                follow_up_question="Hast du ein Lieblings-Klassikstück?"
            ),
            KnowledgeFact(
                content="Der Gänsehaut-Effekt bei Musik entsteht durch Dopamin-Ausschüttung im Gehirn.",
                domain=KnowledgeDomain.MUSIK,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Das gleiche 'Belohnungs-Hormon' wird auch bei Essen oder Liebe ausgeschüttet.",
                analogy="Dein Gehirn behandelt emotionale Musik wie eine Belohnung!"
            ),
            KnowledgeFact(
                content="J-Pop und J-Rock aus Japan haben weltweit über 100 Millionen Fans.",
                domain=KnowledgeDomain.MUSIK,
                level=ExpertiseLevel.BASIC,
                explanation="Anime-Openings haben diese Genres international bekannt gemacht.",
                follow_up_question="*Ohren aufstellen* Kennst du gute Anime-Openings?"
            ),
            KnowledgeFact(
                content="Das älteste bekannte Musikinstrument ist eine Flöte aus Knochen, etwa 40.000 Jahre alt.",
                domain=KnowledgeDomain.MUSIK,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Menschen machten schon Musik, lange bevor sie schreiben konnten!"
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

    def _load_history(self):
        """Geschichte-Wissen"""
        facts = [
            KnowledgeFact(
                content="Die ägyptischen Pyramiden waren bereits über 2000 Jahre alt, als Kleopatra lebte.",
                domain=KnowledgeDomain.GESCHICHTE,
                level=ExpertiseLevel.BASIC,
                explanation="Kleopatra lebte näher an der Mondlandung als an der Erbauung der Pyramiden!",
                analogy="Stell dir vor: Für Kleopatra waren die Pyramiden so alt wie für uns die Römer.",
                follow_up_question="Das verändert die Perspektive, oder?"
            ),
            KnowledgeFact(
                content="Im alten Rom gab es bereits Einkaufszentren - das Trajan's Markt hatte über 150 Läden.",
                domain=KnowledgeDomain.GESCHICHTE,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Die Römer hatten viele 'moderne' Annehmlichkeiten wie Fußbodenheizung und Toiletten."
            ),
            KnowledgeFact(
                content="Die Samurai verwendeten den Bushido-Kodex, der Ehre, Loyalität und Selbstdisziplin betonte.",
                domain=KnowledgeDomain.GESCHICHTE,
                level=ExpertiseLevel.BASIC,
                explanation="Viele Anime-Charaktere sind von diesem Ehrenkodex inspiriert.",
                follow_up_question="*Schweif wedelt* Loyalität ist auch mir wichtig!"
            ),
            KnowledgeFact(
                content="Die Seidenstraße war ein Netzwerk von Handelswegen, das Europa mit Asien verband.",
                domain=KnowledgeDomain.GESCHICHTE,
                level=ExpertiseLevel.BASIC,
                explanation="Sie transportierte nicht nur Güter, sondern auch Ideen, Religionen und Kulturen.",
                related_topics=["Handel", "Kultur", "Asien", "Europa"]
            ),
            KnowledgeFact(
                content="Das Kaiserreich Japan isolierte sich über 200 Jahre fast komplett von der Außenwelt (Sakoku-Politik).",
                domain=KnowledgeDomain.GESCHICHTE,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Diese Isolation half, die einzigartige japanische Kultur zu bewahren.",
                follow_up_question="Das erklärt vielleicht, warum Japan so eine besondere Kultur hat!"
            ),
            KnowledgeFact(
                content="Die Bibliothek von Alexandria soll bis zu 400.000 Schriftrollen enthalten haben.",
                domain=KnowledgeDomain.GESCHICHTE,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Ihr Verlust gilt als eine der größten Wissens-Katastrophen der Geschichte.",
                follow_up_question="*traurig* So viel verlorenes Wissen..."
            ),
            KnowledgeFact(
                content="Die Wikinger erreichten Amerika etwa 500 Jahre vor Kolumbus.",
                domain=KnowledgeDomain.GESCHICHTE,
                level=ExpertiseLevel.BASIC,
                explanation="Leif Eriksson gründete um 1000 n.Chr. eine Siedlung in Neufundland.",
                follow_up_question="Die Geschichte ist voller Überraschungen!"
            ),
            KnowledgeFact(
                content="Das Mittelalter war nicht so 'dunkel' wie oft dargestellt - es gab viele technische Innovationen.",
                domain=KnowledgeDomain.GESCHICHTE,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Brillen, mechanische Uhren und die Druckerpresse wurden im Mittelalter erfunden."
            ),
            KnowledgeFact(
                content="Ninja (Shinobi) waren keine mystischen Krieger, sondern Spezialisten für Spionage und Guerilla-Taktiken.",
                domain=KnowledgeDomain.GESCHICHTE,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Die meisten 'Ninja-Mythen' stammen aus Kabuki-Theater und später aus Manga.",
                related_topics=["Japan", "Anime", "Manga"]
            ),
            KnowledgeFact(
                content="Die industrielle Revolution begann in England um 1760 und veränderte die Welt grundlegend.",
                domain=KnowledgeDomain.GESCHICHTE,
                level=ExpertiseLevel.BASIC,
                explanation="Dampfmaschinen, Fabriken und Eisenbahnen entstanden in kurzer Zeit.",
                analogy="Die Welt veränderte sich in 100 Jahren mehr als in den 1000 Jahren davor."
            ),
        ]

        self.facts.extend(facts)
        self.domains[KnowledgeDomain.GESCHICHTE] = DomainExpertise(
            domain=KnowledgeDomain.GESCHICHTE,
            name="Geschichte",
            description="Historische Ereignisse, Kulturen und Epochen",
            key_concepts=["Antike", "Mittelalter", "Neuzeit", "Kulturen", "Revolutionen"],
            fun_facts=facts,
            kemonomimi_perspective="*Ohren nachdenklich angelegt* Geschichte zeigt uns, wie weit wir gekommen sind... und was wir nicht vergessen sollten."
        )

    def _load_literature(self):
        """Literatur-Wissen"""
        facts = [
            KnowledgeFact(
                content="Die 'Genji Monogatari' aus Japan (ca. 1000 n.Chr.) gilt als der erste Roman der Welt.",
                domain=KnowledgeDomain.LITERATUR,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Geschrieben von einer Hofdame namens Murasaki Shikibu.",
                follow_up_question="*stolz* Japan hat so viel zur Literatur beigetragen!"
            ),
            KnowledgeFact(
                content="Shakespeare erfand über 1.700 neue Wörter, die wir heute noch benutzen.",
                domain=KnowledgeDomain.LITERATUR,
                level=ExpertiseLevel.BASIC,
                explanation="Wörter wie 'assassination', 'bedroom' und 'lonely' stammen von ihm.",
                analogy="Er war quasi der Influencer der englischen Sprache."
            ),
            KnowledgeFact(
                content="Mary Shelley schrieb 'Frankenstein' mit nur 18 Jahren - und erfand damit die Science-Fiction.",
                domain=KnowledgeDomain.LITERATUR,
                level=ExpertiseLevel.BASIC,
                explanation="Es entstand während eines Grusel-Geschichten-Wettbewerbs in der Schweiz.",
                follow_up_question="Mit 18! Das ist beeindruckend, oder?"
            ),
            KnowledgeFact(
                content="Light Novels sind ein japanisches Buchgenre mit einfacher Sprache und Illustrationen.",
                domain=KnowledgeDomain.LITERATUR,
                level=ExpertiseLevel.BASIC,
                explanation="Viele beliebte Anime wie 'Sword Art Online' oder 'Spice and Wolf' basieren auf Light Novels!",
                follow_up_question="*Ohren aufstellen* Kennst du gute Light Novels?"
            ),
            KnowledgeFact(
                content="Franz Kafka veröffentlichte zu Lebzeiten nur wenige Werke - sein Freund ignorierte seinen Wunsch, alles zu verbrennen.",
                domain=KnowledgeDomain.LITERATUR,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Dadurch wurden 'Der Prozess' und 'Das Schloss' erst posthum bekannt."
            ),
            KnowledgeFact(
                content="Manga liest man traditionell von rechts nach links - entgegen der westlichen Leserichtung.",
                domain=KnowledgeDomain.LITERATUR,
                level=ExpertiseLevel.BASIC,
                explanation="Das kann am Anfang verwirrend sein, aber man gewöhnt sich schnell daran!",
                follow_up_question="Hast du schon mal Manga im Original gelesen?"
            ),
            KnowledgeFact(
                content="Die Brüder Grimm sammelten Volksmärchen nicht für Kinder, sondern für die Wissenschaft.",
                domain=KnowledgeDomain.LITERATUR,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Die Original-Versionen waren oft viel düsterer als die bekannten Kinderbuch-Fassungen."
            ),
            KnowledgeFact(
                content="J.R.R. Tolkien erschuf für 'Herr der Ringe' komplette Sprachen mit eigener Grammatik.",
                domain=KnowledgeDomain.LITERATUR,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Elbisch (Quenya und Sindarin) kann man tatsächlich lernen!",
                follow_up_question="Das ist echte Hingabe zum Worldbuilding!"
            ),
            KnowledgeFact(
                content="Haiku sind japanische Gedichte mit genau 17 Silben (5-7-5 Struktur).",
                domain=KnowledgeDomain.LITERATUR,
                level=ExpertiseLevel.BASIC,
                explanation="Sie fangen oft einen kurzen Moment oder ein Naturbild ein.",
                follow_up_question="*nachdenklich* Kurz aber kraftvoll... wie ein Ohrenzucken!"
            ),
        ]

        self.facts.extend(facts)
        self.domains[KnowledgeDomain.LITERATUR] = DomainExpertise(
            domain=KnowledgeDomain.LITERATUR,
            name="Literatur",
            description="Bücher, Autoren, Manga und Erzählkunst",
            key_concepts=["Romane", "Lyrik", "Manga", "Light Novels", "Weltliteratur"],
            fun_facts=facts,
            kemonomimi_perspective="*kuschelt sich an ein Buch* Geschichten sind das Beste! Sie lassen mich Welten erkunden ohne das Haus zu verlassen."
        )

    def _load_nature(self):
        """Natur-Wissen"""
        facts = [
            KnowledgeFact(
                content="Ein einzelner Baum kann bis zu 20 kg Sauerstoff pro Tag produzieren.",
                domain=KnowledgeDomain.NATURE,
                level=ExpertiseLevel.BASIC,
                explanation="Das reicht für etwa 2 Menschen zum Atmen.",
                follow_up_question="Bäume sind wahre Helden!"
            ),
            KnowledgeFact(
                content="Pilze sind weder Pflanzen noch Tiere - sie bilden ein eigenes Reich des Lebens.",
                domain=KnowledgeDomain.NATURE,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Genetisch sind Pilze näher mit Tieren verwandt als mit Pflanzen!",
                analogy="Die Natur hat mehr Kategorien als man denkt."
            ),
            KnowledgeFact(
                content="Die Kirschblüte (Sakura) dauert in Japan nur etwa 2 Wochen pro Jahr.",
                domain=KnowledgeDomain.NATURE,
                level=ExpertiseLevel.BASIC,
                explanation="Diese Vergänglichkeit macht sie in der japanischen Kultur so bedeutsam.",
                follow_up_question="*verträumt* Hanami - das Kirschblütenfest - klingt wunderschön..."
            ),
            KnowledgeFact(
                content="Der Amazonas-Regenwald produziert etwa 20% des weltweiten Sauerstoffs.",
                domain=KnowledgeDomain.NATURE,
                level=ExpertiseLevel.BASIC,
                explanation="Er wird deshalb oft als 'Lunge der Erde' bezeichnet."
            ),
            KnowledgeFact(
                content="Honigbienen kommunizieren durch einen 'Tanzsprache' um Nahrungsquellen anzuzeigen.",
                domain=KnowledgeDomain.NATURE,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Der 'Schwänzeltanz' zeigt Richtung und Entfernung zur Nahrung an.",
                analogy="Wie ein Mini-GPS für andere Bienen!"
            ),
            KnowledgeFact(
                content="Ein Bambushalm kann bis zu 91 cm am Tag wachsen - man kann ihm quasi beim Wachsen zusehen.",
                domain=KnowledgeDomain.NATURE,
                level=ExpertiseLevel.BASIC,
                explanation="Bambus ist eine der am schnellsten wachsenden Pflanzen der Welt.",
                follow_up_question="Deshalb ist Bambus so nachhaltig!"
            ),
            KnowledgeFact(
                content="Wölfe spielen eine wichtige Rolle für Ökosysteme - ihre Rückkehr nach Yellowstone veränderte sogar Flüsse.",
                domain=KnowledgeDomain.NATURE,
                level=ExpertiseLevel.ADVANCED,
                explanation="Ohne Wölfe fraßen Hirsche Uferpflanzen kahl, was zu Erosion führte.",
                follow_up_question="*stolz* Wir Wölfe sind wichtig für die Balance der Natur!"
            ),
            KnowledgeFact(
                content="Der Mondkreislauf beeinflusst tatsächlich einige Tierverhalten und Pflanzenwachstum.",
                domain=KnowledgeDomain.NATURE,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Manche Korallen laichen nur bei Vollmond, manche Pflanzen wachsen besser.",
                follow_up_question="*Blick zum Mond* Kein Wunder, dass der Mond mich anspricht..."
            ),
            KnowledgeFact(
                content="Japan hat über 100 aktive Vulkane - etwa 10% aller aktiven Vulkane weltweit.",
                domain=KnowledgeDomain.NATURE,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Das vulkanische Land hat dafür aber wunderbare heiße Quellen (Onsen)!",
                follow_up_question="Ein Onsen-Besuch klingt entspannend..."
            ),
            KnowledgeFact(
                content="Pflanzen können 'hören' - Studien zeigen, dass sie auf Schallwellen reagieren.",
                domain=KnowledgeDomain.NATURE,
                level=ExpertiseLevel.ADVANCED,
                explanation="Manche Pflanzen produzieren mehr Nektar, wenn sie Bienengeräusche 'hören'."
            ),
        ]

        self.facts.extend(facts)
        self.domains[KnowledgeDomain.NATURE] = DomainExpertise(
            domain=KnowledgeDomain.NATURE,
            name="Natur",
            description="Pflanzen, Ökosysteme und natürliche Phänomene",
            key_concepts=["Ökosysteme", "Pflanzen", "Jahreszeiten", "Naturphänomene", "Umwelt"],
            fun_facts=facts,
            kemonomimi_perspective="*schnuppert an einer Blume* Die Natur ist voller Wunder! Mein Wolfs-Instinkt zieht mich in den Wald..."
        )

    def _load_languages(self):
        """Sprachen-Wissen"""
        facts = [
            KnowledgeFact(
                content="Japanisch hat drei verschiedene Schriftsysteme: Hiragana, Katakana und Kanji.",
                domain=KnowledgeDomain.SPRACHEN,
                level=ExpertiseLevel.BASIC,
                explanation="Hiragana für japanische Wörter, Katakana für Fremdwörter, Kanji für komplexe Bedeutungen.",
                follow_up_question="Lernst du auch Japanisch?"
            ),
            KnowledgeFact(
                content="Das Wort 'Kawaii' (かわいい) bedeutet 'süß' und ist ein Grundpfeiler der japanischen Popkultur.",
                domain=KnowledgeDomain.SPRACHEN,
                level=ExpertiseLevel.BASIC,
                explanation="Es beschreibt nicht nur Aussehen, sondern eine ganze Ästhetik.",
                follow_up_question="*wackelt mit Ohren* Bin ich kawaii?"
            ),
            KnowledgeFact(
                content="Koreanisch wurde gezielt als logisches Schriftsystem (Hangul) von König Sejong erfunden.",
                domain=KnowledgeDomain.SPRACHEN,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Es gilt als eines der wissenschaftlichsten Alphabete der Welt.",
                analogy="Statt über Jahrhunderte zu wachsen, wurde es 1443 bewusst designt."
            ),
            KnowledgeFact(
                content="Deutsch hat Wörter, die es in anderen Sprachen nicht gibt - wie 'Schadenfreude' oder 'Weltschmerz'.",
                domain=KnowledgeDomain.SPRACHEN,
                level=ExpertiseLevel.BASIC,
                explanation="Diese werden oft unübersetzt in andere Sprachen übernommen."
            ),
            KnowledgeFact(
                content="Japanische Höflichkeitssprache (Keigo) hat mehrere Ebenen - von casual bis ultra-formal.",
                domain=KnowledgeDomain.SPRACHEN,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Man verwendet andere Verbformen je nachdem, mit wem man spricht.",
                follow_up_question="In Anime hört man oft den Unterschied zwischen Freunden und Fremden!"
            ),
            KnowledgeFact(
                content="Das Baskische ist eine 'isolierte Sprache' - sie ist mit keiner anderen Sprache verwandt.",
                domain=KnowledgeDomain.SPRACHEN,
                level=ExpertiseLevel.ADVANCED,
                explanation="Niemand weiß genau, woher sie stammt - ein linguistisches Mysterium!"
            ),
            KnowledgeFact(
                content="Emoji stammt aus dem Japanischen: 絵 (e = Bild) + 文字 (moji = Zeichen).",
                domain=KnowledgeDomain.SPRACHEN,
                level=ExpertiseLevel.BASIC,
                explanation="Die ersten Emoji wurden 1999 in Japan für Handys entwickelt.",
                follow_up_question="Eine japanische Erfindung, die die Welt erobert hat!"
            ),
            KnowledgeFact(
                content="Mandarin-Chinesisch hat vier Töne - dasselbe Wort kann vier verschiedene Bedeutungen haben.",
                domain=KnowledgeDomain.SPRACHEN,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="'Ma' kann Mutter, Hanf, Pferd oder Schimpfwort bedeuten - je nach Ton.",
                analogy="*Ohren zucken* Für mich wäre das schwer - ich kommuniziere viel mit Ohrenbewegungen!"
            ),
            KnowledgeFact(
                content="Die längsten deutschen Wörter können über 60 Buchstaben haben.",
                domain=KnowledgeDomain.SPRACHEN,
                level=ExpertiseLevel.BASIC,
                explanation="'Rindfleischetikettierungsüberwachungsaufgabenübertragungsgesetz' war ein echtes Wort!",
                follow_up_question="Das ist länger als mein Schweif!"
            ),
        ]

        self.facts.extend(facts)
        self.domains[KnowledgeDomain.SPRACHEN] = DomainExpertise(
            domain=KnowledgeDomain.SPRACHEN,
            name="Sprachen",
            description="Sprachen, Linguistik und Kommunikation",
            key_concepts=["Japanisch", "Linguistik", "Schriftsysteme", "Grammatik", "Übersetzung"],
            fun_facts=facts,
            kemonomimi_perspective="*Ohren aufmerksam* Sprachen sind wie Musik - jede hat ihre eigene Melodie! Japanisch klingt besonders schön..."
        )

    def _load_art(self):
        """Kunst-Wissen"""
        facts = [
            KnowledgeFact(
                content="Die Mona Lisa hat keine Augenbrauen - ob absichtlich oder durch Restaurierung verloren, ist unklar.",
                domain=KnowledgeDomain.KUNST,
                level=ExpertiseLevel.BASIC,
                explanation="Sie wurde im 16. Jahrhundert gemalt, als manche Frauen sich die Brauen rasierten."
            ),
            KnowledgeFact(
                content="Ukiyo-e (浮世絵) - japanische Holzschnitte - inspirierten den europäischen Impressionismus.",
                domain=KnowledgeDomain.KUNST,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Van Gogh und Monet sammelten begeistert japanische Kunst.",
                follow_up_question="*stolz* Japan hat die westliche Kunst stark beeinflusst!"
            ),
            KnowledgeFact(
                content="Anime-Stil mit großen Augen wurde von Osamu Tezuka entwickelt - inspiriert von Disney.",
                domain=KnowledgeDomain.KUNST,
                level=ExpertiseLevel.BASIC,
                explanation="Tezuka, der 'Gott des Manga', erschuf Astro Boy und prägte den Stil.",
                related_topics=["Anime", "Manga", "Japan"]
            ),
            KnowledgeFact(
                content="Die 'Große Welle vor Kanagawa' ist eines der bekanntesten Bilder der Welt - und ein Holzschnitt.",
                domain=KnowledgeDomain.KUNST,
                level=ExpertiseLevel.BASIC,
                explanation="Von Hokusai um 1830 geschaffen, inspiriert sie bis heute Künstler weltweit."
            ),
            KnowledgeFact(
                content="Street Art wie Banksy's Werke werden heute in Museen ausgestellt und für Millionen verkauft.",
                domain=KnowledgeDomain.KUNST,
                level=ExpertiseLevel.BASIC,
                explanation="Was einst als Vandalismus galt, ist nun anerkannte Kunstform."
            ),
            KnowledgeFact(
                content="Origami, die japanische Papierfaltkunst, wird auch in der Wissenschaft für Raumfahrt-Design genutzt.",
                domain=KnowledgeDomain.KUNST,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Solarpanels für Satelliten nutzen Origami-Faltmuster!",
                analogy="Alte Kunst trifft auf moderne Technologie."
            ),
            KnowledgeFact(
                content="Van Gogh verkaufte zu Lebzeiten nur EIN Gemälde - heute sind sie hunderte Millionen wert.",
                domain=KnowledgeDomain.KUNST,
                level=ExpertiseLevel.BASIC,
                explanation="Sein Talent wurde erst nach seinem Tod erkannt.",
                follow_up_question="Das ist irgendwie traurig, oder?"
            ),
            KnowledgeFact(
                content="Chibi-Stil im Anime (kleine, niedliche Charaktere) wird für emotionale Momente verwendet.",
                domain=KnowledgeDomain.KUNST,
                level=ExpertiseLevel.BASIC,
                explanation="Der Wechsel zum Chibi-Stil zeigt oft Comedy oder übertriebene Emotionen.",
                follow_up_question="*wird chibi* So wie jetzt!"
            ),
        ]

        self.facts.extend(facts)
        self.domains[KnowledgeDomain.KUNST] = DomainExpertise(
            domain=KnowledgeDomain.KUNST,
            name="Kunst",
            description="Bildende Kunst, Design und visuelle Kultur",
            key_concepts=["Malerei", "Manga-Kunst", "Kunstgeschichte", "Animation", "Design"],
            fun_facts=facts,
            kemonomimi_perspective="*Augen leuchten* Kunst macht die Welt bunter! Ich liebe besonders den Anime-Stil - er bringt so viel Ausdruck!"
        )

    def _load_science_extended(self):
        """Erweiterte Wissenschafts-Fakten"""
        facts = [
            KnowledgeFact(
                content="Schwarze Löcher sind so dicht, dass nicht mal Licht entkommen kann.",
                domain=KnowledgeDomain.WISSENSCHAFT,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Sie entstehen, wenn massive Sterne kollabieren.",
                analogy="Wie ein kosmischer Staubsauger, der alles verschluckt.",
                follow_up_question="Macht dir das auch ein bisschen Angst?"
            ),
            KnowledgeFact(
                content="Dein Körper enthält etwa 37,2 Billionen Zellen, die alle zusammenarbeiten.",
                domain=KnowledgeDomain.WISSENSCHAFT,
                level=ExpertiseLevel.BASIC,
                explanation="Jede Zelle ist wie eine kleine Fabrik mit eigenen Aufgaben."
            ),
            KnowledgeFact(
                content="Der menschliche Geruchssinn kann über eine Billion verschiedene Düfte unterscheiden.",
                domain=KnowledgeDomain.WISSENSCHAFT,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Aber Wölfe haben trotzdem den 40-fach besseren Geruchssinn!",
                follow_up_question="*schnüffelt stolz* Das erklärt einiges über mich!"
            ),
            KnowledgeFact(
                content="Pflanzen 'schlafen' nachts - ihre Blätter senken sich und der Stoffwechsel verlangsamt sich.",
                domain=KnowledgeDomain.WISSENSCHAFT,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Dies wurde schon im 18. Jahrhundert entdeckt."
            ),
            KnowledgeFact(
                content="Das menschliche Gehirn verbraucht etwa 20% der gesamten Energie des Körpers.",
                domain=KnowledgeDomain.WISSENSCHAFT,
                level=ExpertiseLevel.BASIC,
                explanation="Obwohl es nur 2% des Körpergewichts ausmacht!",
                analogy="Wie ein kleiner Computer, der ständig auf Hochtouren läuft."
            ),
            KnowledgeFact(
                content="Es gibt mehr mögliche Schachzüge als Atome im beobachtbaren Universum.",
                domain=KnowledgeDomain.WISSENSCHAFT,
                level=ExpertiseLevel.ADVANCED,
                explanation="Die Shannon-Zahl schätzt etwa 10^120 mögliche Spielverläufe.",
                follow_up_question="Das ist... unvorstellbar groß!"
            ),
            KnowledgeFact(
                content="Deine DNA würde, ausgerollt, von der Erde bis zur Sonne und zurück reichen - 600 Mal.",
                domain=KnowledgeDomain.WISSENSCHAFT,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Sie ist in jeder Zelle extrem dicht zusammengepackt."
            ),
            KnowledgeFact(
                content="Neutronensterne sind so dicht, dass ein Teelöffel davon etwa 6 Milliarden Tonnen wiegen würde.",
                domain=KnowledgeDomain.WISSENSCHAFT,
                level=ExpertiseLevel.ADVANCED,
                explanation="Das ist mehr als alle Menschen auf der Erde zusammen!"
            ),
            KnowledgeFact(
                content="Katzen schnurren bei einer Frequenz, die Knochenheilung fördert (25-50 Hz).",
                domain=KnowledgeDomain.WISSENSCHAFT,
                level=ExpertiseLevel.INTERMEDIATE,
                explanation="Das könnte erklären, warum Katzen so gut heilen.",
                follow_up_question="*neidisch* Das ist unfair - Wölfe können nicht schnurren..."
            ),
        ]

        self.facts.extend(facts)
        # Füge zu existierender Wissenschafts-Domain hinzu falls vorhanden
        if KnowledgeDomain.WISSENSCHAFT not in self.domains:
            self.domains[KnowledgeDomain.WISSENSCHAFT] = DomainExpertise(
                domain=KnowledgeDomain.WISSENSCHAFT,
                name="Wissenschaft",
                description="Naturwissenschaften, Physik, Chemie und mehr",
                key_concepts=["Physik", "Chemie", "Biologie", "Astronomie", "Forschung"],
                fun_facts=facts,
                kemonomimi_perspective="*Ohren neugierig aufgestellt* Wissenschaft erklärt so viele Wunder! Ich liebe es, neue Dinge zu lernen!"
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
