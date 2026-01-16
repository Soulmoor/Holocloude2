"""
holo_deception_detection.py - Täuschungserkennung und Wahrhaftigkeitsanalyse

Dieses Modul implementiert Fähigkeiten zur Erkennung von:
- Lügen und Täuschungen
- Inkonsistenzen in Aussagen
- Verdächtige Kommunikationsmuster
- Emotionale Diskrepanzen
- Vertrauenswürdigkeitsbewertung

Autor: Holocloude System
Version: 1.0
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set, Any
from enum import Enum
from datetime import datetime
import re
import math
from collections import defaultdict

# ============================================================================
# ENUMS UND TYPEN
# ============================================================================

class DeceptionIndicator(Enum):
    """Indikatoren für mögliche Täuschung"""
    # Verbale Indikatoren
    VAGUE_LANGUAGE = "vague_language"           # Vage Ausdrücke
    EXCESSIVE_DETAIL = "excessive_detail"       # Übermäßige Details
    LACK_OF_DETAIL = "lack_of_detail"           # Mangel an Details
    INCONSISTENCY = "inconsistency"             # Widersprüche
    DISTANCING_LANGUAGE = "distancing_language" # Distanzierende Sprache
    QUALIFIERS = "qualifiers"                   # Abschwächende Wörter
    MEMORY_GAPS = "memory_gaps"                 # Gedächtnislücken
    DEFLECTION = "deflection"                   # Ablenkung
    OVER_EMPHASIS = "over_emphasis"             # Überbetonte Ehrlichkeit

    # Verhaltens-Indikatoren
    DELAYED_RESPONSE = "delayed_response"       # Verzögerte Antwort
    TOPIC_CHANGE = "topic_change"               # Themenwechsel
    EVASION = "evasion"                         # Ausweichen
    DEFENSIVENESS = "defensiveness"             # Defensive Reaktion

    # Emotionale Indikatoren
    EMOTIONAL_MISMATCH = "emotional_mismatch"   # Emotionale Diskrepanz
    FORCED_EMOTION = "forced_emotion"           # Erzwungene Emotion
    MICRO_EXPRESSIONS = "micro_expressions"     # Mikro-Ausdrücke (theoretisch)


class TruthfulnessLevel(Enum):
    """Wahrscheinlichkeitsgrade der Wahrhaftigkeit"""
    HIGHLY_TRUTHFUL = "highly_truthful"     # > 80%
    LIKELY_TRUTHFUL = "likely_truthful"     # 60-80%
    UNCERTAIN = "uncertain"                 # 40-60%
    LIKELY_DECEPTIVE = "likely_deceptive"   # 20-40%
    HIGHLY_DECEPTIVE = "highly_deceptive"   # < 20%


class DeceptionType(Enum):
    """Arten von Täuschung"""
    OUTRIGHT_LIE = "outright_lie"           # Direkte Lüge
    OMISSION = "omission"                   # Auslassung
    HALF_TRUTH = "half_truth"               # Halbwahrheit
    EXAGGERATION = "exaggeration"           # Übertreibung
    MINIMIZATION = "minimization"           # Untertreibung
    MISDIRECTION = "misdirection"           # Irreführung
    EQUIVOCATION = "equivocation"           # Doppeldeutigkeit
    FABRICATION = "fabrication"             # Erfindung


class CredibilityFactor(Enum):
    """Faktoren die Glaubwürdigkeit beeinflussen"""
    CONSISTENCY = "consistency"             # Konsistenz
    PLAUSIBILITY = "plausibility"           # Plausibilität
    SPECIFICITY = "specificity"             # Spezifität
    EMOTION_CONGRUENCE = "emotion_congruence"  # Emotionale Kongruenz
    PAST_RELIABILITY = "past_reliability"   # Vergangene Zuverlässigkeit
    MOTIVE = "motive"                       # Mögliches Motiv


# ============================================================================
# DATENKLASSEN
# ============================================================================

@dataclass
class Statement:
    """Eine Aussage zur Analyse"""
    content: str
    speaker: str
    timestamp: datetime = field(default_factory=datetime.now)
    context: Optional[str] = None
    emotional_tone: Optional[str] = None
    response_time: Optional[float] = None  # Sekunden

    def __hash__(self):
        return hash((self.content, self.speaker, self.timestamp))


@dataclass
class DeceptionSignal:
    """Ein erkanntes Täuschungssignal"""
    indicator: DeceptionIndicator
    evidence: str                   # Was wurde gefunden
    confidence: float               # 0.0 - 1.0
    weight: float                   # Gewicht in Gesamtbewertung
    explanation: str


@dataclass
class InconsistencyReport:
    """Bericht über gefundene Inkonsistenzen"""
    statement1: Statement
    statement2: Statement
    contradiction_type: str
    severity: float                 # 0.0 - 1.0
    explanation: str


@dataclass
class TruthfulnessAssessment:
    """Bewertung der Wahrhaftigkeit"""
    statement: Statement
    truthfulness_score: float       # 0.0 - 1.0
    truthfulness_level: TruthfulnessLevel
    deception_signals: List[DeceptionSignal]
    credibility_factors: Dict[CredibilityFactor, float]
    likely_deception_type: Optional[DeceptionType]
    confidence: float
    reasoning: List[str]

    @property
    def is_likely_deceptive(self) -> bool:
        return self.truthfulness_score < 0.4


@dataclass
class SpeakerProfile:
    """Profil eines Sprechers für Vertrauensbewertung"""
    name: str
    statements_analyzed: int = 0
    truthful_statements: int = 0
    deceptive_statements: int = 0
    average_truthfulness: float = 0.5
    known_motives: List[str] = field(default_factory=list)
    communication_patterns: Dict[str, int] = field(default_factory=dict)
    trust_score: float = 0.5


@dataclass
class ConversationAnalysis:
    """Analyse einer gesamten Konversation"""
    statements: List[Statement]
    assessments: List[TruthfulnessAssessment]
    inconsistencies: List[InconsistencyReport]
    overall_credibility: float
    suspicious_patterns: List[str]
    summary: str


# ============================================================================
# SPRACHMUSTER FÜR TÄUSCHUNGSERKENNUNG
# ============================================================================

DECEPTION_PATTERNS: Dict[DeceptionIndicator, Dict] = {
    DeceptionIndicator.VAGUE_LANGUAGE: {
        "patterns": [
            r"\birgendwie\b", r"\bvielleicht\b", r"\bwohl\b", r"\bungefähr\b",
            r"\bso\s+(?:etwas|etwa|in\s+etwa)\b", r"\bmehr\s+oder\s+weniger\b",
            r"\bkeine\s+ahnung\b", r"\bich\s+glaube\b", r"\bsowas\s+wie\b"
        ],
        "weight": 0.3,
        "explanation": "Vage Ausdrücke können auf Unsicherheit oder Verschleierung hindeuten"
    },
    DeceptionIndicator.EXCESSIVE_DETAIL: {
        "patterns": [
            r"(?:\w+\s+){20,}",  # Sehr lange Sätze
            r"und\s+dann\s+(?:und\s+dann\s+){2,}"  # Repetitive Strukturen
        ],
        "weight": 0.25,
        "explanation": "Übermäßige Details können ein Versuch sein, überzeugender zu wirken"
    },
    DeceptionIndicator.DISTANCING_LANGUAGE: {
        "patterns": [
            r"\bman\b(?!\s+kann)", r"\bjener\b", r"\bjene\b", r"\bdieser\s+mensch\b",
            r"\bdie\s+person\b", r"\bdiese\s+sache\b", r"\bdas\s+ding\b"
        ],
        "weight": 0.35,
        "explanation": "Distanzierende Sprache kann auf emotionale Ablösung von einer Lüge hindeuten"
    },
    DeceptionIndicator.QUALIFIERS: {
        "patterns": [
            r"\behrlich\s+gesagt\b", r"\bum\s+ehrlich\s+zu\s+sein\b",
            r"\bich\s+schwöre\b", r"\bglaub\s+mir\b", r"\bhand\s+aufs\s+herz\b",
            r"\bich\s+würde\s+niemals\s+lügen\b", r"\boffen\s+gesagt\b"
        ],
        "weight": 0.4,
        "explanation": "Übermäßige Betonung der Ehrlichkeit kann auf das Gegenteil hindeuten"
    },
    DeceptionIndicator.MEMORY_GAPS: {
        "patterns": [
            r"\bich\s+(?:kann\s+mich\s+)?nicht\s+(?:mehr\s+)?erinnern\b",
            r"\bich\s+weiß\s+(?:es\s+)?nicht\s+mehr\b",
            r"\bkeine\s+(?:genaue\s+)?erinnerung\b",
            r"\bist\s+(?:mir\s+)?entfallen\b"
        ],
        "weight": 0.3,
        "explanation": "Strategische Gedächtnislücken bei wichtigen Details"
    },
    DeceptionIndicator.DEFLECTION: {
        "patterns": [
            r"\bwarum\s+fragst\s+du\b", r"\bwas\s+soll\s+(?:das|die\s+frage)\b",
            r"\bdas\s+ist\s+(?:doch\s+)?nicht\s+(?:der\s+)?punkt\b",
            r"\bdarum\s+geht\s+es\s+(?:doch\s+)?(?:gar\s+)?nicht\b"
        ],
        "weight": 0.4,
        "explanation": "Ablenkung von der eigentlichen Frage"
    },
    DeceptionIndicator.EVASION: {
        "patterns": [
            r"\bich\s+möchte\s+(?:darüber\s+)?nicht\s+(?:darüber\s+)?sprechen\b",
            r"\bdas\s+geht\s+(?:dich\s+)?nichts\s+an\b",
            r"\bkein\s+kommentar\b", r"\blass\s+(?:uns\s+)?das\s+thema\s+wechseln\b"
        ],
        "weight": 0.35,
        "explanation": "Direktes Ausweichen kann Schuld oder Verheimlichung signalisieren"
    },
    DeceptionIndicator.DEFENSIVENESS: {
        "patterns": [
            r"\bich\s+habe\s+nichts\s+(?:falsches\s+)?getan\b",
            r"\bwarum\s+(?:glaubst\s+du\s+mir|vertraust\s+du\s+mir)\s+nicht\b",
            r"\bich\s+(?:bin|war)\s+(?:es\s+)?nicht\b",
            r"\bwas\s+(?:soll\s+ich|willst\s+du)\s+(?:denn\s+)?(?:noch\s+)?sagen\b"
        ],
        "weight": 0.35,
        "explanation": "Defensive Reaktionen auf neutrale Fragen"
    }
}

# Emotionale Kongruenz-Muster
EMOTION_CONTENT_MAPPING = {
    "positiv": ["freude", "glück", "liebe", "dankbar", "begeistert", "toll", "super"],
    "negativ": ["traurig", "wütend", "ärger", "enttäuscht", "frustriert", "schrecklich"],
    "neutral": ["okay", "normal", "gewöhnlich", "durchschnittlich"]
}


# ============================================================================
# HAUPTKLASSE: DECEPTION DETECTION ENGINE
# ============================================================================

class DeceptionDetectionEngine:
    """
    Engine zur Erkennung von Täuschungen und Lügen.

    Analysiert:
    - Sprachmuster und Formulierungen
    - Konsistenz von Aussagen
    - Emotionale Kongruenz
    - Verhaltens-Indikatoren
    """

    def __init__(self):
        self.speaker_profiles: Dict[str, SpeakerProfile] = {}
        self.statement_history: List[Statement] = []
        self.analysis_history: List[TruthfulnessAssessment] = []
        self.compiled_patterns = self._compile_patterns()

    def _compile_patterns(self) -> Dict[DeceptionIndicator, List[re.Pattern]]:
        """Kompiliert die Regex-Muster für schnellere Analyse"""
        compiled = {}
        for indicator, data in DECEPTION_PATTERNS.items():
            compiled[indicator] = [
                re.compile(pattern, re.IGNORECASE)
                for pattern in data["patterns"]
            ]
        return compiled

    # -------------------------------------------------------------------------
    # Hauptanalyse-Methoden
    # -------------------------------------------------------------------------

    def analyze_statement(
        self,
        statement: Statement,
        context_statements: Optional[List[Statement]] = None
    ) -> TruthfulnessAssessment:
        """
        Analysiert eine einzelne Aussage auf Wahrhaftigkeit.

        Args:
            statement: Die zu analysierende Aussage
            context_statements: Vorherige Aussagen für Konsistenzprüfung

        Returns:
            TruthfulnessAssessment
        """
        # Sammle Täuschungssignale
        signals = self._detect_deception_signals(statement)

        # Prüfe Konsistenz mit vorherigen Aussagen
        inconsistencies = []
        if context_statements:
            inconsistencies = self._check_consistency(statement, context_statements)

        # Analysiere emotionale Kongruenz
        emotion_congruence = self._analyze_emotion_congruence(statement)

        # Berechne Glaubwürdigkeitsfaktoren
        credibility_factors = self._calculate_credibility_factors(
            statement, signals, inconsistencies, emotion_congruence
        )

        # Berechne Gesamtscore
        truthfulness_score = self._calculate_truthfulness_score(
            signals, inconsistencies, credibility_factors
        )

        # Bestimme Level
        truthfulness_level = self._score_to_level(truthfulness_score)

        # Identifiziere wahrscheinlichen Täuschungstyp
        deception_type = self._identify_deception_type(signals, statement) if truthfulness_score < 0.5 else None

        # Generiere Reasoning
        reasoning = self._generate_reasoning(
            signals, inconsistencies, credibility_factors, truthfulness_score
        )

        # Aktualisiere Sprecher-Profil
        self._update_speaker_profile(statement.speaker, truthfulness_score)

        assessment = TruthfulnessAssessment(
            statement=statement,
            truthfulness_score=truthfulness_score,
            truthfulness_level=truthfulness_level,
            deception_signals=signals,
            credibility_factors=credibility_factors,
            likely_deception_type=deception_type,
            confidence=self._calculate_confidence(signals),
            reasoning=reasoning
        )

        # Speichere in History
        self.statement_history.append(statement)
        self.analysis_history.append(assessment)

        return assessment

    def analyze_conversation(
        self,
        statements: List[Statement]
    ) -> ConversationAnalysis:
        """
        Analysiert eine gesamte Konversation.

        Args:
            statements: Liste aller Aussagen in der Konversation

        Returns:
            ConversationAnalysis
        """
        assessments = []
        all_inconsistencies = []

        # Analysiere jede Aussage
        for i, statement in enumerate(statements):
            context = statements[:i] if i > 0 else None
            assessment = self.analyze_statement(statement, context)
            assessments.append(assessment)

        # Suche nach Inkonsistenzen über die gesamte Konversation
        all_inconsistencies = self._find_all_inconsistencies(statements)

        # Identifiziere verdächtige Muster
        suspicious_patterns = self._identify_suspicious_patterns(statements, assessments)

        # Berechne Gesamtglaubwürdigkeit
        overall_credibility = sum(a.truthfulness_score for a in assessments) / len(assessments) if assessments else 0.5

        # Generiere Zusammenfassung
        summary = self._generate_conversation_summary(
            assessments, all_inconsistencies, suspicious_patterns
        )

        return ConversationAnalysis(
            statements=statements,
            assessments=assessments,
            inconsistencies=all_inconsistencies,
            overall_credibility=overall_credibility,
            suspicious_patterns=suspicious_patterns,
            summary=summary
        )

    # -------------------------------------------------------------------------
    # Signal-Erkennung
    # -------------------------------------------------------------------------

    def _detect_deception_signals(self, statement: Statement) -> List[DeceptionSignal]:
        """Erkennt Täuschungssignale in einer Aussage"""
        signals = []
        content = statement.content.lower()

        # Prüfe alle Muster
        for indicator, patterns in self.compiled_patterns.items():
            matches = []
            for pattern in patterns:
                found = pattern.findall(content)
                matches.extend(found)

            if matches:
                data = DECEPTION_PATTERNS[indicator]
                # Mehrere Matches erhöhen Konfidenz
                confidence = min(1.0, 0.5 + len(matches) * 0.15)

                signals.append(DeceptionSignal(
                    indicator=indicator,
                    evidence=", ".join(matches[:3]),
                    confidence=confidence,
                    weight=data["weight"],
                    explanation=data["explanation"]
                ))

        # Prüfe auf verzögerte Antwort
        if statement.response_time and statement.response_time > 3.0:
            signals.append(DeceptionSignal(
                indicator=DeceptionIndicator.DELAYED_RESPONSE,
                evidence=f"Antwortzeit: {statement.response_time:.1f}s",
                confidence=min(1.0, statement.response_time / 10.0),
                weight=0.25,
                explanation="Verzögerte Antworten können auf Nachdenken über Lüge hindeuten"
            ))

        # Prüfe auf emotionale Diskrepanz
        if statement.emotional_tone:
            mismatch = self._check_emotional_mismatch(statement)
            if mismatch:
                signals.append(mismatch)

        return signals

    def _check_emotional_mismatch(self, statement: Statement) -> Optional[DeceptionSignal]:
        """Prüft auf emotionale Diskrepanz"""
        content = statement.content.lower()
        tone = statement.emotional_tone.lower() if statement.emotional_tone else None

        if not tone:
            return None

        # Bestimme Content-Emotion
        content_emotion = "neutral"
        for emotion_type, keywords in EMOTION_CONTENT_MAPPING.items():
            if any(kw in content for kw in keywords):
                content_emotion = emotion_type
                break

        # Vergleiche mit angegebener Emotion
        tone_emotion = "neutral"
        for emotion_type, keywords in EMOTION_CONTENT_MAPPING.items():
            if any(kw in tone for kw in keywords):
                tone_emotion = emotion_type
                break

        # Prüfe auf Diskrepanz
        if content_emotion != tone_emotion and content_emotion != "neutral" and tone_emotion != "neutral":
            return DeceptionSignal(
                indicator=DeceptionIndicator.EMOTIONAL_MISMATCH,
                evidence=f"Inhalt: {content_emotion}, Ton: {tone_emotion}",
                confidence=0.7,
                weight=0.4,
                explanation="Diskrepanz zwischen Inhalt und emotionalem Ton"
            )

        return None

    # -------------------------------------------------------------------------
    # Konsistenzprüfung
    # -------------------------------------------------------------------------

    def _check_consistency(
        self,
        statement: Statement,
        context: List[Statement]
    ) -> List[InconsistencyReport]:
        """Prüft Konsistenz mit vorherigen Aussagen"""
        inconsistencies = []

        # Filtere auf gleichen Sprecher
        speaker_statements = [s for s in context if s.speaker == statement.speaker]

        for prev in speaker_statements:
            contradiction = self._find_contradiction(prev, statement)
            if contradiction:
                inconsistencies.append(contradiction)

        return inconsistencies

    def _find_contradiction(
        self,
        statement1: Statement,
        statement2: Statement
    ) -> Optional[InconsistencyReport]:
        """Sucht nach Widersprüchen zwischen zwei Aussagen"""

        content1 = statement1.content.lower()
        content2 = statement2.content.lower()

        # Einfache Negationssuche
        negation_patterns = [
            (r"ich\s+war\s+(\w+)", r"ich\s+war\s+nicht\s+\1"),
            (r"ich\s+habe\s+(\w+)", r"ich\s+habe\s+(?:\w+\s+)?nicht\s+\1"),
            (r"ich\s+bin\s+(\w+)", r"ich\s+bin\s+nicht\s+\1")
        ]

        for pos_pattern, neg_pattern in negation_patterns:
            pos_match = re.search(pos_pattern, content1)
            neg_match = re.search(neg_pattern, content2)

            if pos_match and neg_match:
                return InconsistencyReport(
                    statement1=statement1,
                    statement2=statement2,
                    contradiction_type="direct_negation",
                    severity=0.8,
                    explanation=f"Direkte Negation: '{pos_match.group()}' vs '{neg_match.group()}'"
                )

            # Auch umgekehrt prüfen
            pos_match = re.search(pos_pattern, content2)
            neg_match = re.search(neg_pattern, content1)

            if pos_match and neg_match:
                return InconsistencyReport(
                    statement1=statement1,
                    statement2=statement2,
                    contradiction_type="direct_negation",
                    severity=0.8,
                    explanation=f"Direkte Negation: '{neg_match.group()}' vs '{pos_match.group()}'"
                )

        # Zeitliche Inkonsistenzen
        time_patterns = [
            (r"gestern", r"vor\s+einer\s+woche"),
            (r"heute\s+morgen", r"gestern\s+abend"),
            (r"letzte\s+woche", r"letzten\s+monat")
        ]

        for time1, time2 in time_patterns:
            if (re.search(time1, content1) and re.search(time2, content2)) or \
               (re.search(time2, content1) and re.search(time1, content2)):
                return InconsistencyReport(
                    statement1=statement1,
                    statement2=statement2,
                    contradiction_type="temporal_inconsistency",
                    severity=0.6,
                    explanation="Widersprüchliche Zeitangaben"
                )

        return None

    def _find_all_inconsistencies(
        self,
        statements: List[Statement]
    ) -> List[InconsistencyReport]:
        """Findet alle Inkonsistenzen in einer Liste von Aussagen"""
        inconsistencies = []

        # Gruppiere nach Sprecher
        speaker_statements: Dict[str, List[Statement]] = defaultdict(list)
        for s in statements:
            speaker_statements[s.speaker].append(s)

        # Prüfe jede Sprecher-Gruppe
        for speaker, stmts in speaker_statements.items():
            for i, s1 in enumerate(stmts):
                for s2 in stmts[i+1:]:
                    contradiction = self._find_contradiction(s1, s2)
                    if contradiction:
                        inconsistencies.append(contradiction)

        return inconsistencies

    # -------------------------------------------------------------------------
    # Glaubwürdigkeitsberechnung
    # -------------------------------------------------------------------------

    def _analyze_emotion_congruence(self, statement: Statement) -> float:
        """Analysiert emotionale Kongruenz"""
        if not statement.emotional_tone:
            return 0.7  # Neutral wenn keine Info

        # Prüfe ob Ton zum Inhalt passt
        content = statement.content.lower()
        tone = statement.emotional_tone.lower()

        # Zähle emotionale Wörter
        positive_count = sum(1 for w in EMOTION_CONTENT_MAPPING["positiv"] if w in content)
        negative_count = sum(1 for w in EMOTION_CONTENT_MAPPING["negativ"] if w in content)

        content_sentiment = positive_count - negative_count
        tone_positive = any(w in tone for w in EMOTION_CONTENT_MAPPING["positiv"])
        tone_negative = any(w in tone for w in EMOTION_CONTENT_MAPPING["negativ"])

        # Berechne Kongruenz
        if (content_sentiment > 0 and tone_positive) or \
           (content_sentiment < 0 and tone_negative) or \
           (content_sentiment == 0):
            return 0.8 + min(0.2, abs(content_sentiment) * 0.05)
        else:
            return 0.4 - min(0.3, abs(content_sentiment) * 0.05)

    def _calculate_credibility_factors(
        self,
        statement: Statement,
        signals: List[DeceptionSignal],
        inconsistencies: List[InconsistencyReport],
        emotion_congruence: float
    ) -> Dict[CredibilityFactor, float]:
        """Berechnet Glaubwürdigkeitsfaktoren"""

        factors = {}

        # Konsistenz
        if not inconsistencies:
            factors[CredibilityFactor.CONSISTENCY] = 0.9
        else:
            avg_severity = sum(i.severity for i in inconsistencies) / len(inconsistencies)
            factors[CredibilityFactor.CONSISTENCY] = max(0.1, 0.9 - avg_severity)

        # Spezifität (längere, detailliertere Aussagen)
        word_count = len(statement.content.split())
        if 10 <= word_count <= 50:
            factors[CredibilityFactor.SPECIFICITY] = 0.7
        elif word_count > 50:
            # Zu viel Detail kann verdächtig sein
            factors[CredibilityFactor.SPECIFICITY] = 0.5
        else:
            factors[CredibilityFactor.SPECIFICITY] = 0.4

        # Emotionale Kongruenz
        factors[CredibilityFactor.EMOTION_CONGRUENCE] = emotion_congruence

        # Plausibilität (basierend auf Signalen)
        deception_weight = sum(s.weight * s.confidence for s in signals)
        factors[CredibilityFactor.PLAUSIBILITY] = max(0.1, 1.0 - deception_weight)

        # Vergangene Zuverlässigkeit des Sprechers
        profile = self.speaker_profiles.get(statement.speaker)
        if profile and profile.statements_analyzed > 0:
            factors[CredibilityFactor.PAST_RELIABILITY] = profile.average_truthfulness
        else:
            factors[CredibilityFactor.PAST_RELIABILITY] = 0.5

        return factors

    def _calculate_truthfulness_score(
        self,
        signals: List[DeceptionSignal],
        inconsistencies: List[InconsistencyReport],
        credibility_factors: Dict[CredibilityFactor, float]
    ) -> float:
        """Berechnet den Gesamtwahrhaftigkeits-Score"""

        # Basiswert
        score = 0.7

        # Abzüge für Täuschungssignale
        for signal in signals:
            score -= signal.weight * signal.confidence * 0.15

        # Abzüge für Inkonsistenzen
        for inc in inconsistencies:
            score -= inc.severity * 0.2

        # Anpassung durch Glaubwürdigkeitsfaktoren
        avg_credibility = sum(credibility_factors.values()) / len(credibility_factors)
        score = score * 0.6 + avg_credibility * 0.4

        return max(0.0, min(1.0, score))

    def _score_to_level(self, score: float) -> TruthfulnessLevel:
        """Konvertiert Score zu Level"""
        if score > 0.8:
            return TruthfulnessLevel.HIGHLY_TRUTHFUL
        elif score > 0.6:
            return TruthfulnessLevel.LIKELY_TRUTHFUL
        elif score > 0.4:
            return TruthfulnessLevel.UNCERTAIN
        elif score > 0.2:
            return TruthfulnessLevel.LIKELY_DECEPTIVE
        else:
            return TruthfulnessLevel.HIGHLY_DECEPTIVE

    def _identify_deception_type(
        self,
        signals: List[DeceptionSignal],
        statement: Statement
    ) -> Optional[DeceptionType]:
        """Identifiziert den wahrscheinlichen Täuschungstyp"""

        # Analysiere dominante Signale
        indicator_counts = defaultdict(float)
        for signal in signals:
            indicator_counts[signal.indicator] += signal.confidence

        if not indicator_counts:
            return None

        dominant = max(indicator_counts.keys(), key=lambda k: indicator_counts[k])

        # Mapping von Indikatoren zu Täuschungstypen
        type_mapping = {
            DeceptionIndicator.VAGUE_LANGUAGE: DeceptionType.EQUIVOCATION,
            DeceptionIndicator.EXCESSIVE_DETAIL: DeceptionType.FABRICATION,
            DeceptionIndicator.LACK_OF_DETAIL: DeceptionType.OMISSION,
            DeceptionIndicator.QUALIFIERS: DeceptionType.MISDIRECTION,
            DeceptionIndicator.MEMORY_GAPS: DeceptionType.OMISSION,
            DeceptionIndicator.DEFLECTION: DeceptionType.MISDIRECTION,
            DeceptionIndicator.EVASION: DeceptionType.OMISSION,
            DeceptionIndicator.DISTANCING_LANGUAGE: DeceptionType.HALF_TRUTH
        }

        return type_mapping.get(dominant, DeceptionType.OUTRIGHT_LIE)

    def _calculate_confidence(self, signals: List[DeceptionSignal]) -> float:
        """Berechnet die Konfidenz in die Analyse"""
        if not signals:
            return 0.5

        # Mehr Signale = höhere Konfidenz (bis zu einem Punkt)
        num_factor = min(1.0, len(signals) / 5.0)
        avg_confidence = sum(s.confidence for s in signals) / len(signals)

        return (num_factor * 0.4 + avg_confidence * 0.6)

    # -------------------------------------------------------------------------
    # Reasoning und Zusammenfassung
    # -------------------------------------------------------------------------

    def _generate_reasoning(
        self,
        signals: List[DeceptionSignal],
        inconsistencies: List[InconsistencyReport],
        credibility_factors: Dict[CredibilityFactor, float],
        score: float
    ) -> List[str]:
        """Generiert die Begründung für die Bewertung"""
        reasoning = []

        # Score-basierte Einleitung
        if score > 0.7:
            reasoning.append("Die Aussage erscheint weitgehend glaubwürdig.")
        elif score > 0.5:
            reasoning.append("Die Aussage zeigt einige Auffälligkeiten.")
        else:
            reasoning.append("Die Aussage zeigt mehrere Täuschungsindikatoren.")

        # Signale erklären
        if signals:
            for signal in sorted(signals, key=lambda s: s.weight, reverse=True)[:3]:
                reasoning.append(f"- {signal.indicator.value}: {signal.explanation}")

        # Inkonsistenzen
        if inconsistencies:
            reasoning.append(f"Es wurden {len(inconsistencies)} Inkonsistenzen gefunden:")
            for inc in inconsistencies[:2]:
                reasoning.append(f"  - {inc.explanation}")

        # Glaubwürdigkeitsfaktoren
        low_factors = [f for f, v in credibility_factors.items() if v < 0.5]
        if low_factors:
            reasoning.append(f"Niedrige Werte bei: {', '.join(f.value for f in low_factors)}")

        return reasoning

    def _identify_suspicious_patterns(
        self,
        statements: List[Statement],
        assessments: List[TruthfulnessAssessment]
    ) -> List[str]:
        """Identifiziert verdächtige Muster in der Konversation"""
        patterns = []

        # Zunehmende Defensive
        defensive_trend = []
        for a in assessments:
            defensive_signals = [s for s in a.deception_signals
                               if s.indicator == DeceptionIndicator.DEFENSIVENESS]
            defensive_trend.append(len(defensive_signals))

        if len(defensive_trend) > 2 and defensive_trend[-1] > defensive_trend[0]:
            patterns.append("Zunehmend defensive Kommunikation")

        # Themenvermeidung
        evasion_count = sum(
            1 for a in assessments
            for s in a.deception_signals
            if s.indicator == DeceptionIndicator.EVASION
        )
        if evasion_count > len(statements) * 0.3:
            patterns.append("Häufiges Ausweichen bei Fragen")

        # Inkonsistenz-Häufung
        deceptive_count = sum(1 for a in assessments if a.is_likely_deceptive)
        if deceptive_count > len(assessments) * 0.5:
            patterns.append("Überdurchschnittlich viele verdächtige Aussagen")

        return patterns

    def _generate_conversation_summary(
        self,
        assessments: List[TruthfulnessAssessment],
        inconsistencies: List[InconsistencyReport],
        patterns: List[str]
    ) -> str:
        """Generiert eine Zusammenfassung der Konversationsanalyse"""

        avg_score = sum(a.truthfulness_score for a in assessments) / len(assessments) if assessments else 0.5

        if avg_score > 0.7:
            summary = "Die Konversation erscheint insgesamt glaubwürdig. "
        elif avg_score > 0.5:
            summary = "Die Konversation zeigt einige Auffälligkeiten. "
        else:
            summary = "Die Konversation zeigt erhebliche Glaubwürdigkeitsprobleme. "

        if inconsistencies:
            summary += f"Es wurden {len(inconsistencies)} Inkonsistenzen gefunden. "

        if patterns:
            summary += f"Verdächtige Muster: {', '.join(patterns)}."

        return summary

    # -------------------------------------------------------------------------
    # Sprecher-Profil
    # -------------------------------------------------------------------------

    def _update_speaker_profile(self, speaker: str, truthfulness_score: float):
        """Aktualisiert das Sprecher-Profil"""
        if speaker not in self.speaker_profiles:
            self.speaker_profiles[speaker] = SpeakerProfile(name=speaker)

        profile = self.speaker_profiles[speaker]
        profile.statements_analyzed += 1

        if truthfulness_score > 0.6:
            profile.truthful_statements += 1
        elif truthfulness_score < 0.4:
            profile.deceptive_statements += 1

        # Gleitender Durchschnitt
        profile.average_truthfulness = (
            profile.average_truthfulness * 0.8 + truthfulness_score * 0.2
        )

        # Trust-Score aktualisieren
        profile.trust_score = profile.average_truthfulness * 0.7 + \
                             (profile.truthful_statements / max(1, profile.statements_analyzed)) * 0.3

    def get_speaker_trust(self, speaker: str) -> float:
        """Gibt den Vertrauenswert für einen Sprecher zurück"""
        profile = self.speaker_profiles.get(speaker)
        return profile.trust_score if profile else 0.5


# ============================================================================
# HILFSFUNKTIONEN
# ============================================================================

def quick_deception_check(text: str, speaker: str = "unknown") -> Dict[str, Any]:
    """
    Schnelle Täuschungsprüfung ohne Engine-Instanz.

    Args:
        text: Der zu prüfende Text
        speaker: Name des Sprechers

    Returns:
        Dict mit Ergebnis
    """
    engine = DeceptionDetectionEngine()
    statement = Statement(content=text, speaker=speaker)
    assessment = engine.analyze_statement(statement)

    return {
        "truthfulness_score": assessment.truthfulness_score,
        "level": assessment.truthfulness_level.value,
        "is_likely_deceptive": assessment.is_likely_deceptive,
        "signals_found": len(assessment.deception_signals),
        "reasoning": assessment.reasoning[:3]
    }


def check_consistency(statements: List[str], speaker: str = "unknown") -> List[str]:
    """
    Prüft Aussagen auf Konsistenz.

    Args:
        statements: Liste von Aussagen
        speaker: Name des Sprechers

    Returns:
        Liste von gefundenen Inkonsistenzen
    """
    engine = DeceptionDetectionEngine()
    statement_objs = [
        Statement(content=s, speaker=speaker)
        for s in statements
    ]

    inconsistencies = engine._find_all_inconsistencies(statement_objs)
    return [i.explanation for i in inconsistencies]


# ============================================================================
# ALIASE FÜR RÜCKWÄRTSKOMPATIBILITÄT
# ============================================================================

# holo_brain.py erwartet diesen Namen
DeceptionDetector = DeceptionDetectionEngine


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Enums
    "DeceptionIndicator",
    "TruthfulnessLevel",
    "DeceptionType",
    "CredibilityFactor",

    # Dataclasses
    "Statement",
    "DeceptionSignal",
    "InconsistencyReport",
    "TruthfulnessAssessment",
    "SpeakerProfile",
    "ConversationAnalysis",

    # Main class
    "DeceptionDetectionEngine",
    "DeceptionDetector",  # Alias

    # Helper functions
    "quick_deception_check",
    "check_consistency",

    # Constants
    "DECEPTION_PATTERNS"
]
