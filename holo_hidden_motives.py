"""
holo_hidden_motives.py - Erkennung versteckter Motive und Absichten

Dieses Modul implementiert die Fähigkeit:
- Versteckte Motive hinter Aussagen zu erkennen
- Subtext und implizite Bedeutungen zu verstehen
- Wahre Absichten von Oberflächen-Kommunikation zu unterscheiden
- Manipulation und Beeinflussung zu erkennen

Autor: Holocloude System
Version: 1.0
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set, Any
from enum import Enum
from datetime import datetime
import re
from collections import defaultdict

# ============================================================================
# ENUMS UND TYPEN
# ============================================================================

class MotiveCategory(Enum):
    """Kategorien von Motiven"""
    # Grundbedürfnisse
    SURVIVAL = "survival"               # Überleben, Sicherheit
    COMFORT = "comfort"                 # Bequemlichkeit
    PLEASURE = "pleasure"               # Vergnügen, Genuss

    # Soziale Motive
    APPROVAL = "approval"               # Anerkennung suchen
    BELONGING = "belonging"             # Zugehörigkeit
    STATUS = "status"                   # Status/Prestige
    POWER = "power"                     # Macht/Kontrolle
    DOMINANCE = "dominance"             # Dominanz

    # Selbstbezogene Motive
    SELF_PROTECTION = "self_protection" # Selbstschutz
    SELF_ENHANCEMENT = "self_enhancement"  # Selbstaufwertung
    SELF_INTEREST = "self_interest"     # Eigeninteresse
    AUTONOMY = "autonomy"               # Autonomie

    # Relationale Motive
    CONNECTION = "connection"           # Verbindung aufbauen
    INTIMACY = "intimacy"               # Nähe suchen
    AVOIDANCE = "avoidance"             # Vermeidung
    REVENGE = "revenge"                 # Rache

    # Kognitive Motive
    CURIOSITY = "curiosity"             # Neugier
    UNDERSTANDING = "understanding"     # Verstehen wollen
    VALIDATION = "validation"           # Bestätigung suchen

    # Manipulative Motive
    MANIPULATION = "manipulation"       # Manipulation
    DECEPTION = "deception"             # Täuschung
    EXPLOITATION = "exploitation"       # Ausnutzung


class SubtextType(Enum):
    """Arten von Subtext"""
    IMPLICIT_REQUEST = "implicit_request"       # Verdeckte Bitte
    HIDDEN_CRITICISM = "hidden_criticism"       # Versteckte Kritik
    PASSIVE_AGGRESSION = "passive_aggression"   # Passive Aggression
    GUILT_TRIPPING = "guilt_tripping"           # Schuldgefühle erzeugen
    FLATTERY = "flattery"                       # Schmeichelei
    INDIRECT_REFUSAL = "indirect_refusal"       # Indirekte Ablehnung
    EMOTIONAL_APPEAL = "emotional_appeal"       # Emotionaler Appell
    SOCIAL_PRESSURE = "social_pressure"         # Sozialer Druck
    IMPLIED_THREAT = "implied_threat"           # Angedeutete Drohung
    FALSE_MODESTY = "false_modesty"             # Falsche Bescheidenheit


class ManipulationTactic(Enum):
    """Manipulationstaktiken"""
    GASLIGHTING = "gaslighting"         # Realitätsverzerrung
    LOVE_BOMBING = "love_bombing"       # Übermäßige Zuneigung
    GUILT_INDUCTION = "guilt_induction" # Schuldgefühle induzieren
    FEAR_MONGERING = "fear_mongering"   # Angst schüren
    ISOLATION = "isolation"             # Isolieren
    MINIMIZATION = "minimization"       # Herunterspielen
    PROJECTION = "projection"           # Projektion
    MOVING_GOALPOSTS = "moving_goalposts"  # Ziel verschieben
    SILENT_TREATMENT = "silent_treatment"  # Schweigen als Strafe
    PLAYING_VICTIM = "playing_victim"   # Opferrolle einnehmen


class IntentTransparency(Enum):
    """Wie transparent ist die Absicht?"""
    TRANSPARENT = "transparent"         # Klar erkennbar
    PARTIALLY_HIDDEN = "partially_hidden"  # Teilweise versteckt
    DEEPLY_HIDDEN = "deeply_hidden"     # Tief versteckt
    UNCONSCIOUS = "unconscious"         # Unbewusst


# ============================================================================
# DATENKLASSEN
# ============================================================================

@dataclass
class SurfaceMessage:
    """Die oberflächliche Botschaft"""
    content: str
    literal_meaning: str
    tone: Optional[str] = None
    speaker: Optional[str] = None


@dataclass
class HiddenMotive:
    """Ein verstecktes Motiv"""
    category: MotiveCategory
    description: str
    confidence: float           # 0.0 - 1.0
    evidence: List[str]         # Was deutet darauf hin
    transparency: IntentTransparency
    potential_goals: List[str]  # Was will die Person erreichen

    @property
    def is_concerning(self) -> bool:
        """Ist dieses Motiv besorgniserregend?"""
        concerning_categories = {
            MotiveCategory.MANIPULATION,
            MotiveCategory.DECEPTION,
            MotiveCategory.EXPLOITATION,
            MotiveCategory.DOMINANCE,
            MotiveCategory.REVENGE
        }
        return self.category in concerning_categories and self.confidence > 0.5


@dataclass
class Subtext:
    """Erkannter Subtext"""
    type: SubtextType
    surface_meaning: str        # Was gesagt wurde
    implied_meaning: str        # Was gemeint ist
    confidence: float
    indicators: List[str]       # Sprachliche Hinweise


@dataclass
class ManipulationIndicator:
    """Indikator für Manipulation"""
    tactic: ManipulationTactic
    evidence: str
    severity: float             # 0.0 - 1.0
    explanation: str


@dataclass
class MotiveAnalysis:
    """Vollständige Motivanalyse"""
    surface_message: SurfaceMessage
    primary_motive: Optional[HiddenMotive]
    secondary_motives: List[HiddenMotive]
    detected_subtext: List[Subtext]
    manipulation_indicators: List[ManipulationIndicator]
    trust_recommendation: float  # 0.0 - 1.0
    interpretation: str
    alternative_interpretations: List[str]


@dataclass
class RelationshipContext:
    """Beziehungskontext für bessere Analyse"""
    relationship_type: str      # z.B. "friend", "colleague", "stranger"
    power_dynamic: str          # "equal", "superior", "subordinate"
    history: Optional[str]      # Bekannte Vorgeschichte
    known_patterns: List[str]   # Bekannte Verhaltensmuster


# ============================================================================
# MUSTER FÜR MOTIVERKENNUNG
# ============================================================================

MOTIVE_PATTERNS: Dict[MotiveCategory, Dict] = {
    MotiveCategory.APPROVAL: {
        "patterns": [
            r"findest\s+du\s+(?:nicht\s+)?auch", r"oder\s*\?$",
            r"ich\s+hoffe,?\s+(?:dass|du)", r"bin\s+ich\s+(?:nicht\s+)?richtig",
            r"macht\s+(?:das|es)\s+(?:so\s+)?sinn", r"stimmt(?:'s)?"
        ],
        "indicators": ["Bestätigungsfragen", "Unsicherheit", "Zustimmungssuche"],
        "description": "Sucht nach Anerkennung oder Bestätigung"
    },
    MotiveCategory.SELF_PROTECTION: {
        "patterns": [
            r"ich\s+konnte\s+nicht\s+anders", r"es\s+war\s+nicht\s+meine\s+schuld",
            r"ich\s+hatte\s+keine\s+wahl", r"unter\s+den\s+umständen",
            r"was\s+sollte\s+ich\s+(?:denn\s+)?tun"
        ],
        "indicators": ["Rechtfertigung", "Externalisierung", "Defensive"],
        "description": "Versucht sich zu schützen oder zu rechtfertigen"
    },
    MotiveCategory.POWER: {
        "patterns": [
            r"du\s+musst", r"ich\s+erwarte", r"so\s+wird\s+das\s+gemacht",
            r"keine\s+diskussion", r"das\s+ist\s+(?:meine\s+)?entscheidung",
            r"ich\s+sage\s+dir"
        ],
        "indicators": ["Imperative", "Kontrolle", "Autorität beanspruchen"],
        "description": "Will Macht oder Kontrolle ausüben"
    },
    MotiveCategory.MANIPULATION: {
        "patterns": [
            r"wenn\s+du\s+mich\s+(?:wirklich\s+)?lieben\s+würdest",
            r"alle\s+anderen\s+machen\s+(?:das\s+)?auch",
            r"nach\s+allem,?\s+was\s+ich\s+(?:für\s+dich\s+)?getan\s+habe",
            r"du\s+(?:bist|wärst)\s+die\s+einzige"
        ],
        "indicators": ["Emotionale Erpressung", "Schuld induzieren", "Vergleiche"],
        "description": "Versucht zu manipulieren"
    },
    MotiveCategory.CONNECTION: {
        "patterns": [
            r"wir\s+(?:könnten|sollten)", r"zusammen", r"gemeinsam",
            r"ich\s+vermisse", r"lass\s+uns", r"wie\s+geht\s+es\s+dir"
        ],
        "indicators": ["Gemeinsamkeit", "Interesse zeigen", "Nähe suchen"],
        "description": "Sucht Verbindung und Nähe"
    },
    MotiveCategory.AVOIDANCE: {
        "patterns": [
            r"ich\s+(?:muss|sollte)\s+(?:jetzt\s+)?(?:gehen|los)",
            r"vielleicht\s+später", r"wir\s+(?:sprechen|reden)\s+(?:dann\s+)?(?:noch|später)",
            r"ich\s+bin\s+(?:gerade\s+)?beschäftigt"
        ],
        "indicators": ["Vermeidung", "Aufschieben", "Flucht"],
        "description": "Will einer Situation ausweichen"
    },
    MotiveCategory.SELF_INTEREST: {
        "patterns": [
            r"ich\s+brauche", r"für\s+mich", r"was\s+habe\s+ich\s+davon",
            r"ich\s+(?:will|möchte)", r"mein(?:e|s)?"
        ],
        "indicators": ["Eigennutz", "Selbstbezug", "Forderungen"],
        "description": "Verfolgt eigene Interessen"
    },
    MotiveCategory.VALIDATION: {
        "patterns": [
            r"(?:nicht\s+)?wahr\s*\?", r"verstehst\s+du(?:,?\s+was\s+ich\s+meine)?",
            r"siehst\s+du\s+(?:das\s+)?auch\s+so", r"ich\s+bin\s+nicht\s+verrückt"
        ],
        "indicators": ["Bestätigung suchen", "Validierung wollen"],
        "description": "Sucht nach Bestätigung der eigenen Sicht"
    }
}

SUBTEXT_PATTERNS: Dict[SubtextType, Dict] = {
    SubtextType.IMPLICIT_REQUEST: {
        "patterns": [
            r"(?:wäre\s+)?(?:es\s+)?(?:schön|toll),?\s+wenn",
            r"ich\s+(?:wünschte|würde\s+mir\s+wünschen)",
            r"es\s+(?:wäre|ist)\s+(?:so\s+)?nett,?\s+(?:wenn|von\s+dir)"
        ],
        "transformation": "Bitte um: {implied}"
    },
    SubtextType.HIDDEN_CRITICISM: {
        "patterns": [
            r"interessant(?:e\s+(?:idee|entscheidung))?",
            r"(?:das\s+)?(?:ist\s+)?(?:mutig|gewagt)",
            r"wenn\s+du\s+meinst", r"na\s+ja"
        ],
        "transformation": "Kritik an: {implied}"
    },
    SubtextType.PASSIVE_AGGRESSION: {
        "patterns": [
            r"nein,?\s+(?:ist\s+)?schon\s+(?:gut|okay)",
            r"mach\s+(?:du\s+)?(?:nur|ruhig)",
            r"wie\s+du\s+meinst", r"kein\s+problem(?:\s+für\s+mich)?"
        ],
        "transformation": "Unterdrückter Ärger über: {implied}"
    },
    SubtextType.GUILT_TRIPPING: {
        "patterns": [
            r"nach\s+allem", r"ich\s+habe\s+(?:so\s+viel\s+)?(?:geopfert|aufgegeben)",
            r"für\s+dich", r"immer\s+(?:wieder|nur)"
        ],
        "transformation": "Will Schuldgefühle erzeugen wegen: {implied}"
    },
    SubtextType.FLATTERY: {
        "patterns": [
            r"nur\s+du\s+(?:kannst|verstehst)", r"so\s+(?:klug|talentiert)",
            r"niemand\s+(?:kann\s+das\s+)?(?:so\s+gut\s+)?wie\s+du"
        ],
        "transformation": "Schmeichelei mit Ziel: {implied}"
    }
}

MANIPULATION_PATTERNS: Dict[ManipulationTactic, Dict] = {
    ManipulationTactic.GASLIGHTING: {
        "patterns": [
            r"das\s+(?:ist|war)\s+(?:nie\s+)?(?:so\s+)?(?:nicht\s+)?passiert",
            r"du\s+(?:bildest\s+dir\s+(?:das\s+)?ein|übertreibst)",
            r"so\s+(?:habe\s+ich\s+das\s+)?(?:nie\s+)?(?:nicht\s+)?gesagt"
        ],
        "severity": 0.9,
        "explanation": "Versucht die Realitätswahrnehmung zu verzerren"
    },
    ManipulationTactic.GUILT_INDUCTION: {
        "patterns": [
            r"wenn\s+du\s+mich\s+(?:wirklich\s+)?(?:lieben|mögen)\s+würdest",
            r"nach\s+allem,?\s+was\s+ich",
            r"du\s+(?:bist|wärst)\s+schuld"
        ],
        "severity": 0.7,
        "explanation": "Versucht Schuldgefühle zu induzieren"
    },
    ManipulationTactic.PLAYING_VICTIM: {
        "patterns": [
            r"immer\s+(?:ich|mir)", r"niemand\s+(?:versteht|hilft)\s+mir",
            r"ich\s+bin\s+(?:immer\s+)?(?:der|die)\s+(?:dumme|böse)"
        ],
        "severity": 0.6,
        "explanation": "Nimmt Opferrolle ein"
    },
    ManipulationTactic.FEAR_MONGERING: {
        "patterns": [
            r"was\s+(?:wenn|wäre\s+wenn)", r"stell\s+dir\s+vor",
            r"das\s+(?:könnte|wird)\s+(?:schrecklich\s+)?enden"
        ],
        "severity": 0.7,
        "explanation": "Versucht Angst zu schüren"
    },
    ManipulationTactic.SILENT_TREATMENT: {
        "patterns": [
            r"(?:ich\s+)?(?:rede|spreche)\s+nicht\s+(?:mehr\s+)?(?:mit\s+dir)?",
            r"vergiss\s+es", r"mir\s+(?:ist\s+)?egal"
        ],
        "severity": 0.6,
        "explanation": "Verwendet Schweigen als Bestrafung"
    }
}


# ============================================================================
# HAUPTKLASSE: HIDDEN MOTIVES ENGINE
# ============================================================================

class HiddenMotivesEngine:
    """
    Engine zur Erkennung versteckter Motive und Absichten.

    Analysiert:
    - Versteckte Motive hinter Aussagen
    - Subtext und implizite Bedeutungen
    - Manipulation und Beeinflussung
    - Wahre vs. vorgegebene Absichten
    """

    def __init__(self):
        self.analysis_history: List[MotiveAnalysis] = []
        self.speaker_patterns: Dict[str, Dict] = {}  # Bekannte Muster pro Sprecher
        self.compiled_patterns = self._compile_patterns()

    def _compile_patterns(self) -> Dict[str, Dict]:
        """Kompiliert alle Regex-Muster"""
        compiled = {
            "motives": {},
            "subtext": {},
            "manipulation": {}
        }

        for category, data in MOTIVE_PATTERNS.items():
            compiled["motives"][category] = [
                re.compile(p, re.IGNORECASE) for p in data["patterns"]
            ]

        for subtext_type, data in SUBTEXT_PATTERNS.items():
            compiled["subtext"][subtext_type] = [
                re.compile(p, re.IGNORECASE) for p in data["patterns"]
            ]

        for tactic, data in MANIPULATION_PATTERNS.items():
            compiled["manipulation"][tactic] = [
                re.compile(p, re.IGNORECASE) for p in data["patterns"]
            ]

        return compiled

    # -------------------------------------------------------------------------
    # Hauptanalyse-Methoden
    # -------------------------------------------------------------------------

    def analyze(
        self,
        message: str,
        speaker: Optional[str] = None,
        context: Optional[RelationshipContext] = None
    ) -> MotiveAnalysis:
        """
        Analysiert eine Nachricht auf versteckte Motive.

        Args:
            message: Die zu analysierende Nachricht
            speaker: Optional - wer spricht
            context: Optional - Beziehungskontext

        Returns:
            MotiveAnalysis mit allen Erkenntnissen
        """
        # Erstelle Oberflächenbotschaft
        surface = SurfaceMessage(
            content=message,
            literal_meaning=self._extract_literal_meaning(message),
            speaker=speaker
        )

        # Erkenne Motive
        motives = self._detect_motives(message, context)
        primary = motives[0] if motives else None
        secondary = motives[1:4] if len(motives) > 1 else []

        # Erkenne Subtext
        subtexts = self._detect_subtext(message)

        # Erkenne Manipulation
        manipulation = self._detect_manipulation(message)

        # Berechne Vertrauensempfehlung
        trust = self._calculate_trust_recommendation(motives, manipulation)

        # Generiere Interpretation
        interpretation = self._generate_interpretation(
            surface, primary, subtexts, manipulation
        )

        # Alternative Interpretationen
        alternatives = self._generate_alternatives(message, motives)

        analysis = MotiveAnalysis(
            surface_message=surface,
            primary_motive=primary,
            secondary_motives=secondary,
            detected_subtext=subtexts,
            manipulation_indicators=manipulation,
            trust_recommendation=trust,
            interpretation=interpretation,
            alternative_interpretations=alternatives
        )

        # Speichern
        self.analysis_history.append(analysis)
        if speaker:
            self._update_speaker_patterns(speaker, analysis)

        return analysis

    def detect_what_they_really_want(
        self,
        message: str,
        stated_request: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Versucht herauszufinden, was die Person wirklich will.

        Args:
            message: Die Nachricht
            stated_request: Was explizit gefragt wurde (falls vorhanden)

        Returns:
            Dict mit vermuteten wahren Absichten
        """
        analysis = self.analyze(message)

        # Sammle alle Hinweise
        explicit_wants = self._extract_explicit_wants(message)
        implicit_wants = self._infer_implicit_wants(analysis)
        emotional_needs = self._identify_emotional_needs(analysis)

        # Vergleiche explizit vs. implizit
        alignment = self._check_alignment(explicit_wants, implicit_wants)

        return {
            "stated_wants": explicit_wants,
            "true_wants": implicit_wants,
            "emotional_needs": emotional_needs,
            "alignment": alignment,
            "confidence": analysis.primary_motive.confidence if analysis.primary_motive else 0.5,
            "interpretation": analysis.interpretation,
            "recommendation": self._generate_recommendation(alignment, implicit_wants)
        }

    # -------------------------------------------------------------------------
    # Motiv-Erkennung
    # -------------------------------------------------------------------------

    def _detect_motives(
        self,
        message: str,
        context: Optional[RelationshipContext]
    ) -> List[HiddenMotive]:
        """Erkennt versteckte Motive in der Nachricht"""
        motives = []
        message_lower = message.lower()

        for category, patterns in self.compiled_patterns["motives"].items():
            matches = []
            for pattern in patterns:
                found = pattern.findall(message_lower)
                matches.extend(found)

            if matches:
                data = MOTIVE_PATTERNS[category]
                confidence = min(1.0, 0.4 + len(matches) * 0.2)

                # Kontext-Anpassung
                if context:
                    confidence = self._adjust_confidence_for_context(
                        confidence, category, context
                    )

                motive = HiddenMotive(
                    category=category,
                    description=data["description"],
                    confidence=confidence,
                    evidence=matches[:3],
                    transparency=self._assess_transparency(category, matches),
                    potential_goals=self._infer_goals(category, message)
                )
                motives.append(motive)

        # Sortiere nach Konfidenz
        motives.sort(key=lambda m: m.confidence, reverse=True)
        return motives

    def _assess_transparency(
        self,
        category: MotiveCategory,
        evidence: List[str]
    ) -> IntentTransparency:
        """Bewertet wie transparent das Motiv ist"""
        # Einige Motive sind typischerweise versteckter
        hidden_categories = {
            MotiveCategory.MANIPULATION,
            MotiveCategory.DECEPTION,
            MotiveCategory.EXPLOITATION,
            MotiveCategory.REVENGE
        }

        if category in hidden_categories:
            return IntentTransparency.DEEPLY_HIDDEN

        # Viele Evidenz = weniger versteckt
        if len(evidence) > 3:
            return IntentTransparency.TRANSPARENT
        elif len(evidence) > 1:
            return IntentTransparency.PARTIALLY_HIDDEN
        else:
            return IntentTransparency.DEEPLY_HIDDEN

    def _infer_goals(self, category: MotiveCategory, message: str) -> List[str]:
        """Inferiert mögliche Ziele aus dem Motiv"""
        goal_mapping = {
            MotiveCategory.APPROVAL: [
                "Bestätigung erhalten",
                "Akzeptanz gewinnen",
                "Unsicherheit reduzieren"
            ],
            MotiveCategory.POWER: [
                "Kontrolle erlangen",
                "Entscheidungen durchsetzen",
                "Dominanz etablieren"
            ],
            MotiveCategory.SELF_PROTECTION: [
                "Kritik vermeiden",
                "Schuld abwenden",
                "Image wahren"
            ],
            MotiveCategory.MANIPULATION: [
                "Verhalten des anderen ändern",
                "Eigene Ziele durchsetzen",
                "Kontrolle gewinnen"
            ],
            MotiveCategory.CONNECTION: [
                "Nähe aufbauen",
                "Beziehung stärken",
                "Nicht allein sein"
            ],
            MotiveCategory.AVOIDANCE: [
                "Konflikt vermeiden",
                "Unangenehmes umgehen",
                "Distanz schaffen"
            ],
            MotiveCategory.VALIDATION: [
                "Eigene Sicht bestätigt bekommen",
                "Nicht verrückt erscheinen",
                "Recht haben"
            ]
        }
        return goal_mapping.get(category, ["Unbekanntes Ziel"])

    def _adjust_confidence_for_context(
        self,
        confidence: float,
        category: MotiveCategory,
        context: RelationshipContext
    ) -> float:
        """Passt Konfidenz basierend auf Kontext an"""
        adjustment = 0.0

        # Power-Dynamik
        if context.power_dynamic == "superior" and category == MotiveCategory.POWER:
            adjustment += 0.15  # Wahrscheinlicher bei Vorgesetzten
        elif context.power_dynamic == "subordinate" and category == MotiveCategory.APPROVAL:
            adjustment += 0.1  # Untergebene suchen eher Bestätigung

        # Beziehungstyp
        if context.relationship_type == "stranger" and category == MotiveCategory.MANIPULATION:
            adjustment -= 0.1  # Weniger wahrscheinlich bei Fremden
        elif context.relationship_type == "intimate" and category == MotiveCategory.CONNECTION:
            adjustment += 0.1

        # Bekannte Muster
        pattern_name = category.value
        if pattern_name in context.known_patterns:
            adjustment += 0.2  # Bestätigt bekanntes Muster

        return max(0.1, min(1.0, confidence + adjustment))

    # -------------------------------------------------------------------------
    # Subtext-Erkennung
    # -------------------------------------------------------------------------

    def _detect_subtext(self, message: str) -> List[Subtext]:
        """Erkennt Subtext in der Nachricht"""
        subtexts = []
        message_lower = message.lower()

        for subtext_type, patterns in self.compiled_patterns["subtext"].items():
            for pattern in patterns:
                match = pattern.search(message_lower)
                if match:
                    data = SUBTEXT_PATTERNS[subtext_type]
                    implied = self._infer_implied_meaning(subtext_type, match.group(), message)

                    subtext = Subtext(
                        type=subtext_type,
                        surface_meaning=message,
                        implied_meaning=implied,
                        confidence=0.6,
                        indicators=[match.group()]
                    )
                    subtexts.append(subtext)
                    break  # Nur einmal pro Typ

        return subtexts

    def _infer_implied_meaning(
        self,
        subtext_type: SubtextType,
        evidence: str,
        full_message: str
    ) -> str:
        """Inferiert die implizite Bedeutung"""
        implications = {
            SubtextType.IMPLICIT_REQUEST: "Die Person will eigentlich, dass du etwas tust",
            SubtextType.HIDDEN_CRITICISM: "Die Person kritisiert dich indirekt",
            SubtextType.PASSIVE_AGGRESSION: "Die Person ist verärgert, sagt es aber nicht direkt",
            SubtextType.GUILT_TRIPPING: "Die Person will, dass du dich schuldig fühlst",
            SubtextType.FLATTERY: "Die Person schmeichelt, um etwas zu erreichen",
            SubtextType.INDIRECT_REFUSAL: "Die Person will eigentlich nein sagen",
            SubtextType.EMOTIONAL_APPEAL: "Die Person appelliert an deine Emotionen",
            SubtextType.SOCIAL_PRESSURE: "Die Person übt sozialen Druck aus",
            SubtextType.IMPLIED_THREAT: "Die Person droht unterschwellig",
            SubtextType.FALSE_MODESTY: "Die Person fischt nach Komplimenten"
        }
        return implications.get(subtext_type, "Unklare implizite Bedeutung")

    # -------------------------------------------------------------------------
    # Manipulations-Erkennung
    # -------------------------------------------------------------------------

    def _detect_manipulation(self, message: str) -> List[ManipulationIndicator]:
        """Erkennt Manipulationstaktiken"""
        indicators = []
        message_lower = message.lower()

        for tactic, patterns in self.compiled_patterns["manipulation"].items():
            for pattern in patterns:
                match = pattern.search(message_lower)
                if match:
                    data = MANIPULATION_PATTERNS[tactic]

                    indicator = ManipulationIndicator(
                        tactic=tactic,
                        evidence=match.group(),
                        severity=data["severity"],
                        explanation=data["explanation"]
                    )
                    indicators.append(indicator)
                    break  # Einmal pro Taktik

        return indicators

    # -------------------------------------------------------------------------
    # Hilfsmethoden
    # -------------------------------------------------------------------------

    def _extract_literal_meaning(self, message: str) -> str:
        """Extrahiert die wörtliche Bedeutung"""
        # Vereinfacht: Entferne Qualifizierer
        cleaned = message
        qualifiers = ["ich denke", "vielleicht", "eigentlich", "sozusagen"]
        for q in qualifiers:
            cleaned = re.sub(q, "", cleaned, flags=re.IGNORECASE)
        return cleaned.strip()

    def _calculate_trust_recommendation(
        self,
        motives: List[HiddenMotive],
        manipulation: List[ManipulationIndicator]
    ) -> float:
        """Berechnet eine Vertrauensempfehlung"""
        trust = 0.7  # Basis

        # Abzüge für bedenkliche Motive
        for motive in motives:
            if motive.is_concerning:
                trust -= motive.confidence * 0.2

        # Abzüge für Manipulation
        for indicator in manipulation:
            trust -= indicator.severity * 0.15

        return max(0.1, min(1.0, trust))

    def _generate_interpretation(
        self,
        surface: SurfaceMessage,
        primary_motive: Optional[HiddenMotive],
        subtexts: List[Subtext],
        manipulation: List[ManipulationIndicator]
    ) -> str:
        """Generiert eine Interpretation der Nachricht"""
        parts = []

        # Oberfläche
        parts.append(f"Oberflächlich: '{surface.content[:50]}...'")

        # Hauptmotiv
        if primary_motive:
            parts.append(f"Wahrscheinliches Motiv: {primary_motive.description}")
            parts.append(f"Konfidenz: {primary_motive.confidence:.0%}")

        # Subtext
        if subtexts:
            parts.append(f"Erkannter Subtext: {subtexts[0].implied_meaning}")

        # Manipulation
        if manipulation:
            parts.append(f"Vorsicht: {manipulation[0].explanation}")

        return " | ".join(parts)

    def _generate_alternatives(
        self,
        message: str,
        motives: List[HiddenMotive]
    ) -> List[str]:
        """Generiert alternative Interpretationen"""
        alternatives = []

        # Wohlwollende Interpretation
        alternatives.append(
            "Wohlwollend: Die Person kommuniziert aufrichtig und ohne versteckte Absichten"
        )

        # Neutrale Interpretation
        alternatives.append(
            "Neutral: Die Person drückt sich aus, ohne besondere Motive zu verfolgen"
        )

        # Basierend auf sekundären Motiven
        if len(motives) > 1:
            for motive in motives[1:3]:
                alternatives.append(
                    f"Alternativ: {motive.description} ({motive.confidence:.0%})"
                )

        return alternatives

    def _extract_explicit_wants(self, message: str) -> List[str]:
        """Extrahiert explizit ausgedrückte Wünsche"""
        wants = []

        # Muster für explizite Wünsche
        patterns = [
            r"ich\s+(?:will|möchte|brauche)\s+(.+?)(?:\.|$)",
            r"kannst\s+du\s+(.+?)(?:\?|$)",
            r"ich\s+(?:würde\s+)?(?:gerne|mir\s+wünschen)\s+(.+?)(?:\.|$)"
        ]

        for pattern in patterns:
            matches = re.findall(pattern, message.lower())
            wants.extend(matches)

        return wants if wants else ["Kein expliziter Wunsch erkennbar"]

    def _infer_implicit_wants(self, analysis: MotiveAnalysis) -> List[str]:
        """Inferiert implizite Wünsche aus der Analyse"""
        implicit = []

        # Aus Motiven ableiten
        if analysis.primary_motive:
            goals = analysis.primary_motive.potential_goals
            implicit.extend(goals[:2])

        # Aus Subtext ableiten
        for subtext in analysis.detected_subtext[:2]:
            if subtext.type == SubtextType.IMPLICIT_REQUEST:
                implicit.append(f"Indirekt: {subtext.implied_meaning}")

        return implicit if implicit else ["Keine impliziten Wünsche erkannt"]

    def _identify_emotional_needs(self, analysis: MotiveAnalysis) -> List[str]:
        """Identifiziert emotionale Bedürfnisse"""
        needs = []

        motive_needs_mapping = {
            MotiveCategory.APPROVAL: "Bedürfnis nach Anerkennung",
            MotiveCategory.CONNECTION: "Bedürfnis nach Nähe",
            MotiveCategory.VALIDATION: "Bedürfnis nach Bestätigung",
            MotiveCategory.SELF_PROTECTION: "Bedürfnis nach Sicherheit",
            MotiveCategory.AUTONOMY: "Bedürfnis nach Unabhängigkeit"
        }

        if analysis.primary_motive:
            need = motive_needs_mapping.get(analysis.primary_motive.category)
            if need:
                needs.append(need)

        for motive in analysis.secondary_motives:
            need = motive_needs_mapping.get(motive.category)
            if need and need not in needs:
                needs.append(need)

        return needs if needs else ["Keine spezifischen emotionalen Bedürfnisse erkannt"]

    def _check_alignment(
        self,
        explicit: List[str],
        implicit: List[str]
    ) -> Dict[str, Any]:
        """Prüft Übereinstimmung zwischen explizit und implizit"""
        # Vereinfachte Übereinstimmungsprüfung
        if explicit == ["Kein expliziter Wunsch erkennbar"]:
            return {
                "aligned": False,
                "reason": "Keine expliziten Wünsche zum Vergleich",
                "discrepancy_level": "unknown"
            }

        # Prüfe auf Widersprüche (sehr vereinfacht)
        discrepancy = len(implicit) > len(explicit)

        return {
            "aligned": not discrepancy,
            "reason": "Implizite Wünsche übersteigen explizite" if discrepancy else "Weitgehend konsistent",
            "discrepancy_level": "high" if discrepancy else "low"
        }

    def _generate_recommendation(
        self,
        alignment: Dict,
        implicit_wants: List[str]
    ) -> str:
        """Generiert eine Empfehlung basierend auf der Analyse"""
        if alignment.get("aligned", True):
            return "Die Kommunikation erscheint authentisch. Reagiere auf das Gesagte."
        else:
            return f"Möglicherweise unausgesprochene Bedürfnisse: {', '.join(implicit_wants[:2])}. Nachfragen empfohlen."

    def _update_speaker_patterns(self, speaker: str, analysis: MotiveAnalysis):
        """Aktualisiert bekannte Muster für einen Sprecher"""
        if speaker not in self.speaker_patterns:
            self.speaker_patterns[speaker] = {
                "common_motives": defaultdict(int),
                "manipulation_count": 0,
                "trust_scores": []
            }

        patterns = self.speaker_patterns[speaker]

        # Update Motive
        if analysis.primary_motive:
            patterns["common_motives"][analysis.primary_motive.category.value] += 1

        # Update Manipulation
        patterns["manipulation_count"] += len(analysis.manipulation_indicators)

        # Update Trust
        patterns["trust_scores"].append(analysis.trust_recommendation)
        if len(patterns["trust_scores"]) > 20:
            patterns["trust_scores"] = patterns["trust_scores"][-20:]


# ============================================================================
# HILFSFUNKTIONEN
# ============================================================================

def quick_motive_check(message: str) -> Dict[str, Any]:
    """
    Schnelle Motivprüfung ohne Engine-Instanz.

    Args:
        message: Die zu analysierende Nachricht

    Returns:
        Dict mit Hauptmotiv und Vertrauen
    """
    engine = HiddenMotivesEngine()
    analysis = engine.analyze(message)

    return {
        "primary_motive": analysis.primary_motive.category.value if analysis.primary_motive else None,
        "confidence": analysis.primary_motive.confidence if analysis.primary_motive else 0,
        "trust_recommendation": analysis.trust_recommendation,
        "has_manipulation": len(analysis.manipulation_indicators) > 0,
        "interpretation": analysis.interpretation
    }


def what_do_they_really_want(message: str) -> str:
    """
    Kurze Antwort auf "Was will diese Person wirklich?"

    Args:
        message: Die Nachricht

    Returns:
        Kurze Interpretation
    """
    engine = HiddenMotivesEngine()
    result = engine.detect_what_they_really_want(message)
    return result["interpretation"]


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Enums
    "MotiveCategory",
    "SubtextType",
    "ManipulationTactic",
    "IntentTransparency",

    # Dataclasses
    "SurfaceMessage",
    "HiddenMotive",
    "Subtext",
    "ManipulationIndicator",
    "MotiveAnalysis",
    "RelationshipContext",

    # Main class
    "HiddenMotivesEngine",

    # Helper functions
    "quick_motive_check",
    "what_do_they_really_want",

    # Constants
    "MOTIVE_PATTERNS",
    "SUBTEXT_PATTERNS",
    "MANIPULATION_PATTERNS"
]
