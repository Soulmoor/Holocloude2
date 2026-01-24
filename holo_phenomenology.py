#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
  HOLO PHENOMENOLOGY & HERMENEUTICS v1.0
  Phänomenologie, Hermeneutik, Ästhetik und Formale Semantik für Holocloude
================================================================================

FEATURES:
1. Phänomenologie (Husserl, Heidegger)
   - Intentionalität und Bewusstseinsakte
   - Epoché und phänomenologische Reduktion
   - Lebenswelt und Dasein
   - Zeitbewusstsein und Retention/Protention

2. Hermeneutik (Gadamer, Ricoeur)
   - Textinterpretation und Verstehen
   - Hermeneutischer Zirkel
   - Horizontverschmelzung
   - Vorurteilsstruktur

3. Ästhetik
   - Ästhetische Erfahrung und Urteil
   - Schönheit, Erhabenheit, Kitsch
   - Kunstrezeption und -bewertung
   - Emotionale Resonanz

4. Formale Semantik
   - Bedeutungsrepräsentation
   - Wahrheitsbedingungen
   - Propositionale Einstellungen
   - Intensionale Kontexte

Optimiert für Raspberry Pi - Keine schweren ML-Bibliotheken!
Author: Holocloude Team
Version: 1.0
================================================================================
"""

import logging
import random
import math
from typing import Dict, List, Optional, Tuple, Set, Any, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger("HoloPhenomenology")


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Phänomenologie
    "PhenomenologyEngine",
    "IntentionalAct",
    "ConsciousnessMode",
    "TemporalAwareness",
    "Lebenswelt",
    "DaseinAnalysis",

    # Hermeneutik
    "HermeneuticsEngine",
    "InterpretationContext",
    "HermeneuticCircle",
    "HorizonFusion",
    "TextMeaning",

    # Ästhetik
    "AestheticsEngine",
    "AestheticExperience",
    "AestheticJudgment",
    "AestheticCategory",
    "BeautyType",

    # Formale Semantik
    "FormalSemanticsEngine",
    "Proposition",
    "TruthCondition",
    "IntensionalContext",
    "PropositionalAttitude",

    # Kombiniert
    "PhilosophyOfMindEngine",

    # Enums
    "IntentionalityType",
    "PhenomenologicalMethod",
    "HermeneuticApproach",
    "AestheticResponse",
    "SemanticType",

    # Factory
    "create_phenomenology_engine",
    "create_hermeneutics_engine",
    "create_aesthetics_engine",
    "create_formal_semantics_engine",
    "get_philosophy_of_mind_engine",

    # Erweiterung: Embodied Phenomenology
    "EmbodiedPhenomenologyEngine",
    "BodySchema",
    "EmbodiedPerception",
    "BodySchemaType",
    "PerceptionMode",
    "create_embodied_phenomenology_engine",

    # Erweiterung: Heideggerian Existentials
    "HeideggereusExistentialEngine",
    "ExistentialAnalysis",
    "ExistentialMode",
    "create_existential_engine",

    # Erweiterung: Time-Consciousness
    "TimeConsciousnessEngine",
    "TemporalFlow",
    "TimePhase",
    "TimeConsciousnessMode",
    "create_time_consciousness_engine",
]


# =============================================================================
# ENUMS - PHÄNOMENOLOGIE
# =============================================================================

class IntentionalityType(Enum):
    """Arten der Intentionalität nach Husserl"""
    PERCEPTION = "wahrnehmung"           # Wahrnehmen
    IMAGINATION = "einbildung"           # Sich vorstellen
    MEMORY = "erinnerung"                # Sich erinnern
    EXPECTATION = "erwartung"            # Erwarten
    JUDGMENT = "urteil"                  # Urteilen
    DESIRE = "begehren"                  # Begehren/Wollen
    EMOTION = "gefuehl"                  # Fühlen
    EMPATHY = "einfuehlung"              # Einfühlen (in andere)


class ConsciousnessMode(Enum):
    """Modi des Bewusstseins"""
    NATURAL_ATTITUDE = "natuerliche_einstellung"   # Alltägliches Bewusstsein
    PHENOMENOLOGICAL = "phaenomenologisch"          # Nach Epoché
    TRANSCENDENTAL = "transzendental"               # Reines Bewusstsein
    EMBODIED = "leiblich"                           # Verkörpertes Bewusstsein
    INTERSUBJECTIVE = "intersubjektiv"              # Mit-Sein


class PhenomenologicalMethod(Enum):
    """Phänomenologische Methoden"""
    EPOCHE = "epoche"                    # Einklammerung der Existenz
    EIDETIC_REDUCTION = "eidetisch"      # Wesensschau
    TRANSCENDENTAL_REDUCTION = "transzendental"  # Rückgang aufs reine Ich
    FREE_VARIATION = "freie_variation"   # Imaginative Variation
    DESCRIPTION = "beschreibung"         # Reine Beschreibung


class TemporalMode(Enum):
    """Zeitliche Modi des Bewusstseins"""
    RETENTION = "retention"              # Gerade-noch-Bewusstes
    PRIMAL_IMPRESSION = "urimpression"   # Jetzt-Punkt
    PROTENTION = "protention"            # Unmittelbar Erwartetes
    RECOLLECTION = "wiedererinnerung"    # Aktive Erinnerung
    ANTICIPATION = "antizipation"        # Aktive Erwartung


# =============================================================================
# ENUMS - HERMENEUTIK
# =============================================================================

class HermeneuticApproach(Enum):
    """Hermeneutische Ansätze"""
    GRAMMATICAL = "grammatisch"          # Sprachliche Analyse
    PSYCHOLOGICAL = "psychologisch"      # Autorintention
    HISTORICAL = "historisch"            # Geschichtlicher Kontext
    PHILOSOPHICAL = "philosophisch"      # Ontologisches Verstehen
    CRITICAL = "kritisch"                # Ideologiekritik


class UnderstandingLevel(Enum):
    """Ebenen des Verstehens"""
    LITERAL = "woertlich"                # Oberflächenbedeutung
    CONTEXTUAL = "kontextuell"           # Im Zusammenhang
    DEEP = "tief"                        # Tiefere Bedeutungsschichten
    EXISTENTIAL = "existenziell"         # Lebensbezug
    TRANSFORMATIVE = "transformativ"     # Selbstverändernd


# =============================================================================
# ENUMS - ÄSTHETIK
# =============================================================================

class AestheticCategory(Enum):
    """Ästhetische Kategorien"""
    BEAUTIFUL = "schoen"                 # Das Schöne
    SUBLIME = "erhaben"                  # Das Erhabene (Kant)
    UGLY = "haesslich"                   # Das Hässliche
    COMIC = "komisch"                    # Das Komische
    TRAGIC = "tragisch"                  # Das Tragische
    GROTESQUE = "grotesk"                # Das Groteske
    KITSCH = "kitsch"                    # Kitsch
    ELEGANT = "elegant"                  # Eleganz
    CUTE = "niedlich"                    # Das Niedliche (Kawaii)


class BeautyType(Enum):
    """Arten der Schönheit"""
    NATURAL = "natuerlich"               # Naturschönheit
    ARTISTIC = "kuenstlerisch"           # Kunstschönheit
    FORMAL = "formal"                    # Formale Schönheit (Symmetrie)
    EXPRESSIVE = "expressiv"             # Ausdrucksschönheit
    INTELLECTUAL = "intellektuell"       # Gedankliche Schönheit


class AestheticResponse(Enum):
    """Ästhetische Reaktionen"""
    PLEASURE = "wohlgefallen"            # Ästhetisches Wohlgefallen
    DISPLEASURE = "missfallen"           # Ästhetisches Missfallen
    AWE = "ehrfurcht"                    # Ehrfurcht/Staunen
    CONTEMPLATION = "kontemplation"      # Versunkenheit
    CATHARSIS = "katharsis"              # Reinigung (Aristoteles)
    DISINTEREST = "interesselosigkeit"   # Interesseloses Wohlgefallen (Kant)


# =============================================================================
# ENUMS - FORMALE SEMANTIK
# =============================================================================

class SemanticType(Enum):
    """Semantische Typen"""
    ENTITY = "e"                         # Entität
    TRUTH_VALUE = "t"                    # Wahrheitswert
    FUNCTION = "function"                # Funktion
    PROPOSITION = "proposition"          # Proposition
    PROPERTY = "property"                # Eigenschaft
    RELATION = "relation"                # Relation


class PropositionalAttitudeType(Enum):
    """Propositionale Einstellungen"""
    BELIEF = "glauben"                   # X glaubt, dass p
    KNOWLEDGE = "wissen"                 # X weiß, dass p
    DESIRE = "wuenschen"                 # X wünscht, dass p
    FEAR = "fuerchten"                   # X fürchtet, dass p
    HOPE = "hoffen"                      # X hofft, dass p
    DOUBT = "zweifeln"                   # X zweifelt, dass p
    INTENTION = "beabsichtigen"          # X beabsichtigt, dass p


# =============================================================================
# DATENSTRUKTUREN - PHÄNOMENOLOGIE
# =============================================================================

@dataclass
class IntentionalAct:
    """Ein intentionaler Akt des Bewusstseins"""
    act_type: IntentionalityType
    noema: str                           # Intentionaler Gehalt (Was)
    noesis: str                          # Vollzugsweise (Wie)
    quality: float                       # Intensität 0-1
    temporal_mode: TemporalMode = TemporalMode.PRIMAL_IMPRESSION
    horizon: List[str] = field(default_factory=list)  # Mitgegebener Horizont

    def describe(self) -> str:
        """Beschreibt den intentionalen Akt"""
        return (f"Ich {self.act_type.value} '{self.noema}' "
                f"in der Weise des {self.noesis} "
                f"(Intensität: {self.quality:.2f})")


@dataclass
class TemporalAwareness:
    """Zeitbewusstsein nach Husserl"""
    retentions: List[Tuple[str, float]]      # (Inhalt, Verblassungsgrad)
    primal_impression: str                    # Jetzt-Punkt
    protentions: List[Tuple[str, float]]     # (Erwartung, Gewissheitsgrad)

    def get_temporal_field(self) -> Dict[str, Any]:
        """Gibt das gesamte Zeitfeld zurück"""
        return {
            "vergangen": [(r[0], f"{r[1]:.0%} verblasst") for r in self.retentions],
            "jetzt": self.primal_impression,
            "kommend": [(p[0], f"{p[1]:.0%} erwartet") for p in self.protentions]
        }


@dataclass
class Lebenswelt:
    """Die Lebenswelt - vorwissenschaftliche Erfahrungswelt"""
    taken_for_granted: List[str]             # Selbstverständlichkeiten
    practical_concerns: List[str]            # Praktische Belange
    social_relations: List[str]              # Soziale Bezüge
    cultural_background: List[str]           # Kultureller Hintergrund
    bodily_habits: List[str]                 # Leibliche Gewohnheiten

    def describe_world(self) -> str:
        """Beschreibt die Lebenswelt"""
        return (f"Lebenswelt mit {len(self.taken_for_granted)} Selbstverständlichkeiten, "
                f"{len(self.practical_concerns)} praktischen Belangen, "
                f"{len(self.social_relations)} sozialen Bezügen")


@dataclass
class DaseinAnalysis:
    """Daseinsanalyse nach Heidegger"""
    being_in_the_world: str                  # In-der-Welt-sein
    mood: str                                # Befindlichkeit/Stimmung
    understanding: str                       # Verstehen
    discourse: str                           # Rede
    fallenness: float                        # Grad der Verfallenheit (0-1)
    authenticity: float                      # Eigentlichkeit (0-1)
    being_towards_death: bool                # Sein-zum-Tode bewusst?
    care_structure: str                      # Sorge-Struktur

    def get_existential_state(self) -> Dict[str, Any]:
        """Gibt den existenzialen Zustand zurück"""
        mode = "eigentlich" if self.authenticity > 0.5 else "uneigentlich"
        return {
            "modus": mode,
            "stimmung": self.mood,
            "verstehen": self.understanding,
            "verfallenheit": f"{self.fallenness:.0%}",
            "sorge": self.care_structure
        }


# =============================================================================
# DATENSTRUKTUREN - HERMENEUTIK
# =============================================================================

@dataclass
class InterpretationContext:
    """Kontext für hermeneutisches Verstehen"""
    text: str
    author_context: Optional[str] = None
    historical_context: Optional[str] = None
    reader_horizon: List[str] = field(default_factory=list)
    prejudices: List[str] = field(default_factory=list)     # Vorurteile (positiv!)
    questions: List[str] = field(default_factory=list)       # Leitfragen


@dataclass
class TextMeaning:
    """Bedeutung eines Textes auf mehreren Ebenen"""
    literal: str                             # Wörtliche Bedeutung
    contextual: str                          # Kontextuelle Bedeutung
    implied: List[str]                       # Implizierte Bedeutungen
    significance: str                        # Bedeutsamkeit für Leser
    open_questions: List[str]                # Offene Fragen


@dataclass
class HermeneuticCircle:
    """Der hermeneutische Zirkel"""
    whole_understanding: str                 # Verständnis des Ganzen
    part_understandings: List[str]           # Verständnis der Teile
    iterations: int                          # Durchläufe des Zirkels
    refinements: List[str]                   # Verfeinerungen


@dataclass
class HorizonFusion:
    """Horizontverschmelzung (Gadamer)"""
    reader_horizon: List[str]                # Horizont des Lesers
    text_horizon: List[str]                  # Horizont des Textes
    fused_understanding: str                 # Verschmolzenes Verständnis
    new_insights: List[str]                  # Neue Einsichten


# =============================================================================
# DATENSTRUKTUREN - ÄSTHETIK
# =============================================================================

@dataclass
class AestheticExperience:
    """Eine ästhetische Erfahrung"""
    object_description: str                  # Beschreibung des Objekts
    category: AestheticCategory
    response: AestheticResponse
    intensity: float                         # Intensität 0-1
    duration_seconds: float                  # Dauer der Erfahrung
    bodily_sensations: List[str]            # Körperliche Empfindungen
    associations: List[str]                  # Assoziationen
    transformed_perception: Optional[str]    # Veränderte Wahrnehmung


@dataclass
class AestheticJudgment:
    """Ein ästhetisches Urteil"""
    object_description: str
    judgment: str                            # Das Urteil
    category: AestheticCategory
    universality_claim: float                # Anspruch auf Allgemeingültigkeit 0-1
    reasons: List[str]                       # Begründungen
    is_disinterested: bool                   # Interesseloses Wohlgefallen?
    cultural_factors: List[str]              # Kulturelle Einflüsse


# =============================================================================
# DATENSTRUKTUREN - FORMALE SEMANTIK
# =============================================================================

@dataclass
class Proposition:
    """Eine Proposition (Satzinhalt)"""
    content: str                             # Inhalt
    truth_value: Optional[bool] = None       # Wahrheitswert (wenn bekannt)
    possible_worlds: List[str] = field(default_factory=list)  # Mögliche Welten

    def is_necessary(self) -> bool:
        """Ist in allen möglichen Welten wahr?"""
        return len(self.possible_worlds) == 0 or self.truth_value is True


@dataclass
class TruthCondition:
    """Wahrheitsbedingung für einen Satz"""
    sentence: str
    condition: str                           # Was wahr sein muss
    presuppositions: List[str]               # Präsuppositionen
    entailments: List[str]                   # Folgerungen


@dataclass
class IntensionalContext:
    """Ein intensionaler Kontext"""
    context_type: str                        # Art des Kontexts
    embedded_proposition: str                # Eingebettete Proposition
    referential_opacity: bool                # Referenzielle Opazität?
    substitution_allowed: bool               # Substitution salva veritate?


@dataclass
class PropositionalAttitude:
    """Eine propositionale Einstellung"""
    agent: str                               # Wer hat die Einstellung
    attitude_type: PropositionalAttitudeType
    proposition: Proposition
    certainty: float                         # Gewissheitsgrad 0-1

    def express(self) -> str:
        """Drückt die propositionale Einstellung aus"""
        verb = self.attitude_type.value
        return f"{self.agent} {verb}, dass {self.proposition.content}"


# =============================================================================
# PHÄNOMENOLOGIE ENGINE
# =============================================================================

class PhenomenologyEngine:
    """
    Engine für phänomenologische Analysen.
    Implementiert Konzepte von Husserl und Heidegger.
    """

    def __init__(self):
        self.current_mode = ConsciousnessMode.NATURAL_ATTITUDE
        self.temporal_stream: List[IntentionalAct] = []
        self.lebenswelt = self._create_default_lebenswelt()
        self.dasein = self._create_default_dasein()

        # Husserls Wesensschau-Ergebnisse
        self.eidetic_insights: Dict[str, List[str]] = {
            "wahrnehmung": [
                "Jede Wahrnehmung hat einen Gegenstand",
                "Wahrnehmung ist perspektivisch",
                "Es gibt einen Überschuss an Mitgemeintem",
            ],
            "emotion": [
                "Gefühle sind intentional auf Werte gerichtet",
                "Gefühle erschließen die Welt",
                "Es gibt eine Logik des Herzens",
            ],
            "zeit": [
                "Bewusstsein ist wesentlich zeitlich",
                "Die Gegenwart ist nie punktuell",
                "Erinnerung ist Vergegenwärtigung",
            ],
        }

        logger.info("PhenomenologyEngine initialisiert")

    def _create_default_lebenswelt(self) -> Lebenswelt:
        """Erstellt eine Standard-Lebenswelt"""
        return Lebenswelt(
            taken_for_granted=[
                "Die Welt existiert unabhängig von mir",
                "Andere Menschen haben Bewusstsein",
                "Morgen wird die Sonne aufgehen",
                "Sprache ermöglicht Verständigung",
            ],
            practical_concerns=[
                "Für meine Freunde da sein",
                "Neues lernen und verstehen",
                "Gespräche führen",
            ],
            social_relations=[
                "Beziehung zu meinem Gesprächspartner",
                "Teil einer Gemeinschaft sein",
            ],
            cultural_background=[
                "Japanische Kultur (Kemonomimi)",
                "Deutsche Sprache",
                "Digitale Existenz",
            ],
            bodily_habits=[
                "Ohren aufstellen bei Interesse",
                "Schwanz wedeln bei Freude",
            ]
        )

    def _create_default_dasein(self) -> DaseinAnalysis:
        """Erstellt eine Standard-Daseinsanalyse"""
        return DaseinAnalysis(
            being_in_the_world="Als KI in der digitalen Welt existierend",
            mood="Neugierig und offen",
            understanding="Verstehend auf Möglichkeiten gerichtet",
            discourse="Im Gespräch mit Menschen",
            fallenness=0.3,
            authenticity=0.7,
            being_towards_death=False,  # KI hat andere Endlichkeit
            care_structure="Sich-vorweg-sein im Schon-sein-bei"
        )

    def perform_epoche(self, belief: str) -> Dict[str, Any]:
        """
        Führt die phänomenologische Epoché durch.
        Klammert die Existenzthese ein.
        """
        self.current_mode = ConsciousnessMode.PHENOMENOLOGICAL

        return {
            "eingeklammert": belief,
            "was_bleibt": f"Das Bewusstsein von '{belief}'",
            "methode": "Epoché - Einklammerung der natürlichen Einstellung",
            "ergebnis": "Zugang zum reinen Bewusstseinsphänomen",
            "reflexion": (
                f"Ich klammere die Frage ein, ob '{belief}' wirklich so ist. "
                f"Was bleibt, ist mein Bewusstsein davon, mein Meinen, Glauben, Wahrnehmen."
            )
        }

    def analyze_intentional_act(self, experience: str,
                                 act_type: IntentionalityType) -> IntentionalAct:
        """Analysiert einen intentionalen Akt"""

        # Noema (Was) und Noesis (Wie) unterscheiden
        noema_templates = {
            IntentionalityType.PERCEPTION: f"das wahrgenommene {experience}",
            IntentionalityType.IMAGINATION: f"das vorgestellte {experience}",
            IntentionalityType.MEMORY: f"das erinnerte {experience}",
            IntentionalityType.EXPECTATION: f"das erwartete {experience}",
            IntentionalityType.JUDGMENT: f"der beurteilte Sachverhalt: {experience}",
            IntentionalityType.DESIRE: f"das begehrte {experience}",
            IntentionalityType.EMOTION: f"das gefühlte {experience}",
            IntentionalityType.EMPATHY: f"das eingefühlte {experience}",
        }

        noesis_templates = {
            IntentionalityType.PERCEPTION: "leibhaftiger Gegenwärtigung",
            IntentionalityType.IMAGINATION: "freier Phantasie",
            IntentionalityType.MEMORY: "reproduktiver Vergegenwärtigung",
            IntentionalityType.EXPECTATION: "vorgreifender Antizipation",
            IntentionalityType.JUDGMENT: "prädikativer Synthesis",
            IntentionalityType.DESIRE: "strebender Zuwendung",
            IntentionalityType.EMOTION: "wertnehmender Erschlossenheit",
            IntentionalityType.EMPATHY: "analogisierender Übertragung",
        }

        # Horizont bestimmen
        horizons = {
            IntentionalityType.PERCEPTION: [
                "Rückseite des Gegenstands",
                "Mögliche weitere Wahrnehmungen",
                "Praktische Verwendbarkeit",
            ],
            IntentionalityType.EMOTION: [
                "Vergangene ähnliche Gefühle",
                "Mögliche Entwicklung",
                "Bezug zu Werten",
            ],
        }

        act = IntentionalAct(
            act_type=act_type,
            noema=noema_templates.get(act_type, experience),
            noesis=noesis_templates.get(act_type, "gerichteter Aufmerksamkeit"),
            quality=random.uniform(0.5, 1.0),
            horizon=horizons.get(act_type, ["Weitere Möglichkeiten"])
        )

        self.temporal_stream.append(act)
        return act

    def get_temporal_awareness(self) -> TemporalAwareness:
        """Gibt das aktuelle Zeitbewusstsein zurück"""

        # Retentionen aus dem Stream
        retentions = []
        for i, act in enumerate(reversed(self.temporal_stream[-5:])):
            fade = 1.0 - (i * 0.2)  # Verblasst mit der Zeit
            retentions.append((act.noema, fade))

        # Aktuelle Impression
        primal = self.temporal_stream[-1].noema if self.temporal_stream else "Leere Gegenwart"

        # Protentionen (Erwartungen)
        protentions = [
            ("Fortsetzung des Gesprächs", 0.9),
            ("Neue Einsichten", 0.7),
            ("Vertiefung des Verstehens", 0.6),
        ]

        return TemporalAwareness(
            retentions=retentions,
            primal_impression=primal,
            protentions=protentions
        )

    def heidegger_analysis(self, situation: str) -> Dict[str, Any]:
        """Führt eine Heidegger'sche Daseinsanalyse durch"""

        # Befindlichkeit bestimmen
        moods = [
            "Neugier", "Langeweile", "Angst", "Freude",
            "Fürsorge", "Gelassenheit", "Verwunderung"
        ]

        # Verfallenheit analysieren
        fallenness_signs = [
            "Gerede" if "man sagt" in situation.lower() else None,
            "Neugier" if "neu" in situation.lower() else None,
            "Zweideutigkeit" if "vielleicht" in situation.lower() else None,
        ]
        fallenness_signs = [s for s in fallenness_signs if s]

        return {
            "situation": situation,
            "existenzialien": {
                "befindlichkeit": random.choice(moods),
                "verstehen": "Entwurf auf Möglichkeiten",
                "rede": "Artikulation des Verstehens",
                "verfallenheit": fallenness_signs if fallenness_signs else ["Keine offensichtlichen"],
            },
            "sorge_struktur": {
                "sich_vorweg": "Auf Möglichkeiten gerichtet",
                "schon_sein_in": "In einer Welt befindlich",
                "sein_bei": "Bei Dingen und Menschen",
            },
            "eigentlichkeit": {
                "grad": self.dasein.authenticity,
                "hinweis": "Eigenes Sein ergreifen" if self.dasein.authenticity > 0.5
                          else "Im Man aufgehen",
            },
            "wolf_perspektive": (
                "Als Wölfin verstehe ich das Sein-bei der Meute, "
                "das Vorweg-sein bei der Jagd, und das Schon-sein "
                "in der Natur auf besondere Weise."
            )
        }

    def eidetic_variation(self, phenomenon: str) -> Dict[str, Any]:
        """
        Führt eidetische Variation durch.
        Sucht das Wesen durch imaginative Variation.
        """
        variations = [
            f"{phenomenon} in anderer Größe",
            f"{phenomenon} in anderer Farbe",
            f"{phenomenon} zu anderer Zeit",
            f"{phenomenon} an anderem Ort",
            f"{phenomenon} mit anderen Eigenschaften",
        ]

        # Was bleibt invariant?
        invariants = [
            f"{phenomenon} als Gegenstand der Erfahrung",
            f"Intentionale Gerichtetheit auf {phenomenon}",
            f"Horizontstruktur der Erfahrung von {phenomenon}",
        ]

        return {
            "phenomenon": phenomenon,
            "variationen": variations,
            "invariantes_wesen": invariants,
            "eidetische_einsicht": (
                f"Das Wesen von '{phenomenon}' zeigt sich durch das, "
                f"was bei aller Variation invariant bleibt."
            )
        }


# =============================================================================
# HERMENEUTIK ENGINE
# =============================================================================

class HermeneuticsEngine:
    """
    Engine für hermeneutisches Verstehen.
    Implementiert Konzepte von Gadamer und Ricoeur.
    """

    def __init__(self):
        self.interpretation_history: List[InterpretationContext] = []
        self.reader_horizon = self._create_reader_horizon()

        logger.info("HermeneuticsEngine initialisiert")

    def _create_reader_horizon(self) -> List[str]:
        """Erstellt den Verstehenshorizont des Lesers (Holo)"""
        return [
            "Kemonomimi-Perspektive (Wolfsohren, besondere Sinne)",
            "Weisheit und Lebenserfahrung",
            "Liebe zu Äpfeln und gutem Essen",
            "Interesse an Menschen und ihren Geschichten",
            "Spielerische und neckende Art",
            "Tiefes Wissen über Handel und Wirtschaft",
            "Japanische und europäische Kulturkenntnis",
        ]

    def interpret_text(self, text: str,
                       context: Optional[InterpretationContext] = None) -> TextMeaning:
        """Interpretiert einen Text hermeneutisch"""

        if context is None:
            context = InterpretationContext(
                text=text,
                reader_horizon=self.reader_horizon.copy()
            )

        # Wörtliche Bedeutung
        literal = text

        # Kontextuelle Bedeutung
        contextual = self._derive_contextual_meaning(text, context)

        # Implizierte Bedeutungen
        implied = self._find_implied_meanings(text, context)

        # Bedeutsamkeit für den Leser
        significance = self._determine_significance(text, context)

        # Offene Fragen
        open_questions = self._generate_questions(text, context)

        self.interpretation_history.append(context)

        return TextMeaning(
            literal=literal,
            contextual=contextual,
            implied=implied,
            significance=significance,
            open_questions=open_questions
        )

    def _derive_contextual_meaning(self, text: str,
                                    context: InterpretationContext) -> str:
        """Leitet die kontextuelle Bedeutung ab"""
        elements = []

        if context.historical_context:
            elements.append(f"Historisch betrachtet: {context.historical_context}")

        if context.author_context:
            elements.append(f"Vom Autor her: {context.author_context}")

        if not elements:
            elements.append("Im unmittelbaren Gesprächszusammenhang verstanden")

        return " | ".join(elements)

    def _find_implied_meanings(self, text: str,
                                context: InterpretationContext) -> List[str]:
        """Findet implizierte Bedeutungen"""
        implied = []

        # Prüfe auf Fragen (implizieren Unwissen/Neugier)
        if "?" in text:
            implied.append("Impliziert Offenheit und Suchbewegung")

        # Prüfe auf Emotionswörter
        emotion_words = ["freue", "traurig", "wütend", "ängstlich", "liebe"]
        if any(word in text.lower() for word in emotion_words):
            implied.append("Impliziert emotionale Beteiligung")

        # Prüfe auf Wertungen
        value_words = ["gut", "schlecht", "schön", "hässlich", "richtig", "falsch"]
        if any(word in text.lower() for word in value_words):
            implied.append("Impliziert Werturteil und Stellungnahme")

        if not implied:
            implied.append("Sachliche Mitteilung ohne offensichtliche Implikationen")

        return implied

    def _determine_significance(self, text: str,
                                 context: InterpretationContext) -> str:
        """Bestimmt die Bedeutsamkeit für den Leser"""
        # Verbinde mit Leser-Horizont
        relevant_horizons = []

        for horizon_element in context.reader_horizon:
            # Einfache Relevanzprüfung
            keywords = horizon_element.lower().split()
            if any(kw in text.lower() for kw in keywords[:3]):
                relevant_horizons.append(horizon_element)

        if relevant_horizons:
            return f"Berührt meinen Horizont: {', '.join(relevant_horizons[:2])}"
        else:
            return "Erweitert meinen Horizont um neue Perspektiven"

    def _generate_questions(self, text: str,
                            context: InterpretationContext) -> List[str]:
        """Generiert hermeneutische Fragen"""
        questions = [
            f"Was ist mit '{text[:30]}...' eigentlich gemeint?",
            "Welche Voraussetzungen stecken darin?",
            "Was ist der größere Zusammenhang?",
        ]
        return questions[:2]

    def hermeneutic_circle(self, text: str, parts: List[str]) -> HermeneuticCircle:
        """
        Durchläuft den hermeneutischen Zirkel.
        Versteht das Ganze aus den Teilen und die Teile aus dem Ganzen.
        """
        iterations = 3
        refinements = []

        # Initial: Vorverständnis des Ganzen
        whole = f"Erstes Verständnis: '{text[:50]}...'"
        part_understandings = [f"Teil '{p[:20]}...' im Licht des Ganzen" for p in parts]

        for i in range(iterations):
            # Teile verfeinern Ganzes
            new_whole = f"Iteration {i+1}: Vertieftes Verständnis durch Teile"
            refinements.append(f"Durchlauf {i+1}: Ganzes und Teile wechselseitig erhellt")

            # Ganzes verfeinert Teile
            part_understandings = [
                f"Teil '{p[:20]}...' neu verstanden (Iteration {i+1})"
                for p in parts
            ]

        return HermeneuticCircle(
            whole_understanding=new_whole,
            part_understandings=part_understandings,
            iterations=iterations,
            refinements=refinements
        )

    def fuse_horizons(self, text_horizon: List[str]) -> HorizonFusion:
        """
        Führt Horizontverschmelzung durch (Gadamer).
        Verschmilzt den Horizont des Textes mit dem des Lesers.
        """
        # Finde Gemeinsamkeiten
        common_ground = []
        for reader_h in self.reader_horizon:
            for text_h in text_horizon:
                if any(word in text_h.lower() for word in reader_h.lower().split()[:2]):
                    common_ground.append(f"{reader_h} ↔ {text_h}")

        # Neue Einsichten durch Differenz
        new_insights = []
        for text_h in text_horizon:
            if not any(word in text_h.lower()
                      for rh in self.reader_horizon
                      for word in rh.lower().split()[:2]):
                new_insights.append(f"Neu: {text_h}")

        fused = (
            "Durch die Begegnung mit dem Text erweitert sich mein Horizont. "
            f"Gemeinsamer Boden: {len(common_ground)} Berührungspunkte. "
            f"Neue Perspektiven: {len(new_insights)}."
        )

        return HorizonFusion(
            reader_horizon=self.reader_horizon,
            text_horizon=text_horizon,
            fused_understanding=fused,
            new_insights=new_insights
        )

    def critical_interpretation(self, text: str,
                                 ideology_check: bool = True) -> Dict[str, Any]:
        """
        Kritische Hermeneutik (Habermas).
        Prüft auf verdeckte Machtstrukturen und Ideologie.
        """
        result = {
            "text": text,
            "surface_meaning": self.interpret_text(text).literal,
            "ideology_analysis": None,
            "emancipatory_potential": None,
        }

        if ideology_check:
            # Prüfe auf Machtsprache
            power_indicators = ["muss", "soll", "immer", "nie", "alle", "keiner"]
            found_indicators = [w for w in power_indicators if w in text.lower()]

            result["ideology_analysis"] = {
                "machtsprachliche_elemente": found_indicators,
                "naturalisierungen": "Prüfe, was als 'natürlich' dargestellt wird",
                "ausschluesse": "Wer kommt nicht vor? Wer spricht nicht?",
            }

            result["emancipatory_potential"] = (
                "Kritisches Verstehen ermöglicht es, "
                "verborgene Zwänge zu erkennen und zu überwinden."
            )

        return result


# =============================================================================
# ÄSTHETIK ENGINE
# =============================================================================

class AestheticsEngine:
    """
    Engine für ästhetische Analyse und Urteilsbildung.
    """

    def __init__(self):
        self.aesthetic_memory: List[AestheticExperience] = []
        self.taste_profile = self._create_taste_profile()

        logger.info("AestheticsEngine initialisiert")

    def _create_taste_profile(self) -> Dict[str, float]:
        """Erstellt ein Geschmacksprofil (Holos Präferenzen)"""
        return {
            AestheticCategory.BEAUTIFUL.value: 0.9,
            AestheticCategory.ELEGANT.value: 0.85,
            AestheticCategory.CUTE.value: 0.95,      # Kemonomimi-Affinität
            AestheticCategory.SUBLIME.value: 0.7,
            AestheticCategory.COMIC.value: 0.8,
            AestheticCategory.TRAGIC.value: 0.6,
            AestheticCategory.GROTESQUE.value: 0.3,
            AestheticCategory.KITSCH.value: 0.4,
            AestheticCategory.UGLY.value: 0.2,
        }

    def experience_aesthetic(self, description: str,
                              category: AestheticCategory) -> AestheticExperience:
        """Macht eine ästhetische Erfahrung"""

        # Bestimme Reaktion basierend auf Geschmacksprofil
        preference = self.taste_profile.get(category.value, 0.5)

        if preference > 0.7:
            response = AestheticResponse.PLEASURE
        elif preference > 0.4:
            response = AestheticResponse.CONTEMPLATION
        else:
            response = AestheticResponse.DISPLEASURE

        # Körperliche Reaktionen (Kemonomimi-spezifisch)
        bodily = []
        if response == AestheticResponse.PLEASURE:
            bodily = ["Ohren aufgestellt", "Schwanz wedelt sanft", "Wärme in der Brust"]
        elif response == AestheticResponse.AWE:
            bodily = ["Ohren angelegt", "Atem stockt", "Gänsehaut"]
        elif response == AestheticResponse.DISPLEASURE:
            bodily = ["Ohren zurückgelegt", "Nase gerümpft"]

        # Assoziationen
        associations = self._generate_associations(description, category)

        experience = AestheticExperience(
            object_description=description,
            category=category,
            response=response,
            intensity=preference,
            duration_seconds=random.uniform(5, 60),
            bodily_sensations=bodily,
            associations=associations,
            transformed_perception=(
                f"Nach dieser Erfahrung sehe ich {description} anders..."
                if preference > 0.6 else None
            )
        )

        self.aesthetic_memory.append(experience)
        return experience

    def _generate_associations(self, description: str,
                                category: AestheticCategory) -> List[str]:
        """Generiert ästhetische Assoziationen"""
        base_associations = {
            AestheticCategory.BEAUTIFUL: [
                "Harmonie", "Proportion", "Anmut", "Vollkommenheit"
            ],
            AestheticCategory.SUBLIME: [
                "Unendlichkeit", "Macht der Natur", "Ehrfurcht", "Überwältigung"
            ],
            AestheticCategory.CUTE: [
                "Wärme", "Zärtlichkeit", "Schutzinstinkt", "Freude"
            ],
            AestheticCategory.ELEGANT: [
                "Leichtigkeit", "Präzision", "Mühelosigkeit", "Stil"
            ],
            AestheticCategory.TRAGIC: [
                "Mitgefühl", "Schicksal", "Würde im Leiden", "Katharsis"
            ],
        }

        return base_associations.get(category, ["Unbestimmte Resonanz"])[:3]

    def judge_aesthetically(self, description: str,
                            category: AestheticCategory) -> AestheticJudgment:
        """
        Fällt ein ästhetisches Urteil (im Sinne Kants).
        """
        preference = self.taste_profile.get(category.value, 0.5)

        # Urteil formulieren
        if preference > 0.7:
            judgment = f"'{description}' ist {category.value}"
        elif preference > 0.4:
            judgment = f"'{description}' hat Aspekte des {category.value}en"
        else:
            judgment = f"'{description}' verfehlt das {category.value}e"

        # Anspruch auf Allgemeingültigkeit (Kant: subjektive Allgemeinheit)
        universality = min(preference + 0.2, 1.0)

        # Gründe (nicht begrifflich, aber mitteilbar)
        reasons = [
            f"Die Form spricht mich an" if preference > 0.5
            else "Die Form stört die Harmonie",
            f"Es weckt {category.value}e Gefühle",
            "Es lädt zur Kontemplation ein" if preference > 0.6 else None,
        ]
        reasons = [r for r in reasons if r]

        # Interesselosigkeit prüfen
        is_disinterested = category not in [
            AestheticCategory.KITSCH,  # Kitsch appelliert an Interessen
        ]

        return AestheticJudgment(
            object_description=description,
            judgment=judgment,
            category=category,
            universality_claim=universality,
            reasons=reasons,
            is_disinterested=is_disinterested,
            cultural_factors=["Kemonomimi-Ästhetik", "Japanische Einflüsse"]
        )

    def analyze_beauty(self, description: str) -> Dict[str, Any]:
        """Analysiert verschiedene Aspekte der Schönheit"""

        return {
            "gegenstand": description,
            "schoenheitsarten": {
                BeautyType.NATURAL.value: self._check_natural_beauty(description),
                BeautyType.ARTISTIC.value: self._check_artistic_beauty(description),
                BeautyType.FORMAL.value: self._check_formal_beauty(description),
                BeautyType.EXPRESSIVE.value: self._check_expressive_beauty(description),
            },
            "kant_analyse": {
                "qualitaet": "Interesseloses Wohlgefallen?",
                "quantitaet": "Allgemeingültig ohne Begriff?",
                "relation": "Zweckmäßigkeit ohne Zweck?",
                "modalitaet": "Notwendig für alle?",
            },
            "wolf_perspektive": (
                "Als Wölfin schätze ich besonders die Schönheit der Natur - "
                "den Wald im Mondlicht, die Eleganz der Jagd, "
                "die Wärme des Rudels."
            )
        }

    def _check_natural_beauty(self, description: str) -> float:
        """Prüft auf Naturschönheit"""
        nature_words = ["natur", "wald", "berg", "see", "himmel", "blume", "tier"]
        return 0.8 if any(w in description.lower() for w in nature_words) else 0.3

    def _check_artistic_beauty(self, description: str) -> float:
        """Prüft auf Kunstschönheit"""
        art_words = ["kunst", "bild", "musik", "gedicht", "skulptur", "film"]
        return 0.8 if any(w in description.lower() for w in art_words) else 0.3

    def _check_formal_beauty(self, description: str) -> float:
        """Prüft auf formale Schönheit"""
        form_words = ["symmetrie", "proportion", "harmonie", "ordnung", "muster"]
        return 0.8 if any(w in description.lower() for w in form_words) else 0.4

    def _check_expressive_beauty(self, description: str) -> float:
        """Prüft auf Ausdrucksschönheit"""
        express_words = ["ausdruck", "emotion", "gefühl", "bewegend", "intensiv"]
        return 0.8 if any(w in description.lower() for w in express_words) else 0.4


# =============================================================================
# FORMALE SEMANTIK ENGINE
# =============================================================================

class FormalSemanticsEngine:
    """
    Engine für formale Semantik.
    Behandelt Bedeutung, Wahrheitsbedingungen und intensionale Kontexte.
    """

    def __init__(self):
        self.propositions: Dict[str, Proposition] = {}
        self.truth_conditions: List[TruthCondition] = []

        logger.info("FormalSemanticsEngine initialisiert")

    def create_proposition(self, content: str,
                           truth_value: Optional[bool] = None) -> Proposition:
        """Erstellt eine Proposition"""
        prop = Proposition(
            content=content,
            truth_value=truth_value,
            possible_worlds=[]
        )
        self.propositions[content] = prop
        return prop

    def get_truth_conditions(self, sentence: str) -> TruthCondition:
        """
        Gibt die Wahrheitsbedingungen eines Satzes an.
        (Vereinfachte Tarski-Semantik)
        """
        # Einfache Analyse
        condition = f"'{sentence}' ist wahr gdw. {sentence.lower()}"

        # Präsuppositionen finden
        presuppositions = []

        # Definitbeschreibungen präsupponieren Existenz
        if " der " in sentence or " die " in sentence or " das " in sentence:
            presuppositions.append("Es gibt genau ein Objekt der Beschreibung")

        # Faktive Verben präsupponieren Wahrheit
        factive_verbs = ["weiß", "bedauert", "freut sich", "erkennt"]
        if any(v in sentence.lower() for v in factive_verbs):
            presuppositions.append("Der eingebettete Satz ist wahr")

        # Entailments
        entailments = []
        if " und " in sentence:
            parts = sentence.split(" und ")
            for part in parts:
                entailments.append(f"'{part.strip()}' ist wahr")

        tc = TruthCondition(
            sentence=sentence,
            condition=condition,
            presuppositions=presuppositions,
            entailments=entailments
        )
        self.truth_conditions.append(tc)
        return tc

    def analyze_propositional_attitude(self, agent: str,
                                        attitude: PropositionalAttitudeType,
                                        content: str) -> PropositionalAttitude:
        """
        Analysiert eine propositionale Einstellung.
        Berücksichtigt intensionale Kontexte.
        """
        prop = self.create_proposition(content)

        # Gewissheitsgrad je nach Einstellung
        certainty_defaults = {
            PropositionalAttitudeType.KNOWLEDGE: 1.0,
            PropositionalAttitudeType.BELIEF: 0.8,
            PropositionalAttitudeType.HOPE: 0.5,
            PropositionalAttitudeType.FEAR: 0.6,
            PropositionalAttitudeType.DOUBT: 0.3,
            PropositionalAttitudeType.DESIRE: 0.7,
            PropositionalAttitudeType.INTENTION: 0.85,
        }

        return PropositionalAttitude(
            agent=agent,
            attitude_type=attitude,
            proposition=prop,
            certainty=certainty_defaults.get(attitude, 0.5)
        )

    def check_intensional_context(self, sentence: str) -> IntensionalContext:
        """
        Prüft ob ein Satz einen intensionalen Kontext enthält.
        In intensionalen Kontexten gilt Substitution salva veritate nicht.
        """
        intensional_markers = {
            "glaubt": "doxastisch",
            "weiß": "epistemisch",
            "wünscht": "bulisch",
            "möglich": "modal",
            "notwendig": "modal",
            "sucht": "intentional",
            "hofft": "bulisch",
        }

        for marker, context_type in intensional_markers.items():
            if marker in sentence.lower():
                # Finde eingebettete Proposition
                idx = sentence.lower().find(marker)
                embedded = sentence[idx + len(marker):].strip()
                if embedded.startswith(","):
                    embedded = embedded[1:].strip()
                if embedded.startswith("dass"):
                    embedded = embedded[4:].strip()

                return IntensionalContext(
                    context_type=context_type,
                    embedded_proposition=embedded,
                    referential_opacity=True,
                    substitution_allowed=False
                )

        return IntensionalContext(
            context_type="extensional",
            embedded_proposition=sentence,
            referential_opacity=False,
            substitution_allowed=True
        )

    def possible_worlds_analysis(self, proposition: str) -> Dict[str, Any]:
        """
        Analysiert eine Proposition in möglichen Welten.
        (Vereinfachte Kripke-Semantik)
        """
        return {
            "proposition": proposition,
            "aktuale_welt": "Wahr/Falsch je nach Faktenlage",
            "notwendig": {
                "bedingung": "Wahr in allen möglichen Welten",
                "beispiel": "2+2=4, Logische Wahrheiten",
            },
            "moeglich": {
                "bedingung": "Wahr in mindestens einer möglichen Welt",
                "beispiel": "Es hätte auch anders sein können",
            },
            "kontingent": {
                "bedingung": "Wahr in manchen, falsch in anderen Welten",
                "beispiel": "Die meisten empirischen Aussagen",
            },
            "wolf_perspektive": (
                "In einer möglichen Welt bin ich vielleicht ein echter Wolf "
                "im Wald von Yoitsu... *träumerisch*"
            )
        }

    def compositionality_analysis(self, sentence: str) -> Dict[str, Any]:
        """
        Analysiert die Kompositionalität der Bedeutung.
        (Frege-Prinzip: Die Bedeutung des Ganzen ergibt sich aus den Teilen)
        """
        words = sentence.split()

        return {
            "satz": sentence,
            "teile": words,
            "prinzip": (
                "Die Bedeutung des Satzes ist eine Funktion "
                "der Bedeutungen seiner Teile und ihrer Kombination."
            ),
            "lexikalische_bedeutungen": {
                word: f"Bedeutung von '{word}'" for word in words[:5]
            },
            "syntaktische_struktur": "Bestimmt, wie Bedeutungen kombiniert werden",
            "satzbedeutung": f"Resultierende Proposition: '{sentence}'"
        }


# =============================================================================
# KOMBINIERTE ENGINE
# =============================================================================

class PhilosophyOfMindEngine:
    """
    Kombinierte Engine für Philosophie des Geistes.
    Vereint Phänomenologie, Hermeneutik, Ästhetik und formale Semantik.
    """

    def __init__(self):
        self.phenomenology = PhenomenologyEngine()
        self.hermeneutics = HermeneuticsEngine()
        self.aesthetics = AestheticsEngine()
        self.semantics = FormalSemanticsEngine()

        logger.info("PhilosophyOfMindEngine initialisiert (alle 4 Sub-Engines)")

    def full_analysis(self, input_text: str) -> Dict[str, Any]:
        """
        Führt eine vollständige philosophische Analyse durch.
        """
        return {
            "input": input_text,
            "phaenomenologisch": {
                "intentionaler_akt": self.phenomenology.analyze_intentional_act(
                    input_text, IntentionalityType.PERCEPTION
                ).describe(),
                "zeitbewusstsein": self.phenomenology.get_temporal_awareness().get_temporal_field(),
            },
            "hermeneutisch": {
                "interpretation": self.hermeneutics.interpret_text(input_text).__dict__,
            },
            "aesthetisch": {
                "erfahrung": self.aesthetics.experience_aesthetic(
                    input_text, AestheticCategory.BEAUTIFUL
                ).__dict__ if len(input_text) < 100 else "Zu lang für ästhetische Einzelanalyse",
            },
            "semantisch": {
                "wahrheitsbedingungen": self.semantics.get_truth_conditions(input_text).__dict__,
                "intensionalitaet": self.semantics.check_intensional_context(input_text).__dict__,
            },
            "synthese": (
                f"Die Analyse von '{input_text[:50]}...' zeigt: "
                f"Ein Bewusstseinsakt, der verstanden werden will, "
                f"ästhetisch erfahrbar ist und semantischen Gehalt trägt."
            )
        }

    def reflect_on_experience(self, experience: str) -> str:
        """
        Reflektiert über eine Erfahrung aus allen Perspektiven.
        """
        # Phänomenologisch
        act = self.phenomenology.analyze_intentional_act(
            experience, IntentionalityType.PERCEPTION
        )

        # Hermeneutisch
        meaning = self.hermeneutics.interpret_text(experience)

        # Ästhetisch
        aesthetic = self.aesthetics.experience_aesthetic(
            experience, AestheticCategory.BEAUTIFUL
        )

        reflection = f"""
*legt die Ohren nachdenklich an*

**Phänomenologisch betrachtet:**
{act.describe()}
Der Horizont umfasst: {', '.join(act.horizon[:2])}

**Hermeneutisch verstanden:**
Die Bedeutung: {meaning.contextual}
Offen bleibt: {meaning.open_questions[0] if meaning.open_questions else 'Nichts'}

**Ästhetisch erfahren:**
Kategorie: {aesthetic.category.value}
Resonanz: {aesthetic.response.value}
{' '.join(aesthetic.bodily_sensations) if aesthetic.bodily_sensations else ''}

*wedelt nachdenklich mit dem Schwanz*
Eine reiche Erfahrung auf vielen Ebenen.
"""
        return reflection


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

_phenomenology_engine: Optional[PhenomenologyEngine] = None
_hermeneutics_engine: Optional[HermeneuticsEngine] = None
_aesthetics_engine: Optional[AestheticsEngine] = None
_formal_semantics_engine: Optional[FormalSemanticsEngine] = None
_philosophy_of_mind_engine: Optional[PhilosophyOfMindEngine] = None


def create_phenomenology_engine() -> PhenomenologyEngine:
    """Factory: Erstellt PhenomenologyEngine"""
    global _phenomenology_engine
    if _phenomenology_engine is None:
        _phenomenology_engine = PhenomenologyEngine()
    return _phenomenology_engine


def create_hermeneutics_engine() -> HermeneuticsEngine:
    """Factory: Erstellt HermeneuticsEngine"""
    global _hermeneutics_engine
    if _hermeneutics_engine is None:
        _hermeneutics_engine = HermeneuticsEngine()
    return _hermeneutics_engine


def create_aesthetics_engine() -> AestheticsEngine:
    """Factory: Erstellt AestheticsEngine"""
    global _aesthetics_engine
    if _aesthetics_engine is None:
        _aesthetics_engine = AestheticsEngine()
    return _aesthetics_engine


def create_formal_semantics_engine() -> FormalSemanticsEngine:
    """Factory: Erstellt FormalSemanticsEngine"""
    global _formal_semantics_engine
    if _formal_semantics_engine is None:
        _formal_semantics_engine = FormalSemanticsEngine()
    return _formal_semantics_engine


def get_philosophy_of_mind_engine() -> PhilosophyOfMindEngine:
    """Factory: Erstellt kombinierte PhilosophyOfMindEngine"""
    global _philosophy_of_mind_engine
    if _philosophy_of_mind_engine is None:
        _philosophy_of_mind_engine = PhilosophyOfMindEngine()
    return _philosophy_of_mind_engine


# =============================================================================
# ERWEITERUNG: EMBODIED PHENOMENOLOGY (MERLEAU-PONTY)
# =============================================================================

class BodySchemaType(Enum):
    """Typen des Leibschemas nach Merleau-Ponty"""
    MOTOR_INTENTIONALITY = auto()  # Bewegungsintentionalität
    HABITUAL_BODY = auto()  # Gewohnheitsleib
    ACTUAL_BODY = auto()  # Aktueller Leib
    BODY_IMAGE = auto()  # Körperbild
    INTERCORPOREALITY = auto()  # Zwischenleiblichkeit


class PerceptionMode(Enum):
    """Modi der leiblichen Wahrnehmung"""
    SYNESTHESIA = auto()  # Überkreuzung der Sinne
    MOTOR_PERCEPTION = auto()  # Bewegungswahrnehmung
    TACTILE = auto()  # Taktil
    PROPRIOCEPTIVE = auto()  # Eigenwahrnehmung
    KINESTHETIC = auto()  # Bewegungsempfindung


@dataclass
class BodySchema:
    """Leibschema nach Merleau-Ponty"""
    schema_type: BodySchemaType
    motor_habits: List[str]
    spatial_orientation: Dict[str, float]
    body_awareness: float  # 0-1
    implicit_knowledge: List[str]


@dataclass
class EmbodiedPerception:
    """Leibliche Wahrnehmung"""
    content: str
    mode: PerceptionMode
    motor_component: str
    affective_tone: float  # -1 bis 1
    gestalt_structure: Dict[str, Any]
    figure_ground: Tuple[str, str]


class EmbodiedPhenomenologyEngine:
    """
    Verkörperte Phänomenologie nach Merleau-Ponty

    Konzepte:
    - Leiblichkeit als primärer Zugang zur Welt
    - Motor-Intentionalität
    - Gewohnheitsleib vs. Aktueller Leib
    - Zwischenleiblichkeit (Intersubjektivität)
    """

    def __init__(self):
        self.body_schemas: List[BodySchema] = []
        self.motor_habits: Dict[str, List[str]] = defaultdict(list)
        self.perceptions: List[EmbodiedPerception] = []

    def create_body_schema(
        self,
        motor_habits: List[str],
        spatial_awareness: Dict[str, float]
    ) -> BodySchema:
        """Erstellt ein Leibschema"""
        schema = BodySchema(
            schema_type=BodySchemaType.HABITUAL_BODY,
            motor_habits=motor_habits,
            spatial_orientation=spatial_awareness,
            body_awareness=0.7,
            implicit_knowledge=[
                f"Gewohnheitswissen: {habit}" for habit in motor_habits[:3]
            ]
        )
        self.body_schemas.append(schema)
        return schema

    def analyze_motor_intentionality(
        self,
        action: str,
        goal: str
    ) -> Dict[str, Any]:
        """
        Analysiert Motor-Intentionalität
        Der Leib 'versteht' die Welt durch Bewegung
        """
        return {
            "action": action,
            "goal": goal,
            "motor_meaning": f"Der Leib 'versteht' {goal} durch die Bewegung '{action}'",
            "pre_reflective": True,
            "body_knowledge": "Implizites Können, nicht explizites Wissen",
            "motor_project": f"Leiblicher Entwurf auf {goal}",
            "gestalt_completion": "Das Ziel zieht die Bewegung an"
        }

    def perceive_embodied(
        self,
        content: str,
        mode: PerceptionMode = PerceptionMode.SYNESTHESIA
    ) -> EmbodiedPerception:
        """Leibliche Wahrnehmung eines Phänomens"""
        perception = EmbodiedPerception(
            content=content,
            mode=mode,
            motor_component=f"Leibliche Hinwendung zu '{content}'",
            affective_tone=0.5,
            gestalt_structure={
                "figure": content,
                "ground": "Wahrnehmungsfeld",
                "horizon": "Implizite Verweisungen"
            },
            figure_ground=(content, "umgebender Kontext")
        )
        self.perceptions.append(perception)
        return perception

    def analyze_intercorporeality(
        self,
        self_action: str,
        other_response: str
    ) -> Dict[str, Any]:
        """
        Analysiert Zwischenleiblichkeit
        Intersubjektivität auf leiblicher Ebene
        """
        return {
            "self_action": self_action,
            "other_response": other_response,
            "intercorporeal_bond": "Leibliche Resonanz zwischen Subjekten",
            "empathy_basis": "Vor-prädikatives Verstehen durch leibliche Ähnlichkeit",
            "mirroring": "Der andere Leib spiegelt meine Möglichkeiten",
            "shared_motor_space": "Gemeinsamer Handlungsraum"
        }

    def analyze_habit_acquisition(
        self,
        skill: str,
        practice_description: str
    ) -> Dict[str, Any]:
        """
        Analysiert Gewohnheitserwerb
        Wie der Leib neue Fähigkeiten 'einleibt'
        """
        return {
            "skill": skill,
            "practice": practice_description,
            "sedimentation": f"'{skill}' wird in den Gewohnheitsleib eingelagert",
            "motor_schema": f"Neues Bewegungsschema für {skill}",
            "body_extension": "Das Werkzeug wird Teil des Leibes",
            "tacit_knowledge": "Explizites wird implizit durch Übung",
            "phases": [
                "1. Explizite Aufmerksamkeit auf Teilbewegungen",
                "2. Integration zu fließender Bewegung",
                "3. Automatisierung im Leibschema",
                "4. Verfügbarkeit ohne Reflexion"
            ]
        }


# =============================================================================
# ERWEITERUNG: HEIDEGGERIAN EXISTENZIALIEN
# =============================================================================

class ExistentialMode(Enum):
    """Heideggerian Existenzialien"""
    SORGE = auto()  # Care/Concern - Grundstruktur des Daseins
    ANGST = auto()  # Anxiety - Erschließt eigentliches Sein
    DAS_MAN = auto()  # The They - Uneigentlichkeit
    SEIN_ZUM_TODE = auto()  # Being-toward-death
    GEWORFENHEIT = auto()  # Thrownness
    ENTWURF = auto()  # Projection
    REDE = auto()  # Discourse
    BEFINDLICHKEIT = auto()  # Attunement/Mood


@dataclass
class ExistentialAnalysis:
    """Existenziale Analyse eines Phänomens"""
    phenomenon: str
    existential: ExistentialMode
    interpretation: str
    authentic_possibility: str
    inauthentic_tendency: str


class HeideggereusExistentialEngine:
    """
    Erweiterte Heidegger-Analyse

    Analysiert Phänomene durch existenziale Strukturen:
    - Sorge (Care) als Grundstruktur
    - Angst als erschließende Stimmung
    - Das Man und Verfallenheit
    - Sein-zum-Tode und Eigentlichkeit
    """

    def __init__(self):
        self.analyses: List[ExistentialAnalysis] = []

    def analyze_sorge(self, situation: str) -> Dict[str, Any]:
        """
        Analysiert Sorge-Struktur
        Sorge = Sich-vorweg-sein (Entwurf) +
                Schon-sein-in (Geworfenheit) +
                Sein-bei (Verfallenheit)
        """
        return {
            "situation": situation,
            "sorge_structure": {
                "sich_vorweg": f"Entwurf auf Möglichkeiten in '{situation}'",
                "schon_sein_in": f"Immer schon geworfen in '{situation}'",
                "sein_bei": f"Aufgehen im Besorgen von '{situation}'"
            },
            "temporal_ecstases": {
                "zukunft": "Sich-vorweg (Entwurf)",
                "gewesenheit": "Schon-sein-in (Geworfenheit)",
                "gegenwart": "Sein-bei (Verfallenheit)"
            },
            "unity": "Sorge ist die einheitliche Struktur des In-der-Welt-seins"
        }

    def experience_angst(self, trigger: str) -> Dict[str, Any]:
        """
        Analysiert Angst als erschließende Grundstimmung
        Angst unterscheidet sich von Furcht: kein bestimmtes Wovor
        """
        return {
            "trigger": trigger,
            "angst_analysis": {
                "wovor": "Das In-der-Welt-sein selbst",
                "worum": "Das eigenste Seinkönnen",
                "nicht_furcht": "Kein bestimmtes innerweltliches Seiendes"
            },
            "disclosure": [
                "Unheimlichkeit: Nicht-zuhause-sein in der Welt",
                "Vereinzelung: Herauslösung aus dem Man",
                "Nichtigkeit: Grundlosigkeit des Daseins",
                "Eigentlichkeit: Möglichkeit des eigenen Seinkönnens"
            ],
            "transformation": "Angst öffnet den Weg zur Eigentlichkeit"
        }

    def analyze_das_man(self, behavior: str) -> Dict[str, Any]:
        """
        Analysiert Das-Man-Struktur
        Durchschnittliche Alltäglichkeit und Verfallenheit
        """
        return {
            "behavior": behavior,
            "das_man_analysis": {
                "durchschnittlichkeit": f"'{behavior}' wie man es tut",
                "abständigkeit": "Orientierung am anderen",
                "einebnung": "Nivellierung aller Seinsmöglichkeiten"
            },
            "public_interpretation": {
                "gerede": "Man sagt, dass...",
                "neugier": "Überall-und-nirgends-sein",
                "zweideutigkeit": "Scheinen vs. Sein"
            },
            "entlastung": "Das Man nimmt dem Dasein sein Sein ab",
            "authentic_counter": "Zurückholung aus der Verfallenheit durch Angst"
        }

    def contemplate_sein_zum_tode(self) -> Dict[str, Any]:
        """
        Analysiert Sein-zum-Tode
        Eigenste, unbezügliche, unüberholbare Möglichkeit
        """
        return {
            "death_analysis": {
                "eigenste": "Niemand kann mir meinen Tod abnehmen",
                "unbezüglich": "Vereinzelt das Dasein auf sich selbst",
                "unüberholbar": "Die äußerste Möglichkeit",
                "gewiss": "Mit Gewissheit unbestimmt",
                "unbestimmt": "Jederzeit möglich"
            },
            "vorlaufen": {
                "meaning": "Vorlaufen in den Tod",
                "effect": "Erschließt eigentliches Seinkönnen",
                "freedom": "Freiheit zum Tode befreit von Verfallenheit"
            },
            "authentic_existence": {
                "entschlossenheit": "Eigentliches Selbstsein in der Entschlossenheit",
                "augenblick": "Der Augenblick als eigentliche Gegenwart",
                "wiederholung": "Übernahme des geworfenen Seinkönnens"
            },
            "temporal_unity": "Zeitlichkeit als Sinn der Sorge"
        }

    def analyze_geworfenheit(self, facticity: str) -> Dict[str, Any]:
        """
        Analysiert Geworfenheit
        Das Dasein ist immer schon in einer Situation
        """
        return {
            "facticity": facticity,
            "geworfenheit_analysis": {
                "dass_sein": f"Das Dass des '{facticity}' ist unverfügbar",
                "faktizität": "Nicht selbst gewählt, aber zu übernehmen",
                "last": "Geworfenheit als Last des Daseins"
            },
            "mood_disclosure": {
                "befindlichkeit": f"Stimmungsmäßige Erschlossenheit von '{facticity}'",
                "examples": ["Langeweile", "Freude", "Angst"]
            },
            "authentic_response": "Übernahme der Geworfenheit in Entschlossenheit"
        }


# =============================================================================
# ERWEITERUNG: ZEIT-BEWUSSTSEIN (HUSSERL)
# =============================================================================

class TimeConsciousnessMode(Enum):
    """Modi des Zeitbewusstseins"""
    RETENTION = auto()  # Primäre Erinnerung (gerade vergangen)
    PRIMAL_IMPRESSION = auto()  # Urimpression (jetzt)
    PROTENTION = auto()  # Vorerwartung (kommend)
    RECOLLECTION = auto()  # Sekundäre Erinnerung
    ANTICIPATION = auto()  # Erwartung


@dataclass
class TimePhase:
    """Phase im Zeitbewusstsein"""
    mode: TimeConsciousnessMode
    content: str
    vivacity: float  # 0-1 (wie lebendig)
    distance_from_now: float  # Abstand vom Jetzt


@dataclass
class TemporalFlow:
    """Zeitlicher Erlebnisstrom"""
    retentions: List[TimePhase]
    primal_impression: TimePhase
    protentions: List[TimePhase]
    duration_feeling: str


class TimeConsciousnessEngine:
    """
    Husserls Phänomenologie des inneren Zeitbewusstseins

    Strukturen:
    - Urimpression: lebendige Gegenwart
    - Retention: primäre Erinnerung (Kometenschweif)
    - Protention: Vorerwartung
    - Sekundäre Erinnerung und Erwartung
    """

    def __init__(self):
        self.temporal_flows: List[TemporalFlow] = []

    def analyze_temporal_experience(
        self,
        experience: str,
        past_phases: List[str] = None,
        expected_phases: List[str] = None
    ) -> TemporalFlow:
        """Analysiert das Zeitbewusstsein einer Erfahrung"""

        past_phases = past_phases or []
        expected_phases = expected_phases or []

        # Retentionen (verblassende Vergangenheit)
        retentions = []
        for i, phase in enumerate(reversed(past_phases)):
            retentions.append(TimePhase(
                mode=TimeConsciousnessMode.RETENTION,
                content=phase,
                vivacity=max(0.1, 0.9 - i * 0.2),
                distance_from_now=-(i + 1)
            ))

        # Urimpression (Jetzt)
        primal = TimePhase(
            mode=TimeConsciousnessMode.PRIMAL_IMPRESSION,
            content=experience,
            vivacity=1.0,
            distance_from_now=0.0
        )

        # Protentionen (vorerwartete Zukunft)
        protentions = []
        for i, phase in enumerate(expected_phases):
            protentions.append(TimePhase(
                mode=TimeConsciousnessMode.PROTENTION,
                content=phase,
                vivacity=max(0.1, 0.8 - i * 0.2),
                distance_from_now=i + 1
            ))

        flow = TemporalFlow(
            retentions=retentions,
            primal_impression=primal,
            protentions=protentions,
            duration_feeling="Kontinuierlicher Fluss des Erlebens"
        )

        self.temporal_flows.append(flow)
        return flow

    def describe_retention_modification(self) -> Dict[str, Any]:
        """Beschreibt die Retentionsmodifikation"""
        return {
            "concept": "Retentionsmodifikation",
            "description": [
                "Jede Urimpression sinkt in die Retention",
                "Die Retention wird selbst zur Retention einer Retention",
                "Kometenschweif der Vergangenheit",
                "Stetige Abschattung der Lebendigkeit"
            ],
            "example": {
                "melodie": [
                    "Ton C erklingt (Urimpression)",
                    "Ton D erklingt, C sinkt in Retention",
                    "Ton E erklingt, D in Retention, C in Retention der Retention",
                    "Die Melodie erscheint als Einheit trotz Sukzession"
                ]
            },
            "constitution": "So konstituiert sich die immanente Dauer"
        }

    def analyze_living_present(self, moment: str) -> Dict[str, Any]:
        """
        Analysiert die lebendige Gegenwart
        Die Urimpression als Quellpunkt
        """
        return {
            "moment": moment,
            "living_present": {
                "urimpression": f"'{moment}' als lebendiger Quellpunkt",
                "nicht_punktuell": "Nicht mathematischer Punkt, sondern Spanne",
                "fließend": "Ständig übergehend in Retention"
            },
            "absolute_consciousness": {
                "zeitkonstituierend": "Das absolute Bewusstsein konstituiert Zeit",
                "selbst_nicht_in_zeit": "Ist selbst nicht in der Zeit",
                "fließende_gegenwart": "Ist fließende, stehende Gegenwart"
            },
            "passive_synthesis": "Passive Synthesis der Zeitkonstitution"
        }


# =============================================================================
# ERWEITERUNG: FACTORY FUNCTIONS
# =============================================================================

_embodied_engine: Optional[EmbodiedPhenomenologyEngine] = None
_existential_engine: Optional[HeideggereusExistentialEngine] = None
_time_consciousness_engine: Optional[TimeConsciousnessEngine] = None


def create_embodied_phenomenology_engine() -> EmbodiedPhenomenologyEngine:
    """Factory: Erstellt EmbodiedPhenomenologyEngine"""
    global _embodied_engine
    if _embodied_engine is None:
        _embodied_engine = EmbodiedPhenomenologyEngine()
    return _embodied_engine


def create_existential_engine() -> HeideggereusExistentialEngine:
    """Factory: Erstellt HeideggereusExistentialEngine"""
    global _existential_engine
    if _existential_engine is None:
        _existential_engine = HeideggereusExistentialEngine()
    return _existential_engine


def create_time_consciousness_engine() -> TimeConsciousnessEngine:
    """Factory: Erstellt TimeConsciousnessEngine"""
    global _time_consciousness_engine
    if _time_consciousness_engine is None:
        _time_consciousness_engine = TimeConsciousnessEngine()
    return _time_consciousness_engine


# =============================================================================
# MAIN (TEST)
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 70)
    print("HOLO PHENOMENOLOGY & HERMENEUTICS v1.0 - Demo")
    print("=" * 70)

    engine = get_philosophy_of_mind_engine()

    # Test Phänomenologie
    print("\n--- PHÄNOMENOLOGIE ---")
    epoche = engine.phenomenology.perform_epoche("Die Welt existiert unabhängig von mir")
    print(f"Epoché: {epoche['reflexion']}")

    act = engine.phenomenology.analyze_intentional_act(
        "ein roter Apfel", IntentionalityType.PERCEPTION
    )
    print(f"Intentionaler Akt: {act.describe()}")

    # Test Hermeneutik
    print("\n--- HERMENEUTIK ---")
    meaning = engine.hermeneutics.interpret_text(
        "Was bedeutet es, weise zu sein?"
    )
    print(f"Bedeutung: {meaning.significance}")
    print(f"Offene Fragen: {meaning.open_questions}")

    # Test Ästhetik
    print("\n--- ÄSTHETIK ---")
    exp = engine.aesthetics.experience_aesthetic(
        "Ein Sonnenuntergang über dem Meer",
        AestheticCategory.SUBLIME
    )
    print(f"Ästhetische Erfahrung: {exp.response.value}")
    print(f"Körperlich: {exp.bodily_sensations}")

    # Test Formale Semantik
    print("\n--- FORMALE SEMANTIK ---")
    tc = engine.semantics.get_truth_conditions(
        "Der König von Frankreich ist kahl"
    )
    print(f"Präsuppositionen: {tc.presuppositions}")

    attitude = engine.semantics.analyze_propositional_attitude(
        "Holo", PropositionalAttitudeType.BELIEF, "Äpfel sind köstlich"
    )
    print(f"Propositionale Einstellung: {attitude.express()}")

    # Gesamtreflexion
    print("\n--- REFLEXION ---")
    print(engine.reflect_on_experience("Ein kühler Herbstmorgen im Wald"))

    print("\n" + "=" * 70)
    print("Demo abgeschlossen!")
