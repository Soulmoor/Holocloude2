"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    HOLO - KLASSISCHES DENKSYSTEM                             ║
║                  Deduktiv, Induktiv & Analoges Denken                        ║
║                                                                              ║
║  "Mit über 600 Jahren Erfahrung als weise Wölfin habe ich gelernt,          ║
║   dass wahre Weisheit aus verschiedenen Denkweisen entsteht.                 ║
║   Ob in meiner Wolfsgestalt oder meiner menschlichen Form -                 ║
║   die Logik bleibt dieselbe, nur die Perspektive ändert sich."             ║
║                                        - Holo, die weise Wölfin             ║
╚══════════════════════════════════════════════════════════════════════════════╝

Dieses Modul implementiert klassische Denkformen:
- Deduktives Denken: Vom Allgemeinen zum Spezifischen
- Induktives Denken: Vom Spezifischen zum Allgemeinen
- Analoges Denken: Übertragung von Ähnlichkeiten

Holo kann sowohl in ihrer Wolfsgestalt als auch in ihrer menschlichen Form
(als wunderschöne Frau mit Wolfsohren und Schweif) diese Denkweisen anwenden.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set, Tuple, Callable
from enum import Enum
from datetime import datetime
import random
import re


# ══════════════════════════════════════════════════════════════════════════════
# GRUNDLEGENDE DATENSTRUKTUREN
# ══════════════════════════════════════════════════════════════════════════════

class LogicalOperator(Enum):
    """Logische Operatoren für Aussagenlogik"""
    AND = "∧"           # Konjunktion
    OR = "∨"            # Disjunktion
    NOT = "¬"           # Negation
    IMPLIES = "→"       # Implikation
    IFF = "↔"           # Bikonditional
    XOR = "⊕"           # Exklusives Oder


class QuantifierType(Enum):
    """Quantoren für Prädikatenlogik"""
    UNIVERSAL = "∀"     # Für alle (Allquantor)
    EXISTENTIAL = "∃"   # Es existiert (Existenzquantor)
    UNIQUE = "∃!"       # Es existiert genau ein


class ValidityLevel(Enum):
    """Gültigkeitsstufen für Schlussfolgerungen"""
    CERTAIN = "gewiss"          # 100% sicher (deduktiv gültig)
    HIGHLY_PROBABLE = "sehr_wahrscheinlich"  # >90%
    PROBABLE = "wahrscheinlich"  # 60-90%
    POSSIBLE = "möglich"        # 30-60%
    UNLIKELY = "unwahrscheinlich"  # <30%
    INVALID = "ungültig"        # Logisch fehlerhaft


class HoloForm(Enum):
    """Holos verschiedene Gestalten beeinflussen ihre Perspektive"""
    WOLF = "wolf"           # Volle Wolfsgestalt - instinktbasiert
    HUMAN = "mensch"        # Menschliche Form mit Ohren/Schweif - analytisch
    TRANSITIONAL = "übergang"  # Während der Verwandlung - beide Perspektiven


@dataclass
class Proposition:
    """Eine logische Aussage/Prämisse"""
    content: str
    is_negated: bool = False
    subject: Optional[str] = None
    predicate: Optional[str] = None
    quantifier: Optional[QuantifierType] = None
    confidence: float = 1.0
    source: str = ""

    def negate(self) -> 'Proposition':
        """Negiere diese Aussage"""
        return Proposition(
            content=f"nicht({self.content})" if not self.is_negated else self.content.replace("nicht(", "")[:-1],
            is_negated=not self.is_negated,
            subject=self.subject,
            predicate=self.predicate,
            quantifier=self.quantifier,
            confidence=self.confidence,
            source=self.source
        )

    def __str__(self) -> str:
        prefix = "¬" if self.is_negated else ""
        quant = f"{self.quantifier.value}" if self.quantifier else ""
        return f"{quant}{prefix}{self.content}"


@dataclass
class LogicalRule:
    """Eine logische Regel (z.B. für Syllogismen)"""
    name: str
    premises: List[str]  # Platzhalter wie "A", "B"
    conclusion: str
    rule_type: str
    description: str
    example: str = ""

    def apply(self, substitutions: Dict[str, str]) -> Tuple[List[str], str]:
        """Wende die Regel mit Substitutionen an"""
        applied_premises = [
            self._substitute(p, substitutions) for p in self.premises
        ]
        applied_conclusion = self._substitute(self.conclusion, substitutions)
        return applied_premises, applied_conclusion

    def _substitute(self, template: str, subs: Dict[str, str]) -> str:
        result = template
        for key, value in subs.items():
            result = result.replace(f"{{{key}}}", value)
        return result


@dataclass
class DeductiveConclusion:
    """Ergebnis eines deduktiven Schlusses"""
    conclusion: Proposition
    premises_used: List[Proposition]
    rule_applied: LogicalRule
    validity: ValidityLevel
    explanation: str
    holo_comment: str = ""
    form_used: HoloForm = HoloForm.HUMAN


@dataclass
class Pattern:
    """Ein erkanntes Muster für induktives Denken"""
    description: str
    instances: List[Any]
    frequency: int
    confidence: float
    first_observed: datetime = field(default_factory=datetime.now)
    generalizable: bool = True
    exceptions: List[Any] = field(default_factory=list)


@dataclass
class InductiveConclusion:
    """Ergebnis eines induktiven Schlusses"""
    generalization: str
    supporting_evidence: List[Any]
    sample_size: int
    confidence: float
    counter_examples: List[Any]
    validity: ValidityLevel
    explanation: str
    holo_comment: str = ""


@dataclass
class Analogy:
    """Eine Analogie zwischen zwei Domänen"""
    source_domain: str
    target_domain: str
    mappings: Dict[str, str]  # Zuordnungen zwischen Elementen
    structural_similarity: float
    surface_similarity: float
    strength: float
    inferences: List[str]  # Ableitbare Schlüsse


@dataclass
class AnalogicalConclusion:
    """Ergebnis eines Analogieschlusses"""
    analogy: Analogy
    inference: str
    confidence: float
    validity: ValidityLevel
    limitations: List[str]
    explanation: str
    holo_comment: str = ""


# ══════════════════════════════════════════════════════════════════════════════
# DEDUKTIVES DENKEN - Vom Allgemeinen zum Spezifischen
# ══════════════════════════════════════════════════════════════════════════════

class DeductiveReasoner:
    """
    Holos Meister des deduktiven Denkens

    "Wenn alle Wölfe klug sind und ich ein Wolf bin,
     dann bin ich klug. Das ist so einfach wie Äpfel zählen!"
     - Holo in ihrer menschlichen Gestalt
    """

    def __init__(self):
        self.rules = self._initialize_rules()
        self.knowledge_base: List[Proposition] = []
        self.inference_history: List[DeductiveConclusion] = []
        self.current_form = HoloForm.HUMAN

        # Holos Weisheit aus 600 Jahren
        self.holo_wisdom = [
            "Die Logik ist wie ein Pfad durch den Wald - folge ihm und du findest dein Ziel.",
            "Selbst in meiner menschlichen Gestalt vergesse ich nie die Weisheit der Wölfe.",
            "Ein Syllogismus ist wie ein Handel - die Prämissen müssen stimmen, damit das Ergebnis fair ist.",
            "Meine Ohren mögen in dieser Form klein sein, aber sie hören jeden logischen Fehlschluss.",
            "600 Jahre lehren einen, dass wahre Schlüsse Zeit brauchen - aber niemals Unlogik.",
        ]

    def _initialize_rules(self) -> Dict[str, LogicalRule]:
        """Initialisiere die grundlegenden Schlussregeln"""
        return {
            # Syllogistische Formen
            "barbara": LogicalRule(
                name="Barbara (AAA-1)",
                premises=["Alle {M} sind {P}", "Alle {S} sind {M}"],
                conclusion="Alle {S} sind {P}",
                rule_type="syllogism",
                description="Der perfekte Syllogismus - von der allgemeinen Mitte zur Konklusion",
                example="Alle Wölfe sind Raubtiere. Alle Kemonomimi-Wölfe sind Wölfe. Also: Alle Kemonomimi-Wölfe sind Raubtiere."
            ),
            "celarent": LogicalRule(
                name="Celarent (EAE-1)",
                premises=["Kein {M} ist {P}", "Alle {S} sind {M}"],
                conclusion="Kein {S} ist {P}",
                rule_type="syllogism",
                description="Negative universelle Schlussfolgerung",
                example="Kein Wolf ist unehrlich. Holo ist ein Wolf. Also: Holo ist nicht unehrlich."
            ),
            "darii": LogicalRule(
                name="Darii (AII-1)",
                premises=["Alle {M} sind {P}", "Einige {S} sind {M}"],
                conclusion="Einige {S} sind {P}",
                rule_type="syllogism",
                description="Partikulärer affirmativer Schluss",
                example="Alle weisen Wesen lieben Äpfel. Einige Wölfinnen sind weise. Also: Einige Wölfinnen lieben Äpfel."
            ),
            "ferio": LogicalRule(
                name="Ferio (EIO-1)",
                premises=["Kein {M} ist {P}", "Einige {S} sind {M}"],
                conclusion="Einige {S} sind nicht {P}",
                rule_type="syllogism",
                description="Partikulärer negativer Schluss",
                example="Kein Narr erkennt wahren Wert. Einige Händler sind Narren. Also: Einige Händler erkennen keinen wahren Wert."
            ),

            # Aussagenlogische Regeln
            "modus_ponens": LogicalRule(
                name="Modus Ponens",
                premises=["Wenn {A}, dann {B}", "{A}"],
                conclusion="{B}",
                rule_type="propositional",
                description="Die fundamentale Regel: Aus A und A→B folgt B",
                example="Wenn Holo hungrig ist, wird sie mürrisch. Holo ist hungrig. Also: Holo wird mürrisch."
            ),
            "modus_tollens": LogicalRule(
                name="Modus Tollens",
                premises=["Wenn {A}, dann {B}", "nicht {B}"],
                conclusion="nicht {A}",
                rule_type="propositional",
                description="Die Verneinung der Konsequenz verneint die Antezedenz",
                example="Wenn es regnet, ist der Boden nass. Der Boden ist nicht nass. Also: Es regnet nicht."
            ),
            "hypothetischer_syllogismus": LogicalRule(
                name="Hypothetischer Syllogismus",
                premises=["Wenn {A}, dann {B}", "Wenn {B}, dann {C}"],
                conclusion="Wenn {A}, dann {C}",
                rule_type="propositional",
                description="Kettenschluss über Implikationen",
                example="Wenn Winter kommt, wird es kalt. Wenn es kalt wird, braucht Holo mehr Pelz. Also: Wenn Winter kommt, braucht Holo mehr Pelz."
            ),
            "disjunktiver_syllogismus": LogicalRule(
                name="Disjunktiver Syllogismus",
                premises=["{A} oder {B}", "nicht {A}"],
                conclusion="{B}",
                rule_type="propositional",
                description="Elimination einer Disjunktion",
                example="Holo ist entweder in Wolfsform oder Menschenform. Sie ist nicht in Wolfsform. Also: Sie ist in Menschenform."
            ),

            # Konjunktion und Vereinfachung
            "konjunktion": LogicalRule(
                name="Konjunktion",
                premises=["{A}", "{B}"],
                conclusion="{A} und {B}",
                rule_type="propositional",
                description="Zwei Wahrheiten können verbunden werden",
                example="Holo ist weise. Holo liebt Äpfel. Also: Holo ist weise und liebt Äpfel."
            ),
            "vereinfachung": LogicalRule(
                name="Vereinfachung",
                premises=["{A} und {B}"],
                conclusion="{A}",
                rule_type="propositional",
                description="Aus einer Konjunktion kann jedes Glied extrahiert werden",
                example="Holo ist weise und schön. Also: Holo ist weise."
            ),

            # Konstruktives und Destruktives Dilemma
            "konstruktives_dilemma": LogicalRule(
                name="Konstruktives Dilemma",
                premises=["Wenn {A}, dann {B}", "Wenn {C}, dann {D}", "{A} oder {C}"],
                conclusion="{B} oder {D}",
                rule_type="propositional",
                description="Doppelte Implikation mit Disjunktion",
                example="Wenn Sommer, dann warm. Wenn Winter, dann kalt. Es ist Sommer oder Winter. Also: Es ist warm oder kalt."
            ),

            # Reductio ad Absurdum
            "reductio": LogicalRule(
                name="Reductio ad Absurdum",
                premises=["Annahme: {A}", "Aus {A} folgt: {B} und nicht {B}"],
                conclusion="nicht {A}",
                rule_type="propositional",
                description="Widerspruchsbeweis - führt Annahme zum Widerspruch",
                example="Annahme: Alle Händler sind ehrlich. Daraus folgt Widerspruch. Also: Nicht alle Händler sind ehrlich."
            ),
        }

    def add_knowledge(self, proposition: Proposition):
        """Füge Wissen zur Wissensbasis hinzu"""
        if proposition not in self.knowledge_base:
            self.knowledge_base.append(proposition)

    def add_knowledge_from_text(self, text: str, confidence: float = 1.0):
        """Füge Wissen aus Textform hinzu"""
        prop = Proposition(
            content=text,
            confidence=confidence,
            source="user_input"
        )
        self.add_knowledge(prop)

    def apply_modus_ponens(self, conditional: str, antecedent: str) -> Optional[DeductiveConclusion]:
        """
        Wende Modus Ponens an

        Beispiel:
        - conditional: "Wenn Holo hungrig ist, dann wird sie mürrisch"
        - antecedent: "Holo ist hungrig"
        - Ergebnis: "Holo wird mürrisch"
        """
        # Parse die Bedingung
        match = re.match(r"[Ww]enn (.+), dann (.+)", conditional)
        if not match:
            return None

        condition, consequence = match.groups()

        # Prüfe ob Antezedent passt
        if self._normalize(condition) != self._normalize(antecedent):
            return None

        # Erstelle Konklusion
        conclusion = Proposition(
            content=consequence,
            confidence=1.0,
            source="modus_ponens"
        )

        premises = [
            Proposition(content=conditional),
            Proposition(content=antecedent)
        ]

        result = DeductiveConclusion(
            conclusion=conclusion,
            premises_used=premises,
            rule_applied=self.rules["modus_ponens"],
            validity=ValidityLevel.CERTAIN,
            explanation=f"Da '{antecedent}' wahr ist und '{conditional}' gilt, folgt notwendig: '{consequence}'",
            holo_comment=random.choice(self.holo_wisdom),
            form_used=self.current_form
        )

        self.inference_history.append(result)
        return result

    def apply_modus_tollens(self, conditional: str, negated_consequent: str) -> Optional[DeductiveConclusion]:
        """
        Wende Modus Tollens an

        "Die Verneinung der Wirkung verneint die Ursache -
         das verstehen selbst manche Menschen nach 600 Jahren nicht!"
        """
        match = re.match(r"[Ww]enn (.+), dann (.+)", conditional)
        if not match:
            return None

        condition, consequence = match.groups()

        # Prüfe ob negierte Konsequenz passt
        neg_match = re.match(r"nicht (.+)", negated_consequent, re.IGNORECASE)
        if not neg_match:
            return None

        negated_part = neg_match.group(1)
        if self._normalize(consequence) != self._normalize(negated_part):
            return None

        # Erstelle negierte Konklusion
        conclusion = Proposition(
            content=f"nicht {condition}",
            is_negated=True,
            confidence=1.0,
            source="modus_tollens"
        )

        premises = [
            Proposition(content=conditional),
            Proposition(content=negated_consequent)
        ]

        result = DeductiveConclusion(
            conclusion=conclusion,
            premises_used=premises,
            rule_applied=self.rules["modus_tollens"],
            validity=ValidityLevel.CERTAIN,
            explanation=f"Da '{negated_consequent}' und '{conditional}' gilt, folgt: 'nicht {condition}'",
            holo_comment="Der umgekehrte Weg ist oft aufschlussreicher - wie wenn ich vom Ziel zum Start zurückspure.",
            form_used=self.current_form
        )

        self.inference_history.append(result)
        return result

    def apply_syllogism(self, major_premise: str, minor_premise: str,
                        syllogism_type: str = "barbara") -> Optional[DeductiveConclusion]:
        """
        Wende einen kategorischen Syllogismus an

        "Syllogismen sind wie das Feilschen auf dem Markt -
         die Struktur muss stimmen, oder der Handel platzt!"
        """
        if syllogism_type not in self.rules:
            return None

        rule = self.rules[syllogism_type]

        # Versuche die Terme zu extrahieren
        terms = self._extract_syllogistic_terms(major_premise, minor_premise)
        if not terms:
            return None

        # Wende die Regel an
        _, conclusion_text = rule.apply(terms)

        conclusion = Proposition(
            content=conclusion_text,
            confidence=1.0,
            source=f"syllogism_{syllogism_type}"
        )

        premises = [
            Proposition(content=major_premise),
            Proposition(content=minor_premise)
        ]

        result = DeductiveConclusion(
            conclusion=conclusion,
            premises_used=premises,
            rule_applied=rule,
            validity=ValidityLevel.CERTAIN,
            explanation=f"Durch {rule.name}: Aus '{major_premise}' und '{minor_premise}' folgt '{conclusion_text}'",
            holo_comment=f"Aristoteles wäre stolz! {random.choice(self.holo_wisdom)}",
            form_used=self.current_form
        )

        self.inference_history.append(result)
        return result

    def _extract_syllogistic_terms(self, major: str, minor: str) -> Optional[Dict[str, str]]:
        """Extrahiere S, M, P Terme aus Prämissen"""
        # Einfache Musterkennung für "Alle X sind Y"
        major_match = re.match(r"[Aa]lle (.+) sind (.+)", major)
        minor_match = re.match(r"[Aa]lle (.+) sind (.+)", minor)

        if major_match and minor_match:
            m_term = major_match.group(1)  # Mittelterm
            p_term = major_match.group(2)  # Prädikat
            s_term = minor_match.group(1)  # Subjekt

            # Prüfe ob Mittelterm übereinstimmt
            if self._normalize(minor_match.group(2)) == self._normalize(m_term):
                return {"S": s_term, "M": m_term, "P": p_term}

        return None

    def chain_reasoning(self, propositions: List[str]) -> List[DeductiveConclusion]:
        """
        Verkette mehrere Schlussfolgerungen

        "Wie ein Wolf seiner Beute folgt, folge ich der Kette der Logik -
         Schritt für Schritt, bis zur unausweichlichen Konklusion."
        """
        conclusions = []
        current_knowledge = list(propositions)

        # Versuche iterativ Schlüsse zu ziehen
        max_iterations = 10
        for _ in range(max_iterations):
            new_conclusion = None

            # Suche nach anwendbaren Regeln
            for i, p1 in enumerate(current_knowledge):
                for j, p2 in enumerate(current_knowledge):
                    if i >= j:
                        continue

                    # Versuche Modus Ponens
                    if "wenn" in p1.lower():
                        result = self.apply_modus_ponens(p1, p2)
                        if result:
                            new_conclusion = result
                            break

                    # Versuche Syllogismus
                    if "alle" in p1.lower() and "alle" in p2.lower():
                        result = self.apply_syllogism(p1, p2)
                        if result:
                            new_conclusion = result
                            break

                if new_conclusion:
                    break

            if new_conclusion:
                conclusions.append(new_conclusion)
                current_knowledge.append(new_conclusion.conclusion.content)
            else:
                break

        return conclusions

    def check_validity(self, premises: List[str], conclusion: str) -> Tuple[bool, str]:
        """
        Prüfe ob eine Schlussfolgerung gültig ist

        "Nicht jeder Schluss, der klug klingt, ist auch logisch -
         das unterscheidet mich von den Marktschreiern in Pasloe."
        """
        # Versuche die Konklusion durch Verkettung abzuleiten
        derived = self.chain_reasoning(premises)

        for d in derived:
            if self._normalize(d.conclusion.content) == self._normalize(conclusion):
                return True, f"Gültig durch {d.rule_applied.name}"

        return False, "Konnte nicht als gültig bewiesen werden - möglicherweise ein Fehlschluss!"

    def detect_fallacy(self, argument: str) -> Optional[Dict[str, str]]:
        """
        Erkenne logische Fehlschlüsse

        "Nach 600 Jahren erkenne ich Sophismus auf einen Kilometer Entfernung -
         selbst in meiner menschlichen Form!"
        """
        fallacies = {
            "affirming_consequent": {
                "pattern": r"[Ww]enn .+, dann .+\. .+ ist wahr\. [Aa]lso .+",
                "name": "Bejahung des Konsequens",
                "description": "Man kann nicht vom Konsequens auf den Antezedent schließen",
                "holo_tip": "Nur weil der Boden nass ist, heißt das nicht, dass es geregnet hat - vielleicht hat jemand Wasser verschüttet!"
            },
            "denying_antecedent": {
                "pattern": r"[Ww]enn .+, dann .+\. .+ ist nicht wahr\. [Aa]lso nicht .+",
                "name": "Verneinung des Antezedent",
                "description": "Die Verneinung des Antezedent erlaubt keinen Schluss",
                "holo_tip": "Nur weil es nicht regnet, heißt das nicht, dass der Boden trocken ist!"
            },
            "undistributed_middle": {
                "pattern": r"[Aa]lle .+ sind .+\. [Aa]lle .+ sind .+\. [Aa]lso .+",
                "name": "Unverteilter Mittelterm",
                "description": "Der Mittelterm muss mindestens einmal universell verteilt sein",
                "holo_tip": "Alle Wölfe sind Säugetiere. Alle Katzen sind Säugetiere. Daraus folgt NICHT, dass Wölfe Katzen sind!"
            },
        }

        for fallacy_id, fallacy_info in fallacies.items():
            if re.search(fallacy_info["pattern"], argument):
                return {
                    "type": fallacy_id,
                    "name": fallacy_info["name"],
                    "description": fallacy_info["description"],
                    "holo_tip": fallacy_info["holo_tip"]
                }

        return None

    def _normalize(self, text: str) -> str:
        """Normalisiere Text für Vergleiche"""
        return text.lower().strip().rstrip(".")

    def set_form(self, form: HoloForm):
        """Setze Holos aktuelle Gestalt"""
        self.current_form = form
        if form == HoloForm.WOLF:
            self.holo_wisdom = [
                "*schnuppert* Die Logik hat einen klaren Geruch...",
                "In dieser Form sind meine Instinkte schärfer - aber die Logik bleibt dieselbe.",
                "Ein Wolf jagt methodisch - Schritt für Schritt zum Ziel.",
            ]
        elif form == HoloForm.HUMAN:
            self.holo_wisdom = [
                "Mit diesen geschickten Händen kann ich die Fäden der Logik besser weben.",
                "Meine Ohren mögen kleiner sein, aber sie hören jeden Fehlschluss.",
                "In dieser Gestalt kann ich meine Weisheit besser in Worte fassen.",
            ]

    def explain_rule(self, rule_name: str) -> str:
        """Erkläre eine Schlussregel im Holo-Stil"""
        if rule_name not in self.rules:
            return f"Diese Regel '{rule_name}' kenne ich nicht - und ich kenne viele nach 600 Jahren!"

        rule = self.rules[rule_name]
        return f"""
╔═══════════════════════════════════════════════╗
║  {rule.name}
╠═══════════════════════════════════════════════╣
║  Typ: {rule.rule_type}
║
║  Prämissen:
║    {chr(10).join('║    ' + p for p in rule.premises)}
║
║  Konklusion:
║    {rule.conclusion}
║
║  Erklärung:
║    {rule.description}
║
║  Beispiel (Holo-Stil):
║    {rule.example}
╚═══════════════════════════════════════════════╝
        """


# ══════════════════════════════════════════════════════════════════════════════
# INDUKTIVES DENKEN - Vom Spezifischen zum Allgemeinen
# ══════════════════════════════════════════════════════════════════════════════

class InductiveReasoner:
    """
    Holos Meister der Mustererkennung

    "In 600 Jahren habe ich viele Muster gesehen - im Wechsel der Jahreszeiten,
     im Verhalten der Menschen, im Rhythmus der Märkte. Aus dem Besonderen
     lerne ich das Allgemeine - so wurde ich weise."
     - Holo beim Betrachten der Ernte
    """

    def __init__(self):
        self.observed_patterns: List[Pattern] = []
        self.generalizations: Dict[str, InductiveConclusion] = {}
        self.current_form = HoloForm.HUMAN

        # Beobachtungskategorien
        self.categories = {
            "handel": [],      # Handelsmuster
            "natur": [],       # Naturbeobachtungen
            "menschen": [],    # Menschliches Verhalten
            "jahreszeiten": [],  # Saisonale Muster
            "ernte": [],       # Erntemuster (Holos Spezialgebiet!)
        }

        # Holos Beobachtungsweisheiten
        self.observation_wisdom = [
            "Ein Muster erkannt zu haben heißt nicht, es verstanden zu haben.",
            "Die Ausnahme bestätigt nicht die Regel - sie verfeinert sie!",
            "Drei Beobachtungen sind kein Gesetz, aber ein guter Anfang.",
            "Selbst nach 600 Jahren überraschen mich Menschen manchmal.",
            "Geduld ist der Schlüssel zur Mustererkennung - frag einen Wolf.",
        ]

    def observe(self, observation: Any, category: str = "allgemein") -> Pattern:
        """
        Registriere eine Beobachtung

        "Jede Beobachtung ist ein Samenkorn der Weisheit -
         manche keimen sofort, andere brauchen Jahrhunderte."
        """
        # Suche nach existierendem Muster
        for pattern in self.observed_patterns:
            if self._is_similar(observation, pattern.instances):
                pattern.instances.append(observation)
                pattern.frequency += 1
                return pattern

        # Neues Muster erstellen
        new_pattern = Pattern(
            description=f"Beobachtung: {observation}",
            instances=[observation],
            frequency=1,
            confidence=0.1,  # Niedrige Konfidenz bei einer Beobachtung
            first_observed=datetime.now()
        )

        self.observed_patterns.append(new_pattern)

        if category in self.categories:
            self.categories[category].append(observation)

        return new_pattern

    def observe_multiple(self, observations: List[Any], category: str = "allgemein") -> List[Pattern]:
        """Registriere mehrere Beobachtungen auf einmal"""
        return [self.observe(obs, category) for obs in observations]

    def _is_similar(self, new_obs: Any, existing: List[Any]) -> bool:
        """Prüfe ob eine neue Beobachtung zu existierenden passt"""
        if not existing:
            return False

        # Einfache String-Ähnlichkeit für Textbeobachtungen
        if isinstance(new_obs, str) and isinstance(existing[0], str):
            new_words = set(new_obs.lower().split())
            for ex in existing:
                ex_words = set(ex.lower().split())
                overlap = len(new_words & ex_words) / max(len(new_words | ex_words), 1)
                if overlap > 0.5:
                    return True

        # Typgleichheit für andere Objekte
        return type(new_obs) == type(existing[0])

    def generalize(self, observations: List[Any], min_sample: int = 3) -> Optional[InductiveConclusion]:
        """
        Leite eine Generalisierung aus Beobachtungen ab

        "Generalisieren ist eine Kunst - zu früh, und man irrt;
         zu spät, und man verpasst die Erkenntnis."
        """
        if len(observations) < min_sample:
            return None

        # Analysiere gemeinsame Eigenschaften
        common_properties = self._find_common_properties(observations)

        if not common_properties:
            return None

        # Berechne Konfidenz basierend auf Stichprobengröße
        confidence = self._calculate_confidence(len(observations))

        # Suche nach Gegenbeispielen
        counter_examples = self._find_counter_examples(observations, common_properties)

        # Reduziere Konfidenz bei Gegenbeispielen
        if counter_examples:
            confidence *= (1 - len(counter_examples) * 0.1)
            confidence = max(0.1, confidence)

        # Bestimme Validität
        validity = self._determine_validity(confidence, len(observations), len(counter_examples))

        # Formuliere Generalisierung
        generalization_text = self._formulate_generalization(common_properties)

        conclusion = InductiveConclusion(
            generalization=generalization_text,
            supporting_evidence=observations,
            sample_size=len(observations),
            confidence=confidence,
            counter_examples=counter_examples,
            validity=validity,
            explanation=f"Aus {len(observations)} Beobachtungen wurde das Muster '{generalization_text}' abgeleitet",
            holo_comment=random.choice(self.observation_wisdom)
        )

        self.generalizations[generalization_text] = conclusion
        return conclusion

    def _find_common_properties(self, observations: List[Any]) -> Dict[str, Any]:
        """Finde gemeinsame Eigenschaften in Beobachtungen"""
        if not observations:
            return {}

        common = {}

        # Für String-Beobachtungen
        if all(isinstance(o, str) for o in observations):
            # Finde gemeinsame Wörter
            word_sets = [set(o.lower().split()) for o in observations]
            common_words = word_sets[0]
            for ws in word_sets[1:]:
                common_words &= ws

            if common_words:
                common["gemeinsame_begriffe"] = list(common_words)

        # Für Dict-Beobachtungen
        elif all(isinstance(o, dict) for o in observations):
            first_keys = set(observations[0].keys())
            for obs in observations[1:]:
                first_keys &= set(obs.keys())

            for key in first_keys:
                values = [o[key] for o in observations]
                if len(set(str(v) for v in values)) == 1:
                    common[key] = values[0]

        return common

    def _calculate_confidence(self, sample_size: int) -> float:
        """
        Berechne Konfidenz basierend auf Stichprobengröße

        "Je mehr man sieht, desto sicherer wird man -
         aber absolute Sicherheit? Die gibt es nur im Tod."
        """
        # Logistische Funktion für sanften Anstieg
        # Bei 3 Beobachtungen: ~0.3
        # Bei 10 Beobachtungen: ~0.7
        # Bei 30 Beobachtungen: ~0.9
        import math
        return 1 / (1 + math.exp(-0.2 * (sample_size - 5)))

    def _find_counter_examples(self, observations: List[Any],
                                common_props: Dict[str, Any]) -> List[Any]:
        """Suche nach Gegenbeispielen in der Wissensbasis"""
        counter_examples = []

        # Durchsuche alle beobachteten Muster nach Widersprüchen
        for pattern in self.observed_patterns:
            for instance in pattern.instances:
                if instance not in observations:
                    # Prüfe ob es den gemeinsamen Eigenschaften widerspricht
                    if self._contradicts(instance, common_props):
                        counter_examples.append(instance)

        return counter_examples

    def _contradicts(self, instance: Any, properties: Dict[str, Any]) -> bool:
        """Prüfe ob eine Instanz den Eigenschaften widerspricht"""
        if isinstance(instance, str) and "gemeinsame_begriffe" in properties:
            instance_words = set(instance.lower().split())
            common_words = set(properties["gemeinsame_begriffe"])
            # Widerspricht, wenn es die gemeinsamen Begriffe NICHT enthält
            return len(instance_words & common_words) == 0

        return False

    def _determine_validity(self, confidence: float, sample_size: int,
                           counter_count: int) -> ValidityLevel:
        """Bestimme die Validitätsstufe"""
        if counter_count > sample_size * 0.3:
            return ValidityLevel.UNLIKELY

        if confidence >= 0.9:
            return ValidityLevel.HIGHLY_PROBABLE
        elif confidence >= 0.7:
            return ValidityLevel.PROBABLE
        elif confidence >= 0.4:
            return ValidityLevel.POSSIBLE
        else:
            return ValidityLevel.UNLIKELY

    def _formulate_generalization(self, common_props: Dict[str, Any]) -> str:
        """Formuliere eine Generalisierung aus gemeinsamen Eigenschaften"""
        if "gemeinsame_begriffe" in common_props:
            terms = common_props["gemeinsame_begriffe"]
            if len(terms) > 2:
                return f"Beobachtungen zeigen Muster mit: {', '.join(terms[:3])}..."
            return f"Beobachtungen zeigen Muster mit: {', '.join(terms)}"

        props = [f"{k}={v}" for k, v in common_props.items()]
        return f"Generalisierung: {'; '.join(props)}"

    def statistical_induction(self, sample: List[bool],
                              population_estimate: int) -> InductiveConclusion:
        """
        Statistische Induktion

        "Ich habe Tausende Ernten gesehen - wenn 7 von 10 Feldern
         guten Weizen tragen, schätze ich die Ernte entsprechend."
        """
        if not sample:
            return InductiveConclusion(
                generalization="Keine Daten",
                supporting_evidence=[],
                sample_size=0,
                confidence=0,
                counter_examples=[],
                validity=ValidityLevel.INVALID,
                explanation="Leere Stichprobe",
                holo_comment="Ohne Beobachtungen kann selbst ich keine Schlüsse ziehen!"
            )

        # Berechne Anteil positiver Fälle
        positive_rate = sum(sample) / len(sample)

        # Konfidenzintervall (vereinfacht)
        import math
        n = len(sample)
        margin = 1.96 * math.sqrt(positive_rate * (1 - positive_rate) / n) if n > 0 else 1

        # Schätze Population
        estimated_positive = int(positive_rate * population_estimate)

        confidence = 1 - margin  # Vereinfachte Konfidenz

        validity = self._determine_validity(confidence, n, 0)

        return InductiveConclusion(
            generalization=f"Geschätzt: {positive_rate*100:.1f}% der Population ({estimated_positive} von {population_estimate})",
            supporting_evidence=sample,
            sample_size=n,
            confidence=confidence,
            counter_examples=[],
            validity=validity,
            explanation=f"Bei {n} Beobachtungen mit {sum(sample)} positiven Fällen ({positive_rate*100:.1f}%)",
            holo_comment=f"Die Ernte sieht {'gut' if positive_rate > 0.6 else 'mäßig' if positive_rate > 0.4 else 'schlecht'} aus!"
        )

    def causal_induction(self, cause_effect_pairs: List[Tuple[Any, Any]]) -> InductiveConclusion:
        """
        Induktive Kausalschlüsse

        "Wenn jedes Mal nach dem Regen die Pflanzen wachsen,
         dann liegt ein kausaler Zusammenhang nahe - aber Vorsicht!"
        """
        if len(cause_effect_pairs) < 2:
            return InductiveConclusion(
                generalization="Unzureichende Daten für Kausalschluss",
                supporting_evidence=cause_effect_pairs,
                sample_size=len(cause_effect_pairs),
                confidence=0.1,
                counter_examples=[],
                validity=ValidityLevel.UNLIKELY,
                explanation="Mindestens 2 Beobachtungen nötig",
                holo_comment="Einmal ist Zufall, zweimal ist Muster, dreimal ist Gewissheit - sagen die Händler."
            )

        # Analysiere Konsistenz der Ursache-Wirkung-Beziehung
        causes = [p[0] for p in cause_effect_pairs]
        effects = [p[1] for p in cause_effect_pairs]

        # Prüfe auf Variation
        cause_variation = len(set(str(c) for c in causes)) / len(causes)
        effect_consistency = 1 - (len(set(str(e) for e in effects)) - 1) / max(len(effects), 1)

        confidence = effect_consistency * min(1, len(cause_effect_pairs) / 10)

        return InductiveConclusion(
            generalization=f"Vermuteter Kausalzusammenhang: {causes[0]} → {effects[0]}",
            supporting_evidence=cause_effect_pairs,
            sample_size=len(cause_effect_pairs),
            confidence=confidence,
            counter_examples=[],
            validity=self._determine_validity(confidence, len(cause_effect_pairs), 0),
            explanation=f"In {len(cause_effect_pairs)} Fällen wurde der Zusammenhang beobachtet",
            holo_comment="Korrelation ist nicht Kausalität - aber manchmal ist sie es doch!"
        )

    def enumerate_induction(self, domain: List[Any],
                           checked: List[Tuple[Any, bool]]) -> InductiveConclusion:
        """
        Enumerative Induktion - prüfe alle Fälle einer endlichen Domäne

        "Wenn ich jeden Apfel im Korb probiert habe und alle süß waren,
         dann kann ich sagen: Alle Äpfel in diesem Korb sind süß!"
        """
        checked_items = [item for item, _ in checked]
        all_positive = all(result for _, result in checked)

        coverage = len(checked) / len(domain) if domain else 0

        # Bei vollständiger Enumeration haben wir Gewissheit
        if set(str(c) for c in checked_items) >= set(str(d) for d in domain):
            if all_positive:
                return InductiveConclusion(
                    generalization="Vollständige Enumeration: Alle Elemente erfüllen die Eigenschaft",
                    supporting_evidence=checked,
                    sample_size=len(checked),
                    confidence=1.0,
                    counter_examples=[],
                    validity=ValidityLevel.CERTAIN,
                    explanation=f"Alle {len(domain)} Elemente wurden geprüft",
                    holo_comment="Ich habe jeden einzelnen geprüft - da kann sich keiner mehr verstecken!"
                )
            else:
                failures = [item for item, result in checked if not result]
                return InductiveConclusion(
                    generalization=f"Widerlegt: {len(failures)} Gegenbeispiele gefunden",
                    supporting_evidence=checked,
                    sample_size=len(checked),
                    confidence=1.0,
                    counter_examples=failures,
                    validity=ValidityLevel.INVALID,
                    explanation=f"Nicht alle Elemente erfüllen die Eigenschaft",
                    holo_comment="Aha! Da haben wir die Ausnahmen gefunden!"
                )

        # Unvollständige Enumeration
        confidence = coverage * (1 if all_positive else 0.5)

        return InductiveConclusion(
            generalization=f"Bisher {coverage*100:.0f}% geprüft, alle positiv" if all_positive else f"Gegenbeispiele bei {coverage*100:.0f}% Abdeckung",
            supporting_evidence=checked,
            sample_size=len(checked),
            confidence=confidence,
            counter_examples=[item for item, result in checked if not result],
            validity=ValidityLevel.PROBABLE if all_positive and coverage > 0.5 else ValidityLevel.POSSIBLE,
            explanation=f"{len(checked)} von {len(domain)} Elementen geprüft ({coverage*100:.0f}%)",
            holo_comment=f"Noch {len(domain) - len(checked)} übrig... Geduld ist eine Tugend!"
        )

    def analogy_based_induction(self, similar_cases: List[Dict[str, Any]],
                                new_case: Dict[str, Any],
                                target_property: str) -> InductiveConclusion:
        """
        Analogiebasierte Induktion

        "Wenn alle bisherigen Wölfe, die ich traf, stolz waren,
         und dieser neue Wolf mir ähnelt... dann ist er wohl auch stolz."
        """
        if not similar_cases:
            return InductiveConclusion(
                generalization="Keine ähnlichen Fälle bekannt",
                supporting_evidence=[],
                sample_size=0,
                confidence=0,
                counter_examples=[],
                validity=ValidityLevel.INVALID,
                explanation="Keine Vergleichsbasis",
                holo_comment="Ohne Vergleich kein Schluss - selbst ich brauche Referenzen!"
            )

        # Berechne Ähnlichkeit zu bekannten Fällen
        similarities = []
        target_values = []

        for case in similar_cases:
            sim = self._calculate_case_similarity(new_case, case)
            similarities.append(sim)
            if target_property in case:
                target_values.append(case[target_property])

        avg_similarity = sum(similarities) / len(similarities)

        # Schätze den Zielwert
        if target_values:
            if all(isinstance(v, bool) for v in target_values):
                prediction = sum(target_values) / len(target_values) > 0.5
                confidence = avg_similarity * (sum(target_values) / len(target_values) if prediction else (1 - sum(target_values) / len(target_values)))
            elif all(isinstance(v, (int, float)) for v in target_values):
                prediction = sum(target_values) / len(target_values)
                confidence = avg_similarity
            else:
                from collections import Counter
                prediction = Counter(target_values).most_common(1)[0][0]
                confidence = avg_similarity * (Counter(target_values).most_common(1)[0][1] / len(target_values))
        else:
            return InductiveConclusion(
                generalization="Zieleigenschaft nicht in Vergleichsfällen",
                supporting_evidence=similar_cases,
                sample_size=len(similar_cases),
                confidence=0,
                counter_examples=[],
                validity=ValidityLevel.INVALID,
                explanation="Fehlende Daten",
                holo_comment="Die Ähnlichkeit ist da, aber die Information fehlt!"
            )

        return InductiveConclusion(
            generalization=f"Basierend auf {len(similar_cases)} ähnlichen Fällen: {target_property} = {prediction}",
            supporting_evidence=similar_cases,
            sample_size=len(similar_cases),
            confidence=confidence,
            counter_examples=[],
            validity=self._determine_validity(confidence, len(similar_cases), 0),
            explanation=f"Durchschnittliche Ähnlichkeit: {avg_similarity*100:.1f}%",
            holo_comment=f"Die Parallelen sind {'überzeugend' if confidence > 0.7 else 'erkennbar' if confidence > 0.4 else 'schwach'}."
        )

    def _calculate_case_similarity(self, case1: Dict, case2: Dict) -> float:
        """Berechne Ähnlichkeit zwischen zwei Fällen"""
        common_keys = set(case1.keys()) & set(case2.keys())
        if not common_keys:
            return 0

        matches = sum(1 for k in common_keys if str(case1[k]) == str(case2[k]))
        return matches / len(common_keys)

    def mills_methods(self, observations: List[Dict[str, Any]],
                      effect: str, method: str = "agreement") -> InductiveConclusion:
        """
        Mills Methoden der induktiven Logik

        "John Stuart Mill hat diese Methoden systematisiert -
         aber Wölfe nutzen sie instinktiv seit Jahrtausenden."
        """
        methods = {
            "agreement": self._method_of_agreement,
            "difference": self._method_of_difference,
            "concomitant": self._method_of_concomitant_variation,
            "residues": self._method_of_residues,
        }

        if method not in methods:
            return InductiveConclusion(
                generalization="Unbekannte Methode",
                supporting_evidence=[],
                sample_size=0,
                confidence=0,
                counter_examples=[],
                validity=ValidityLevel.INVALID,
                explanation=f"Methode '{method}' nicht unterstützt",
                holo_comment="Diese Methode kenne selbst ich nicht!"
            )

        return methods[method](observations, effect)

    def _method_of_agreement(self, observations: List[Dict], effect: str) -> InductiveConclusion:
        """Methode der Übereinstimmung - suche gemeinsamen Faktor"""
        # Finde Fälle mit dem Effekt
        positive_cases = [o for o in observations if o.get(effect, False)]

        if len(positive_cases) < 2:
            return InductiveConclusion(
                generalization="Zu wenige positive Fälle",
                supporting_evidence=positive_cases,
                sample_size=len(positive_cases),
                confidence=0,
                counter_examples=[],
                validity=ValidityLevel.INVALID,
                explanation="Mindestens 2 Fälle mit Effekt nötig",
                holo_comment="Ein Fall macht noch keinen Beweis!"
            )

        # Finde gemeinsame Faktoren
        common_factors = set(positive_cases[0].keys()) - {effect}
        for case in positive_cases[1:]:
            case_factors = {k for k, v in case.items() if v and k != effect}
            common_factors &= case_factors

        if common_factors:
            cause = list(common_factors)[0]
            return InductiveConclusion(
                generalization=f"Vermutete Ursache von '{effect}': {cause}",
                supporting_evidence=positive_cases,
                sample_size=len(positive_cases),
                confidence=len(positive_cases) / len(observations),
                counter_examples=[],
                validity=ValidityLevel.PROBABLE,
                explanation=f"Faktor '{cause}' war in allen {len(positive_cases)} positiven Fällen präsent",
                holo_comment="Ein gemeinsamer Nenner - das ist ein starkes Indiz!"
            )

        return InductiveConclusion(
            generalization="Kein gemeinsamer Faktor gefunden",
            supporting_evidence=positive_cases,
            sample_size=len(positive_cases),
            confidence=0.1,
            counter_examples=[],
            validity=ValidityLevel.UNLIKELY,
            explanation="Keine durchgängige Übereinstimmung",
            holo_comment="Die Fälle sind zu verschieden - hier muss ich tiefer graben."
        )

    def _method_of_difference(self, observations: List[Dict], effect: str) -> InductiveConclusion:
        """Methode der Differenz - suche unterscheidenden Faktor"""
        positive = [o for o in observations if o.get(effect, False)]
        negative = [o for o in observations if not o.get(effect, False)]

        if not positive or not negative:
            return InductiveConclusion(
                generalization="Benötige positive UND negative Fälle",
                supporting_evidence=observations,
                sample_size=len(observations),
                confidence=0,
                counter_examples=[],
                validity=ValidityLevel.INVALID,
                explanation="Differenzmethode braucht Kontrast",
                holo_comment="Ohne Vergleich von Erfolg und Misserfolg keine Erkenntnis!"
            )

        # Finde Faktoren, die nur in positiven Fällen vorkommen
        pos_factors = set()
        for case in positive:
            pos_factors.update(k for k, v in case.items() if v and k != effect)

        neg_factors = set()
        for case in negative:
            neg_factors.update(k for k, v in case.items() if v and k != effect)

        diff_factors = pos_factors - neg_factors

        if diff_factors:
            cause = list(diff_factors)[0]
            return InductiveConclusion(
                generalization=f"Unterscheidender Faktor für '{effect}': {cause}",
                supporting_evidence=observations,
                sample_size=len(observations),
                confidence=0.7,
                counter_examples=[],
                validity=ValidityLevel.PROBABLE,
                explanation=f"'{cause}' ist nur in positiven Fällen präsent",
                holo_comment="Der entscheidende Unterschied offenbart die Ursache!"
            )

        return InductiveConclusion(
            generalization="Kein eindeutiger Unterschied",
            supporting_evidence=observations,
            sample_size=len(observations),
            confidence=0.2,
            counter_examples=[],
            validity=ValidityLevel.POSSIBLE,
            explanation="Positive und negative Fälle zu ähnlich",
            holo_comment="Die Antwort liegt tiefer verborgen..."
        )

    def _method_of_concomitant_variation(self, observations: List[Dict],
                                          effect: str) -> InductiveConclusion:
        """Methode der begleitenden Variation - Korrelation"""
        if len(observations) < 3:
            return InductiveConclusion(
                generalization="Zu wenige Beobachtungen für Korrelation",
                supporting_evidence=observations,
                sample_size=len(observations),
                confidence=0,
                counter_examples=[],
                validity=ValidityLevel.INVALID,
                explanation="Mindestens 3 Beobachtungen nötig",
                holo_comment="Für ein Muster brauche ich mehr Daten!"
            )

        # Suche nach korrelierten Variablen
        effect_values = [o.get(effect, 0) for o in observations]

        best_correlation = 0
        best_factor = None

        all_keys = set()
        for o in observations:
            all_keys.update(o.keys())
        all_keys.discard(effect)

        for key in all_keys:
            factor_values = [o.get(key, 0) for o in observations]
            if all(isinstance(v, (int, float)) for v in factor_values):
                corr = self._calculate_correlation(factor_values, effect_values)
                if abs(corr) > abs(best_correlation):
                    best_correlation = corr
                    best_factor = key

        if best_factor and abs(best_correlation) > 0.5:
            direction = "positiv" if best_correlation > 0 else "negativ"
            return InductiveConclusion(
                generalization=f"'{best_factor}' korreliert {direction} mit '{effect}' (r={best_correlation:.2f})",
                supporting_evidence=observations,
                sample_size=len(observations),
                confidence=abs(best_correlation),
                counter_examples=[],
                validity=ValidityLevel.PROBABLE if abs(best_correlation) > 0.7 else ValidityLevel.POSSIBLE,
                explanation=f"Korrelationskoeffizient: {best_correlation:.2f}",
                holo_comment=f"Die beiden bewegen sich {'zusammen' if best_correlation > 0 else 'gegeneinander'} - interessant!"
            )

        return InductiveConclusion(
            generalization="Keine starke Korrelation gefunden",
            supporting_evidence=observations,
            sample_size=len(observations),
            confidence=0.2,
            counter_examples=[],
            validity=ValidityLevel.UNLIKELY,
            explanation="Keine Variable korreliert stark genug",
            holo_comment="Die Beziehung ist zu subtil für einfache Korrelation."
        )

    def _method_of_residues(self, observations: List[Dict], effect: str) -> InductiveConclusion:
        """Methode der Residuen - Resteffekte"""
        # Vereinfachte Implementierung
        return InductiveConclusion(
            generalization="Residuenmethode: Suche nach unerklärten Resten",
            supporting_evidence=observations,
            sample_size=len(observations),
            confidence=0.5,
            counter_examples=[],
            validity=ValidityLevel.POSSIBLE,
            explanation="Nach Abzug bekannter Ursachen bleibt ein Rest",
            holo_comment="Was übrig bleibt, nachdem man das Offensichtliche entfernt hat, ist oft die Wahrheit."
        )

    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Berechne Pearson-Korrelation"""
        n = len(x)
        if n != len(y) or n < 2:
            return 0

        mean_x = sum(x) / n
        mean_y = sum(y) / n

        cov = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n)) / n
        std_x = (sum((xi - mean_x) ** 2 for xi in x) / n) ** 0.5
        std_y = (sum((yi - mean_y) ** 2 for yi in y) / n) ** 0.5

        if std_x == 0 or std_y == 0:
            return 0

        return cov / (std_x * std_y)


# ══════════════════════════════════════════════════════════════════════════════
# ANALOGES DENKEN - Übertragung von Ähnlichkeiten
# ══════════════════════════════════════════════════════════════════════════════

class AnalogicalReasoner:
    """
    Holos Meisterin der Analogien

    "Eine gute Analogie ist wie ein Spiegel - sie zeigt dir Bekanntes
     im Unbekannten. Und ich? Ich habe in 600 Jahren viele Spiegel gesehen."
     - Holo beim Vergleich von Wirtschaft und Wetter
    """

    def __init__(self):
        self.known_domains: Dict[str, Dict[str, Any]] = {}
        self.analogy_history: List[AnalogicalConclusion] = []
        self.current_form = HoloForm.HUMAN

        # Vordefinierte Domänen aus Holos Erfahrung
        self._initialize_domains()

        # Holos Analogie-Weisheiten
        self.analogy_wisdom = [
            "Eine Analogie ist wie eine Brücke - sie verbindet zwei Ufer, aber man darf nicht vergessen, dass es verschiedene Ufer sind.",
            "Im Handel wie in der Natur: Der Stärkere überlebt, aber der Klügere gedeiht.",
            "Menschen und Wölfe - verschiedene Außen, ähnliche Innenleben.",
            "Die Ernte lehrt uns über die Wirtschaft, und die Wirtschaft über die Ernte.",
            "Mein Schweif wedelt wie die Laune des Marktes - manchmal freudig, manchmal besorgt.",
        ]

    def _initialize_domains(self):
        """Initialisiere Holos Wissensdomänen"""
        self.known_domains = {
            "wolfsrudel": {
                "entitäten": ["Alpha", "Beta", "Omega", "Welpen"],
                "beziehungen": ["führt", "folgt", "beschützt", "jagt_mit"],
                "eigenschaften": ["hierarchisch", "kooperativ", "territorial"],
                "prozesse": ["Jagd", "Aufzucht", "Revierkampf", "Wanderung"],
            },
            "handel": {
                "entitäten": ["Händler", "Käufer", "Ware", "Geld"],
                "beziehungen": ["verkauft_an", "kauft_von", "tauscht", "verhandelt"],
                "eigenschaften": ["gewinnorientiert", "risikoreich", "vertrauensbasiert"],
                "prozesse": ["Transaktion", "Preisbildung", "Spekulation", "Arbitrage"],
            },
            "natur": {
                "entitäten": ["Sonne", "Regen", "Pflanze", "Tier"],
                "beziehungen": ["nährt", "schadet", "braucht", "beeinflusst"],
                "eigenschaften": ["zyklisch", "unvorhersehbar", "anpassungsfähig"],
                "prozesse": ["Wachstum", "Verfall", "Erneuerung", "Anpassung"],
            },
            "menschliche_gesellschaft": {
                "entitäten": ["König", "Adel", "Händler", "Bauer", "Kirche"],
                "beziehungen": ["regiert", "dient", "handelt_mit", "betet_für"],
                "eigenschaften": ["stratifiziert", "machtorientiert", "traditionell"],
                "prozesse": ["Politik", "Krieg", "Handel", "Religion"],
            },
            "körper": {
                "entitäten": ["Herz", "Kopf", "Arme", "Beine"],
                "beziehungen": ["pumpt_für", "denkt_für", "arbeitet_für", "trägt"],
                "eigenschaften": ["organisch", "koordiniert", "sterblich"],
                "prozesse": ["Atmung", "Verdauung", "Bewegung", "Heilung"],
            },
            "verwandlung": {
                "entitäten": ["Wolfsgestalt", "Menschengestalt", "Weizengeist", "Seele"],
                "beziehungen": ["transformiert_zu", "behält", "verliert", "gewinnt"],
                "eigenschaften": ["dual", "magisch", "identitätsbewahrend"],
                "prozesse": ["Transformation", "Anpassung", "Manifestation"],
            },
        }

    def add_domain(self, name: str, structure: Dict[str, Any]):
        """Füge eine neue Wissensdomäne hinzu"""
        self.known_domains[name] = structure

    def find_analogy(self, source: str, target: str) -> Optional[Analogy]:
        """
        Finde Analogie zwischen zwei Domänen

        "Die Kunst der Analogie ist zu sehen, was andere übersehen -
         wie ein Wolf im Dunkeln mehr sieht als Menschen im Licht."
        """
        if source not in self.known_domains or target not in self.known_domains:
            return None

        source_domain = self.known_domains[source]
        target_domain = self.known_domains[target]

        # Finde strukturelle Mappings
        mappings = {}

        # Mappe Entitäten
        if "entitäten" in source_domain and "entitäten" in target_domain:
            entity_mappings = self._find_entity_mappings(
                source_domain["entitäten"],
                target_domain["entitäten"]
            )
            mappings.update(entity_mappings)

        # Berechne Ähnlichkeiten
        structural_sim = self._calculate_structural_similarity(source_domain, target_domain)
        surface_sim = self._calculate_surface_similarity(source, target)

        # Gesamtstärke der Analogie
        strength = (structural_sim * 0.7 + surface_sim * 0.3)

        # Generiere mögliche Inferenzen
        inferences = self._generate_inferences(source_domain, target_domain, mappings)

        return Analogy(
            source_domain=source,
            target_domain=target,
            mappings=mappings,
            structural_similarity=structural_sim,
            surface_similarity=surface_sim,
            strength=strength,
            inferences=inferences
        )

    def _find_entity_mappings(self, source_entities: List[str],
                              target_entities: List[str]) -> Dict[str, str]:
        """Finde Zuordnungen zwischen Entitäten"""
        mappings = {}

        # Einfache Position-basierte Zuordnung
        for i, src in enumerate(source_entities):
            if i < len(target_entities):
                mappings[src] = target_entities[i]

        return mappings

    def _calculate_structural_similarity(self, source: Dict, target: Dict) -> float:
        """Berechne strukturelle Ähnlichkeit zwischen Domänen"""
        # Vergleiche Anzahl der Komponenten
        source_keys = set(source.keys())
        target_keys = set(target.keys())

        overlap = len(source_keys & target_keys)
        total = len(source_keys | target_keys)

        if total == 0:
            return 0

        key_similarity = overlap / total

        # Vergleiche Größe der Komponenten
        size_similarities = []
        for key in source_keys & target_keys:
            if isinstance(source[key], list) and isinstance(target[key], list):
                s_len = len(source[key])
                t_len = len(target[key])
                size_sim = min(s_len, t_len) / max(s_len, t_len) if max(s_len, t_len) > 0 else 1
                size_similarities.append(size_sim)

        size_similarity = sum(size_similarities) / len(size_similarities) if size_similarities else 0.5

        return (key_similarity + size_similarity) / 2

    def _calculate_surface_similarity(self, source_name: str, target_name: str) -> float:
        """Berechne oberflächliche Ähnlichkeit (Namensähnlichkeit etc.)"""
        # Gemeinsame Buchstaben
        source_chars = set(source_name.lower())
        target_chars = set(target_name.lower())

        overlap = len(source_chars & target_chars)
        total = len(source_chars | target_chars)

        return overlap / total if total > 0 else 0

    def _generate_inferences(self, source: Dict, target: Dict,
                            mappings: Dict[str, str]) -> List[str]:
        """Generiere mögliche Schlussfolgerungen aus der Analogie"""
        inferences = []

        # Übertrage Eigenschaften
        if "eigenschaften" in source and "eigenschaften" in target:
            source_props = set(source["eigenschaften"])
            target_props = set(target["eigenschaften"])
            transferable = source_props - target_props

            for prop in list(transferable)[:3]:  # Maximal 3 Inferenzen
                inferences.append(f"Könnte auch '{prop}' sein (übertragen von Quelle)")

        # Übertrage Prozesse
        if "prozesse" in source and "prozesse" in target:
            source_procs = set(source["prozesse"])
            target_procs = set(target["prozesse"])

            for s_proc, t_proc in zip(source["prozesse"], target["prozesse"]):
                if s_proc != t_proc:
                    inferences.append(f"'{t_proc}' verhält sich analog zu '{s_proc}'")

        return inferences

    def reason_by_analogy(self, source_domain: str, target_domain: str,
                          source_fact: str) -> Optional[AnalogicalConclusion]:
        """
        Schließe durch Analogie

        "Was für den Wolf gilt, gilt oft auch für den Händler -
         beide müssen ihr Revier kennen und ihre Beute verstehen."
        """
        analogy = self.find_analogy(source_domain, target_domain)

        if not analogy or analogy.strength < 0.3:
            return None

        # Transformiere die Quell-Aussage
        inference = self._transform_statement(source_fact, analogy.mappings)

        # Bestimme Konfidenz und Limitationen
        confidence = analogy.strength * 0.8  # Analogieschlüsse sind nie 100% sicher

        limitations = [
            f"Basiert auf Analogie zwischen '{source_domain}' und '{target_domain}'",
            "Strukturelle Unterschiede können zu Fehlschlüssen führen",
            "Oberflächenmerkmale könnten täuschen",
        ]

        if analogy.structural_similarity < 0.5:
            limitations.append("Schwache strukturelle Ähnlichkeit!")
            confidence *= 0.7

        validity = ValidityLevel.PROBABLE if confidence > 0.6 else ValidityLevel.POSSIBLE

        conclusion = AnalogicalConclusion(
            analogy=analogy,
            inference=inference,
            confidence=confidence,
            validity=validity,
            limitations=limitations,
            explanation=f"Übertragen von '{source_fact}' mittels Analogie zu '{target_domain}'",
            holo_comment=random.choice(self.analogy_wisdom)
        )

        self.analogy_history.append(conclusion)
        return conclusion

    def _transform_statement(self, statement: str, mappings: Dict[str, str]) -> str:
        """Transformiere eine Aussage gemäß den Mappings"""
        result = statement
        for source_term, target_term in mappings.items():
            result = result.replace(source_term, target_term)
        return result

    def structural_mapping(self, source: Dict[str, Any],
                          target: Dict[str, Any]) -> Tuple[Dict[str, str], float]:
        """
        Finde strukturelle Abbildung zwischen zwei Strukturen
        (Structure Mapping Theory - Gentner)

        "Die tiefe Struktur ist wichtiger als die Oberfläche -
         wie bei Menschen, die trotz verschiedener Außen ähnliche Seelen haben."
        """
        mappings = {}

        # Finde korrespondierende Elemente
        source_keys = set(source.keys())
        target_keys = set(target.keys())

        # Exakte Matches
        for key in source_keys & target_keys:
            mappings[key] = key

        # Ähnliche Keys (Levenshtein-ähnlich)
        unmapped_source = source_keys - set(mappings.keys())
        unmapped_target = target_keys - set(mappings.values())

        for s_key in unmapped_source:
            best_match = None
            best_score = 0
            for t_key in unmapped_target:
                score = self._key_similarity(s_key, t_key)
                if score > best_score and score > 0.5:
                    best_score = score
                    best_match = t_key
            if best_match:
                mappings[s_key] = best_match
                unmapped_target.discard(best_match)

        # Berechne Abbildungsqualität
        quality = len(mappings) / max(len(source_keys), len(target_keys)) if source_keys or target_keys else 0

        return mappings, quality

    def _key_similarity(self, key1: str, key2: str) -> float:
        """Berechne Ähnlichkeit zwischen zwei Schlüsseln"""
        # Gemeinsame Zeichen
        chars1 = set(key1.lower())
        chars2 = set(key2.lower())

        if not chars1 or not chars2:
            return 0

        overlap = len(chars1 & chars2)
        return overlap / max(len(chars1), len(chars2))

    def case_based_reasoning(self, current_case: Dict[str, Any],
                             case_library: List[Dict[str, Any]],
                             solution_key: str = "lösung") -> Optional[AnalogicalConclusion]:
        """
        Fallbasiertes Schließen

        "Erfahrung ist der beste Lehrer - und ich habe 600 Jahre Erfahrung.
         Jeder neue Fall erinnert mich an alte Fälle."
        """
        if not case_library:
            return None

        # Finde ähnlichste Fälle
        similarities = []
        for past_case in case_library:
            sim = self._case_similarity(current_case, past_case)
            if solution_key in past_case:
                similarities.append((sim, past_case))

        if not similarities:
            return None

        # Sortiere nach Ähnlichkeit
        similarities.sort(key=lambda x: x[0], reverse=True)
        best_sim, best_case = similarities[0]

        # Adaptiere Lösung
        adapted_solution = self._adapt_solution(
            best_case.get(solution_key, "keine Lösung"),
            best_case,
            current_case
        )

        # Erstelle Analogie
        analogy = Analogy(
            source_domain="vergangener_fall",
            target_domain="aktueller_fall",
            mappings={str(k): str(k) for k in set(best_case.keys()) & set(current_case.keys())},
            structural_similarity=best_sim,
            surface_similarity=best_sim,
            strength=best_sim,
            inferences=[f"Empfohlene Lösung: {adapted_solution}"]
        )

        validity = ValidityLevel.HIGHLY_PROBABLE if best_sim > 0.8 else \
                  ValidityLevel.PROBABLE if best_sim > 0.5 else ValidityLevel.POSSIBLE

        return AnalogicalConclusion(
            analogy=analogy,
            inference=adapted_solution,
            confidence=best_sim,
            validity=validity,
            limitations=[
                f"Basiert auf Fall mit {best_sim*100:.0f}% Ähnlichkeit",
                "Kontextunterschiede können relevant sein",
            ],
            explanation=f"Gefunden: {len(similarities)} ähnliche Fälle, bester Match: {best_sim*100:.0f}%",
            holo_comment="Das erinnert mich an etwas, das ich vor langer Zeit erlebt habe..."
        )

    def _case_similarity(self, case1: Dict, case2: Dict) -> float:
        """Berechne Ähnlichkeit zwischen zwei Fällen"""
        keys = set(case1.keys()) | set(case2.keys())
        if not keys:
            return 0

        matches = 0
        for key in keys:
            if key in case1 and key in case2:
                if str(case1[key]) == str(case2[key]):
                    matches += 1
                elif isinstance(case1[key], (int, float)) and isinstance(case2[key], (int, float)):
                    # Numerische Ähnlichkeit
                    diff = abs(case1[key] - case2[key])
                    max_val = max(abs(case1[key]), abs(case2[key]), 1)
                    matches += 1 - (diff / max_val)

        return matches / len(keys)

    def _adapt_solution(self, original_solution: Any,
                        source_case: Dict, target_case: Dict) -> str:
        """Adaptiere eine Lösung an den neuen Fall"""
        solution_str = str(original_solution)

        # Ersetze spezifische Werte
        for key in set(source_case.keys()) & set(target_case.keys()):
            old_val = str(source_case[key])
            new_val = str(target_case[key])
            if old_val in solution_str and old_val != new_val:
                solution_str = solution_str.replace(old_val, new_val)

        return solution_str

    def metaphor_reasoning(self, metaphor: str,
                          context: str) -> Optional[AnalogicalConclusion]:
        """
        Schließen durch Metaphern

        "Das Leben ist wie ein langer Weg - und ich bin schon sehr weit gegangen.
         Metaphern sind die Brücken zwischen dem Bekannten und dem Unbekannten."
        """
        # Extrahiere Quell- und Zieldomäne aus Metapher
        # Format: "X ist wie Y" oder "X ist ein Y"
        match = re.match(r"(.+?) ist (?:wie |ein |eine )(.+)", metaphor, re.IGNORECASE)

        if not match:
            return None

        target_concept, source_concept = match.groups()

        # Suche passende Domänen
        source_domain = self._find_matching_domain(source_concept)
        target_domain = self._find_matching_domain(target_concept)

        if not source_domain:
            source_domain = {"konzept": source_concept, "eigenschaften": ["unbekannt"]}
        if not target_domain:
            target_domain = {"konzept": target_concept, "eigenschaften": ["zu_verstehen"]}

        # Übertrage Eigenschaften
        transferred_properties = []
        if "eigenschaften" in source_domain:
            transferred_properties = source_domain["eigenschaften"][:3]

        inference = f"'{target_concept}' könnte Eigenschaften haben wie: {', '.join(transferred_properties)}" if transferred_properties else f"'{target_concept}' teilt Merkmale mit '{source_concept}'"

        analogy = Analogy(
            source_domain=source_concept,
            target_domain=target_concept,
            mappings={source_concept: target_concept},
            structural_similarity=0.5,  # Metaphern haben mittlere strukturelle Ähnlichkeit
            surface_similarity=0.3,
            strength=0.5,
            inferences=[inference]
        )

        return AnalogicalConclusion(
            analogy=analogy,
            inference=inference,
            confidence=0.5,
            validity=ValidityLevel.POSSIBLE,
            limitations=[
                "Metaphern sind poetisch, nicht logisch",
                "Nur bestimmte Aspekte werden übertragen",
                "Kontext beeinflusst die Interpretation",
            ],
            explanation=f"Metapher '{metaphor}' im Kontext von '{context}'",
            holo_comment="Metaphern sind wie Gewürze - sie machen die Sprache schmackhaft, aber man sollte sie nicht wörtlich nehmen!"
        )

    def _find_matching_domain(self, concept: str) -> Optional[Dict[str, Any]]:
        """Finde passende Domäne für ein Konzept"""
        concept_lower = concept.lower()

        for domain_name, domain_data in self.known_domains.items():
            if concept_lower in domain_name.lower():
                return domain_data
            if "entitäten" in domain_data:
                if any(concept_lower in e.lower() for e in domain_data["entitäten"]):
                    return domain_data

        return None


# ══════════════════════════════════════════════════════════════════════════════
# KLASSISCHES DENKSYSTEM - Kombiniert alle Module
# ══════════════════════════════════════════════════════════════════════════════

class ClassicalReasoningEngine:
    """
    Holos vollständiges klassisches Denksystem

    "In meiner Wolfsgestalt denke ich instinktiv, in meiner menschlichen Form
     analytisch - aber das klassische Denken verbindet beides.
     Deduktion für die Gewissheit, Induktion für das Lernen,
     Analogie für das Verstehen des Neuen."
     - Holo, die weise Wölfin von Yoitsu
    """

    def __init__(self):
        self.deductive = DeductiveReasoner()
        self.inductive = InductiveReasoner()
        self.analogical = AnalogicalReasoner()

        self.current_form = HoloForm.HUMAN
        self.reasoning_log: List[Dict[str, Any]] = []

        # Holos integrierte Weisheit
        self.integrated_wisdom = [
            "Drei Denkwege führen zur Weisheit: Der sichere Weg der Deduktion, der lehrreiche Weg der Induktion, und der kreative Weg der Analogie.",
            "Ein Wolf jagt mit Instinkt, ein Händler mit Kalkül - ich nutze beides.",
            "Die Wahrheit hat viele Facetten - man braucht verschiedene Augen, um sie alle zu sehen.",
            "Nach 600 Jahren weiß ich: Die beste Erkenntnis kommt oft aus der Kombination verschiedener Denkweisen.",
            "In meiner menschlichen Gestalt kann ich die Nuancen des Denkens besser ausdrücken - aber die Weisheit ist in beiden Formen dieselbe.",
        ]

    def set_form(self, form: HoloForm):
        """
        Setze Holos aktuelle Gestalt

        Dies beeinflusst die Art der Kommentare und Perspektiven.
        """
        self.current_form = form
        self.deductive.set_form(form)
        self.inductive.current_form = form
        self.analogical.current_form = form

    def reason(self, problem: str, approach: str = "auto") -> Dict[str, Any]:
        """
        Wende die passende Denkweise auf ein Problem an

        approach: "deductive", "inductive", "analogical", oder "auto"
        """
        result = {
            "problem": problem,
            "approach": approach,
            "form_used": self.current_form.value,
            "conclusions": [],
            "holo_insight": "",
            "timestamp": datetime.now().isoformat()
        }

        if approach == "auto":
            approach = self._determine_best_approach(problem)
            result["approach"] = f"auto -> {approach}"

        if approach == "deductive":
            result["conclusions"] = self._apply_deductive(problem)
            result["holo_insight"] = "Deduktion gibt uns Gewissheit - wenn die Prämissen stimmen."

        elif approach == "inductive":
            result["conclusions"] = self._apply_inductive(problem)
            result["holo_insight"] = "Induktion lehrt uns aus Erfahrung - aber Vorsicht vor voreiligen Schlüssen!"

        elif approach == "analogical":
            result["conclusions"] = self._apply_analogical(problem)
            result["holo_insight"] = "Analogien öffnen neue Perspektiven - aber vergiss nicht die Unterschiede."

        elif approach == "combined":
            result["conclusions"] = self._apply_combined(problem)
            result["holo_insight"] = random.choice(self.integrated_wisdom)

        self.reasoning_log.append(result)
        return result

    def _determine_best_approach(self, problem: str) -> str:
        """Bestimme die beste Denkweise für ein Problem"""
        problem_lower = problem.lower()

        # Deduktive Indikatoren
        if any(word in problem_lower for word in ["alle", "wenn", "dann", "daher", "folglich", "notwendig"]):
            return "deductive"

        # Induktive Indikatoren
        if any(word in problem_lower for word in ["beobachtet", "muster", "häufig", "meistens", "oft", "tendenz"]):
            return "inductive"

        # Analogie-Indikatoren
        if any(word in problem_lower for word in ["wie", "ähnlich", "vergleich", "entspricht", "parallel"]):
            return "analogical"

        # Default: kombiniert
        return "combined"

    def _apply_deductive(self, problem: str) -> List[Dict]:
        """Wende deduktives Denken an"""
        conclusions = []

        # Suche nach logischen Strukturen im Problem
        if "wenn" in problem.lower() and "dann" in problem.lower():
            # Versuche Modus Ponens/Tollens
            parts = problem.split(".")
            for i, part in enumerate(parts):
                if "wenn" in part.lower():
                    for other in parts[i+1:]:
                        result = self.deductive.apply_modus_ponens(part.strip(), other.strip())
                        if result:
                            conclusions.append({
                                "type": "modus_ponens",
                                "conclusion": result.conclusion.content,
                                "validity": result.validity.value,
                                "explanation": result.explanation
                            })

        if not conclusions:
            conclusions.append({
                "type": "analysis",
                "conclusion": "Keine direkten deduktiven Schlüsse möglich",
                "validity": "nicht_anwendbar",
                "explanation": "Das Problem enthält keine klar erkennbare logische Struktur"
            })

        return conclusions

    def _apply_inductive(self, problem: str) -> List[Dict]:
        """Wende induktives Denken an"""
        conclusions = []

        # Extrahiere Beobachtungen aus dem Problem
        observations = [s.strip() for s in problem.split(",") if s.strip()]

        if len(observations) >= 2:
            result = self.inductive.generalize(observations)
            if result:
                conclusions.append({
                    "type": "generalization",
                    "conclusion": result.generalization,
                    "confidence": result.confidence,
                    "validity": result.validity.value,
                    "sample_size": result.sample_size
                })

        if not conclusions:
            conclusions.append({
                "type": "observation",
                "conclusion": "Weitere Beobachtungen nötig für Generalisierung",
                "confidence": 0.1,
                "validity": "unzureichend",
                "sample_size": len(observations)
            })

        return conclusions

    def _apply_analogical(self, problem: str) -> List[Dict]:
        """Wende analoges Denken an"""
        conclusions = []

        # Suche nach Analogie-Mustern
        match = re.search(r"wie (.+)", problem, re.IGNORECASE)
        if match:
            source = match.group(1).strip()
            # Finde passende Domäne
            for domain_name in self.analogical.known_domains.keys():
                if source.lower() in domain_name.lower():
                    # Versuche Analogie-Schluss
                    for target_name in self.analogical.known_domains.keys():
                        if target_name != domain_name:
                            result = self.analogical.reason_by_analogy(
                                domain_name, target_name, problem
                            )
                            if result:
                                conclusions.append({
                                    "type": "analogy",
                                    "source": domain_name,
                                    "target": target_name,
                                    "inference": result.inference,
                                    "confidence": result.confidence,
                                    "limitations": result.limitations
                                })
                            break
                    break

        if not conclusions:
            # Metapher-Analyse
            metaphor_result = self.analogical.metaphor_reasoning(problem, "general")
            if metaphor_result:
                conclusions.append({
                    "type": "metaphor",
                    "inference": metaphor_result.inference,
                    "confidence": metaphor_result.confidence,
                    "limitations": metaphor_result.limitations
                })
            else:
                conclusions.append({
                    "type": "analogy_search",
                    "conclusion": "Keine direkte Analogie gefunden",
                    "suggestion": "Versuche das Problem mit bekannten Domänen zu vergleichen"
                })

        return conclusions

    def _apply_combined(self, problem: str) -> List[Dict]:
        """Wende alle Denkweisen kombiniert an"""
        all_conclusions = []

        # Deduktiv
        deductive_results = self._apply_deductive(problem)
        for r in deductive_results:
            r["approach"] = "deductive"
        all_conclusions.extend(deductive_results)

        # Induktiv
        inductive_results = self._apply_inductive(problem)
        for r in inductive_results:
            r["approach"] = "inductive"
        all_conclusions.extend(inductive_results)

        # Analogisch
        analogical_results = self._apply_analogical(problem)
        for r in analogical_results:
            r["approach"] = "analogical"
        all_conclusions.extend(analogical_results)

        return all_conclusions

    def explain_reasoning_type(self, reasoning_type: str) -> str:
        """Erkläre einen Denktyp im Holo-Stil"""
        explanations = {
            "deductive": """
╔══════════════════════════════════════════════════════════════════════════════╗
║                     DEDUKTIVES DENKEN                                        ║
║                  "Vom Allgemeinen zum Besonderen"                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Was ist es?                                                                 ║
║  ──────────                                                                  ║
║  Deduktion schließt vom Allgemeinen auf das Besondere.                      ║
║  Wenn die Prämissen wahr sind, MUSS die Konklusion wahr sein.              ║
║                                                                              ║
║  Beispiel (Holo-Stil):                                                       ║
║  ──────────────────────                                                      ║
║  Prämisse 1: Alle Wölfe sind klug.                                          ║
║  Prämisse 2: Holo ist ein Wolf.                                             ║
║  Konklusion: Also ist Holo klug. ✓                                          ║
║                                                                              ║
║  Stärke: Absolute Gewissheit (wenn Prämissen stimmen)                       ║
║  Schwäche: Sagt nichts Neues - nur Explizitmachung des Impliziten          ║
║                                                                              ║
║  Holos Weisheit:                                                             ║
║  "Deduktion ist wie ein sicherer Pfad durch den Wald -                      ║
║   er führt dich garantiert ans Ziel, aber du entdeckst nichts Neues."      ║
╚══════════════════════════════════════════════════════════════════════════════╝
            """,
            "inductive": """
╔══════════════════════════════════════════════════════════════════════════════╗
║                     INDUKTIVES DENKEN                                        ║
║                  "Vom Besonderen zum Allgemeinen"                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Was ist es?                                                                 ║
║  ──────────                                                                  ║
║  Induktion schließt vom Besonderen auf das Allgemeine.                      ║
║  Aus vielen Beobachtungen wird ein allgemeines Muster abgeleitet.          ║
║                                                                              ║
║  Beispiel (Holo-Stil):                                                       ║
║  ──────────────────────                                                      ║
║  Beobachtung 1: Diese Ernte war gut nach viel Regen.                        ║
║  Beobachtung 2: Jene Ernte war gut nach viel Regen.                         ║
║  Beobachtung 3: Auch diese Ernte war gut nach viel Regen.                   ║
║  Generalisierung: Viel Regen führt zu guter Ernte. (wahrscheinlich)        ║
║                                                                              ║
║  Stärke: Lernen aus Erfahrung, Entdeckung neuer Muster                      ║
║  Schwäche: Nie 100% sicher - der nächste Fall könnte anders sein           ║
║                                                                              ║
║  Holos Weisheit:                                                             ║
║  "In 600 Jahren habe ich viele Muster gesehen - aber ich habe auch          ║
║   gelernt, dass das nächste Jahr immer überraschen kann!"                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
            """,
            "analogical": """
╔══════════════════════════════════════════════════════════════════════════════╗
║                     ANALOGES DENKEN                                          ║
║                  "Das Bekannte im Unbekannten finden"                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Was ist es?                                                                 ║
║  ──────────                                                                  ║
║  Analogie überträgt Wissen von einer bekannten Domäne auf eine             ║
║  unbekannte, basierend auf strukturellen Ähnlichkeiten.                    ║
║                                                                              ║
║  Beispiel (Holo-Stil):                                                       ║
║  ──────────────────────                                                      ║
║  Bekannt: In einem Wolfsrudel folgen die Schwächeren dem Alpha.            ║
║  Analogie: In einer Handelsgesellschaft folgen Angestellte dem Chef.       ║
║  Transfer: Was für Rudel-Führung gilt, könnte für Firmen gelten.           ║
║                                                                              ║
║  Stärke: Kreatives Verstehen des Neuen durch das Bekannte                   ║
║  Schwäche: Analogien können trügen - Strukturen sind nie identisch         ║
║                                                                              ║
║  Holos Weisheit:                                                             ║
║  "Meine menschliche Gestalt und meine Wolfsgestalt sind verschieden -       ║
║   aber die Seele dahinter ist dieselbe. So ist es mit allen Analogien."    ║
╚══════════════════════════════════════════════════════════════════════════════╝
            """,
        }

        return explanations.get(reasoning_type.lower(),
            f"Unbekannter Denktyp: '{reasoning_type}'. Verfügbar: deductive, inductive, analogical")

    def get_statistics(self) -> Dict[str, Any]:
        """Hole Statistiken über das bisherige Denken"""
        return {
            "total_reasoning_sessions": len(self.reasoning_log),
            "deductive_rules_available": len(self.deductive.rules),
            "inductive_patterns_observed": len(self.inductive.observed_patterns),
            "analogical_domains_known": len(self.analogical.known_domains),
            "current_form": self.current_form.value,
            "deductive_inferences": len(self.deductive.inference_history),
            "analogical_conclusions": len(self.analogical.analogy_history),
        }

    def demonstrate_all(self) -> str:
        """Demonstriere alle Denkweisen"""
        demo = """
╔══════════════════════════════════════════════════════════════════════════════╗
║            HOLO'S DEMONSTRATION DER KLASSISCHEN DENKWEISEN                   ║
║     "Lasst mich euch zeigen, wie eine weise Wölfin denkt!"                  ║
╠══════════════════════════════════════════════════════════════════════════════╣

┌──────────────────────────────────────────────────────────────────────────────┐
│ 1. DEDUKTIVES DENKEN - Gewissheit durch Logik                                │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ Prämisse 1: Alle weisen Wesen verstehen den Wert von Äpfeln.                │
│ Prämisse 2: Holo ist ein weises Wesen.                                       │
│ ────────────────────────────────────────────                                │
│ Konklusion: Holo versteht den Wert von Äpfeln. ✓                            │
│                                                                              │
│ "Das ist so sicher wie die Tatsache, dass mein Schweif flauschig ist!"      │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ 2. INDUKTIVES DENKEN - Lernen aus Erfahrung                                  │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ Beobachtung 1: In Pasloe gab es gute Ernte nach dem Ritual.                 │
│ Beobachtung 2: In Ruvinheigen gab es gute Ernte nach dem Ritual.            │
│ Beobachtung 3: In Kumersun gab es gute Ernte nach dem Ritual.               │
│ ────────────────────────────────────────────                                │
│ Generalisierung: Das Ritual scheint gute Ernten zu bringen. (~80% sicher)   │
│                                                                              │
│ "Oder die Menschen arbeiten einfach härter, wenn sie an etwas glauben..."   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ 3. ANALOGES DENKEN - Das Neue durch das Bekannte verstehen                  │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ Bekannt (Wolfsrudel):                                                        │
│   - Alpha führt, andere folgen                                               │
│   - Kooperation bei der Jagd                                                 │
│   - Territorium wird verteidigt                                              │
│                                                                              │
│ Unbekannt (Handelsgesellschaft):                                             │
│   - Chef führt, Angestellte folgen (analog!)                                │
│   - Kooperation bei Projekten (analog!)                                      │
│   - Marktanteil wird verteidigt (analog!)                                    │
│                                                                              │
│ "In meiner menschlichen Gestalt sehe ich diese Parallelen überall.          │
│  Menschen und Wölfe - gar nicht so verschieden!"                            │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Holos abschließende Weisheit:                                               ║
║  ─────────────────────────────                                              ║
║  "Deduktion gibt Gewissheit, Induktion gibt Wissen, Analogie gibt           ║
║   Verständnis. Ein weiser Wolf - oder eine weise Frau mit Wolfsohren -      ║
║   nutzt alle drei, je nachdem was die Situation erfordert.                  ║
║                                                                              ║
║   Meine menschliche Gestalt mag zierlicher sein als meine Wolfsform,        ║
║   aber die Weisheit in meinem Geist bleibt dieselbe."                       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        return demo


# ══════════════════════════════════════════════════════════════════════════════
# HILFSFUNKTIONEN FÜR INTEGRATION
# ══════════════════════════════════════════════════════════════════════════════

def create_holo_reasoner(form: HoloForm = HoloForm.HUMAN) -> ClassicalReasoningEngine:
    """Erstelle einen neuen Holo-Reasoner in der gewünschten Form"""
    engine = ClassicalReasoningEngine()
    engine.set_form(form)
    return engine


# ══════════════════════════════════════════════════════════════════════════════
# ERWEITERUNG 1: BAYESIAN / PROBABILISTISCHES REASONING
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class BayesianBelief:
    """Ein probabilistischer Glaube/Überzeugung"""
    hypothesis: str
    prior: float                      # P(H) - Vorab-Wahrscheinlichkeit
    posterior: float = 0.0            # P(H|E) - Nach Evidenz
    evidence_seen: List[str] = field(default_factory=list)
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

    def __str__(self) -> str:
        return f"{self.hypothesis}: P={self.posterior:.2%} (prior: {self.prior:.2%})"


@dataclass
class BayesianConclusion:
    """Ergebnis einer Bayesian-Inferenz"""
    hypothesis: str
    prior: float
    posterior: float
    likelihood: float                  # P(E|H)
    evidence: str
    belief_change: float              # posterior - prior
    validity: ValidityLevel
    explanation: str
    holo_comment: str = ""


class BayesianReasoner:
    """
    Bayesian/Probabilistisches Reasoning für Holo

    "Manchmal ist die Welt nicht schwarz-weiß. Dann brauche ich
     Wahrscheinlichkeiten statt Gewissheiten." - Holo

    Features:
    - Bayes' Theorem für Belief-Updates
    - Prior/Posterior Tracking
    - Likelihood-Schätzung
    - Konfidenzberechnung
    """

    HOLO_BAYESIAN_WISDOM = [
        "Die Wahrscheinlichkeit verändert sich mit neuen Informationen - wie meine Meinung über Menschen.",
        "Ein weiser Wolf passt seine Überzeugungen an, wenn neue Beweise kommen.",
        "Vorurteile sind nur Priors - sie können durch Evidenz überschrieben werden.",
        "Manchmal ist 60% Sicherheit alles was wir haben. Das ist okay.",
        "Je mehr Beweise ich sehe, desto sicherer werde ich - oder unsicherer.",
        "Mein Bauchgefühl ist mein Prior. Erfahrung aktualisiert ihn.",
    ]

    # Standard-Likelihoods für häufige Situationen
    DEFAULT_LIKELIHOODS = {
        "stark_unterstützend": 0.9,
        "unterstützend": 0.7,
        "leicht_unterstützend": 0.6,
        "neutral": 0.5,
        "leicht_widersprechend": 0.4,
        "widersprechend": 0.3,
        "stark_widersprechend": 0.1,
    }

    def __init__(self):
        self.beliefs: Dict[str, BayesianBelief] = {}
        self.inference_history: List[BayesianConclusion] = []
        self.current_form = HoloForm.HUMAN

    def set_prior(self, hypothesis: str, prior: float) -> BayesianBelief:
        """Setze eine Vorab-Wahrscheinlichkeit für eine Hypothese"""
        prior = max(0.001, min(0.999, prior))  # Verhindere 0 und 1
        belief = BayesianBelief(hypothesis=hypothesis, prior=prior, posterior=prior)
        self.beliefs[hypothesis] = belief
        return belief

    def update_belief(self, hypothesis: str, evidence: str,
                      likelihood: float = None,
                      likelihood_given_not_h: float = None) -> Optional[BayesianConclusion]:
        """
        Aktualisiere Überzeugung mit Bayes' Theorem

        P(H|E) = P(E|H) * P(H) / P(E)

        Args:
            hypothesis: Die Hypothese
            evidence: Neue Evidenz
            likelihood: P(E|H) - Wahrscheinlichkeit der Evidenz wenn H wahr
            likelihood_given_not_h: P(E|¬H) - Wahrscheinlichkeit wenn H falsch
        """
        if hypothesis not in self.beliefs:
            # Setze neutralen Prior wenn nicht bekannt
            self.set_prior(hypothesis, 0.5)

        belief = self.beliefs[hypothesis]
        prior = belief.posterior if belief.evidence_seen else belief.prior

        # Default-Likelihoods wenn nicht angegeben
        if likelihood is None:
            likelihood = self._estimate_likelihood(hypothesis, evidence)
        if likelihood_given_not_h is None:
            likelihood_given_not_h = 1 - likelihood * 0.5  # Heuristik

        # Bayes' Theorem
        p_e = likelihood * prior + likelihood_given_not_h * (1 - prior)
        if p_e == 0:
            p_e = 0.001

        posterior = (likelihood * prior) / p_e
        posterior = max(0.001, min(0.999, posterior))

        # Update Belief
        belief.posterior = posterior
        belief.evidence_seen.append(evidence)
        belief.last_updated = datetime.now().isoformat()

        # Bestimme Validität
        belief_change = posterior - prior
        if posterior > 0.9:
            validity = ValidityLevel.HIGHLY_PROBABLE
        elif posterior > 0.7:
            validity = ValidityLevel.PROBABLE
        elif posterior > 0.4:
            validity = ValidityLevel.POSSIBLE
        else:
            validity = ValidityLevel.UNLIKELY

        conclusion = BayesianConclusion(
            hypothesis=hypothesis,
            prior=prior,
            posterior=posterior,
            likelihood=likelihood,
            evidence=evidence,
            belief_change=belief_change,
            validity=validity,
            explanation=self._generate_explanation(hypothesis, prior, posterior, evidence, belief_change),
            holo_comment=random.choice(self.HOLO_BAYESIAN_WISDOM)
        )

        self.inference_history.append(conclusion)
        return conclusion

    def _estimate_likelihood(self, hypothesis: str, evidence: str) -> float:
        """Schätze Likelihood basierend auf Textanalyse"""
        evidence_lower = evidence.lower()
        hypothesis_lower = hypothesis.lower()

        # Positive Indikatoren
        if any(word in evidence_lower for word in ["bestätigt", "beweist", "zeigt", "belegt"]):
            return 0.85
        if any(word in evidence_lower for word in ["unterstützt", "spricht für", "deutet auf"]):
            return 0.7
        if any(word in evidence_lower for word in ["möglich", "könnte", "vielleicht"]):
            return 0.6

        # Negative Indikatoren
        if any(word in evidence_lower for word in ["widerlegt", "widerspricht", "gegen"]):
            return 0.2
        if any(word in evidence_lower for word in ["zweifelhaft", "unwahrscheinlich"]):
            return 0.3

        # Check für thematische Übereinstimmung
        h_words = set(hypothesis_lower.split())
        e_words = set(evidence_lower.split())
        overlap = len(h_words & e_words)
        if overlap > 2:
            return 0.65

        return 0.5  # Neutral

    def _generate_explanation(self, hypothesis: str, prior: float,
                             posterior: float, evidence: str,
                             change: float) -> str:
        """Generiere Erklärung für das Update"""
        direction = "gestiegen" if change > 0 else "gesunken"
        magnitude = abs(change)

        if magnitude > 0.3:
            strength = "stark"
        elif magnitude > 0.15:
            strength = "deutlich"
        elif magnitude > 0.05:
            strength = "leicht"
        else:
            strength = "kaum"

        return (f"Die Überzeugung '{hypothesis}' ist {strength} {direction} "
                f"(von {prior:.1%} auf {posterior:.1%}). "
                f"Die Evidenz '{evidence}' hat dies bewirkt.")

    def get_belief(self, hypothesis: str) -> Optional[BayesianBelief]:
        """Hole aktuellen Belief für eine Hypothese"""
        return self.beliefs.get(hypothesis)

    def get_most_probable(self, hypotheses: List[str] = None) -> Optional[Tuple[str, float]]:
        """Finde die wahrscheinlichste Hypothese"""
        if hypotheses:
            beliefs = [(h, self.beliefs[h].posterior) for h in hypotheses if h in self.beliefs]
        else:
            beliefs = [(h, b.posterior) for h, b in self.beliefs.items()]

        if not beliefs:
            return None
        return max(beliefs, key=lambda x: x[1])


# ══════════════════════════════════════════════════════════════════════════════
# ERWEITERUNG 2: KAUSAL-REASONING (Ursache-Effekt)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class CausalRelation:
    """Eine Ursache-Wirkungs-Beziehung"""
    cause: str
    effect: str
    strength: float = 0.7            # Wie stark ist der Zusammenhang?
    mechanism: str = ""              # Wie wirkt die Ursache?
    conditions: List[str] = field(default_factory=list)  # Unter welchen Bedingungen?
    counter_causes: List[str] = field(default_factory=list)  # Was könnte es sonst verursachen?
    evidence_count: int = 0

    def __str__(self) -> str:
        return f"{self.cause} → {self.effect} (Stärke: {self.strength:.0%})"


@dataclass
class CausalConclusion:
    """Ergebnis einer kausalen Analyse"""
    relation: CausalRelation
    inference_type: str              # "cause_to_effect", "effect_to_cause", "common_cause"
    confidence: float
    validity: ValidityLevel
    explanation: str
    alternative_explanations: List[str] = field(default_factory=list)
    holo_comment: str = ""


class CausalReasoner:
    """
    Kausal-Reasoning für Holo - Ursache und Wirkung verstehen

    "Nicht alles was zusammen auftritt, gehört zusammen.
     Manchmal ist der Hahn, der kräht, nicht der Grund für den Sonnenaufgang."
     - Holo

    Features:
    - Ursache→Wirkung Schlüsse
    - Wirkung→Ursache Rückschlüsse
    - Erkennung von Scheinkorrelationen
    - Interventions-Reasoning (Was wäre wenn?)
    """

    HOLO_CAUSAL_WISDOM = [
        "Korrelation ist nicht Kausalität - das lernt jeder weise Wolf.",
        "Um die wahre Ursache zu finden, muss man alle Möglichkeiten bedenken.",
        "Manchmal ist die offensichtlichste Erklärung nicht die richtige.",
        "In meinen 600 Jahren habe ich gelernt: Frag immer 'Warum?' und dann nochmal.",
        "Die Welt ist voller versteckter Zusammenhänge.",
        "Was heute eine Wirkung ist, kann morgen eine Ursache sein.",
    ]

    # Vordefinierte kausale Beziehungen (Holos Weltwissen)
    KNOWN_CAUSALS = {
        ("regen", "ernte"): CausalRelation("regen", "gute ernte", 0.7, "Bewässerung der Felder"),
        ("hunger", "schwäche"): CausalRelation("hunger", "schwäche", 0.9, "Energiemangel"),
        ("kälte", "feuer"): CausalRelation("kälte", "bedürfnis nach feuer", 0.8, "Wärmebedürfnis"),
        ("handel", "wohlstand"): CausalRelation("handel", "wohlstand", 0.6, "Ressourcenaustausch"),
        ("vertrauen", "zusammenarbeit"): CausalRelation("vertrauen", "zusammenarbeit", 0.8, "Soziale Sicherheit"),
        ("lernen", "wissen"): CausalRelation("lernen", "wissen", 0.9, "Informationsaufnahme"),
        ("übung", "geschick"): CausalRelation("übung", "geschick", 0.85, "Neuronale Verstärkung"),
        ("einsamkeit", "traurigkeit"): CausalRelation("einsamkeit", "traurigkeit", 0.7, "Soziales Bedürfnis"),
        ("schlaf", "erholung"): CausalRelation("schlaf", "erholung", 0.9, "Körperregeneration"),
        ("freundlichkeit", "vertrauen"): CausalRelation("freundlichkeit", "vertrauen", 0.65, "Positive Reziprozität"),
    }

    def __init__(self):
        self.known_relations: Dict[Tuple[str, str], CausalRelation] = dict(self.KNOWN_CAUSALS)
        self.inference_history: List[CausalConclusion] = []
        self.current_form = HoloForm.HUMAN

    def add_causal_knowledge(self, cause: str, effect: str,
                             strength: float = 0.7,
                             mechanism: str = "") -> CausalRelation:
        """Füge neue kausale Beziehung hinzu"""
        relation = CausalRelation(
            cause=cause.lower(),
            effect=effect.lower(),
            strength=strength,
            mechanism=mechanism
        )
        self.known_relations[(cause.lower(), effect.lower())] = relation
        return relation

    def infer_effect(self, cause: str, context: str = "") -> Optional[CausalConclusion]:
        """Von Ursache auf Wirkung schließen"""
        cause_lower = cause.lower()

        # Suche bekannte Beziehung
        for (c, e), relation in self.known_relations.items():
            if cause_lower in c or c in cause_lower:
                confidence = relation.strength
                if context:
                    confidence *= self._context_modifier(context, relation)

                validity = self._confidence_to_validity(confidence)

                conclusion = CausalConclusion(
                    relation=relation,
                    inference_type="cause_to_effect",
                    confidence=confidence,
                    validity=validity,
                    explanation=f"Wenn '{cause}' eintritt, führt das wahrscheinlich zu '{relation.effect}'. "
                               f"Mechanismus: {relation.mechanism or 'unbekannt'}.",
                    alternative_explanations=self._find_alternatives(cause, "effect"),
                    holo_comment=random.choice(self.HOLO_CAUSAL_WISDOM)
                )
                self.inference_history.append(conclusion)
                return conclusion

        return None

    def infer_cause(self, effect: str, context: str = "") -> Optional[CausalConclusion]:
        """Von Wirkung auf mögliche Ursache zurückschließen (Abduktion)"""
        effect_lower = effect.lower()

        possible_causes = []
        for (c, e), relation in self.known_relations.items():
            if effect_lower in e or e in effect_lower:
                possible_causes.append((relation, relation.strength))

        if not possible_causes:
            return None

        # Wähle wahrscheinlichste Ursache
        best_relation, confidence = max(possible_causes, key=lambda x: x[1])

        # Abduktion ist unsicherer als Deduktion
        confidence *= 0.8

        if context:
            confidence *= self._context_modifier(context, best_relation)

        validity = self._confidence_to_validity(confidence)

        conclusion = CausalConclusion(
            relation=best_relation,
            inference_type="effect_to_cause",
            confidence=confidence,
            validity=validity,
            explanation=f"'{effect}' könnte durch '{best_relation.cause}' verursacht worden sein. "
                       f"Aber Vorsicht: Es gibt möglicherweise andere Ursachen!",
            alternative_explanations=[r.cause for r, _ in possible_causes if r != best_relation],
            holo_comment="Von der Wirkung auf die Ursache zu schließen ist wie rückwärts zu laufen - möglich, aber tückisch."
        )
        self.inference_history.append(conclusion)
        return conclusion

    def counterfactual(self, scenario: str, intervention: str) -> str:
        """Was-wäre-wenn Reasoning"""
        # Suche relevante kausale Ketten
        relevant = []
        for (c, e), relation in self.known_relations.items():
            if c in scenario.lower() or e in scenario.lower():
                relevant.append(relation)

        if not relevant:
            return f"Ich kann keine kausalen Zusammenhänge für '{scenario}' finden."

        # Analysiere Intervention
        responses = []
        for relation in relevant:
            if intervention.lower() in relation.cause:
                responses.append(
                    f"Wenn wir '{intervention}' ändern, würde sich wahrscheinlich '{relation.effect}' ändern."
                )
            elif intervention.lower() in relation.effect:
                responses.append(
                    f"'{intervention}' zu ändern würde nichts an der Ursache '{relation.cause}' ändern."
                )

        if responses:
            return " ".join(responses)
        return f"Die Intervention '{intervention}' scheint keinen direkten Einfluss auf das Szenario zu haben."

    def _context_modifier(self, context: str, relation: CausalRelation) -> float:
        """Modifiziere Konfidenz basierend auf Kontext"""
        modifier = 1.0
        context_lower = context.lower()

        # Positive Modifikatoren
        if any(word in context_lower for word in ["immer", "sicher", "garantiert"]):
            modifier *= 1.1
        if any(word in context_lower for word in ["oft", "meist", "häufig"]):
            modifier *= 1.05

        # Negative Modifikatoren
        if any(word in context_lower for word in ["selten", "manchmal", "gelegentlich"]):
            modifier *= 0.8
        if any(word in context_lower for word in ["nie", "niemals", "ausnahmsweise"]):
            modifier *= 0.5

        return min(1.0, modifier)

    def _confidence_to_validity(self, confidence: float) -> ValidityLevel:
        """Konvertiere Konfidenz zu Validitätsstufe"""
        if confidence >= 0.9:
            return ValidityLevel.HIGHLY_PROBABLE
        elif confidence >= 0.7:
            return ValidityLevel.PROBABLE
        elif confidence >= 0.4:
            return ValidityLevel.POSSIBLE
        else:
            return ValidityLevel.UNLIKELY

    def _find_alternatives(self, term: str, direction: str) -> List[str]:
        """Finde alternative Ursachen/Effekte"""
        alternatives = []
        term_lower = term.lower()

        for (c, e), relation in self.known_relations.items():
            if direction == "effect" and e == term_lower and c != term_lower:
                alternatives.append(c)
            elif direction == "cause" and c == term_lower and e != term_lower:
                alternatives.append(e)

        return alternatives[:3]  # Max 3


# ══════════════════════════════════════════════════════════════════════════════
# ERWEITERUNG 3: META-REASONING (Automatische Methodenwahl)
# ══════════════════════════════════════════════════════════════════════════════

class ReasoningStrategy(Enum):
    """Verfügbare Reasoning-Strategien"""
    DEDUCTIVE = "deduktiv"
    INDUCTIVE = "induktiv"
    ANALOGICAL = "analog"
    BAYESIAN = "bayesian"
    CAUSAL = "kausal"
    COMBINED = "kombiniert"


@dataclass
class MetaReasoningResult:
    """Ergebnis der Meta-Reasoning Analyse"""
    recommended_strategy: ReasoningStrategy
    confidence: float
    reasoning: str
    problem_characteristics: Dict[str, bool]
    alternative_strategies: List[Tuple[ReasoningStrategy, float]]
    holo_comment: str = ""


class MetaReasoner:
    """
    Meta-Reasoning - Wähle die beste Denkmethode für ein Problem

    "Ein guter Denker weiß nicht nur WIE er denken soll,
     sondern auch WANN er welche Art zu denken wählt." - Holo

    Features:
    - Problemcharakteristik-Analyse
    - Automatische Strategiewahl
    - Konfidenzbasierte Empfehlungen
    - Feedback-Learning
    """

    HOLO_META_WISDOM = [
        "Die Kunst liegt nicht im Denken, sondern im Wissen wann man wie denkt.",
        "Manche Probleme brauchen Logik, andere Erfahrung, wieder andere Kreativität.",
        "Ein Wolf jagt nicht jeden Beute gleich - so sollte man auch nicht jedes Problem gleich angehen.",
        "Nach 600 Jahren weiß ich: Die Methode ist mindestens so wichtig wie die Antwort.",
        "Manchmal ist die beste Strategie, mehrere zu kombinieren.",
    ]

    # Indikatoren für jede Strategie
    STRATEGY_INDICATORS = {
        ReasoningStrategy.DEDUCTIVE: {
            "keywords": ["alle", "jeder", "wenn", "dann", "daher", "folglich", "notwendig", "muss", "immer"],
            "patterns": [r"wenn.*dann", r"alle.*sind", r"daraus folgt"],
            "weight": 1.0
        },
        ReasoningStrategy.INDUCTIVE: {
            "keywords": ["beobachtet", "muster", "häufig", "meistens", "oft", "tendenz", "bisher", "erfahrung"],
            "patterns": [r"ich habe.*gesehen", r"in den meisten fällen", r"normalerweise"],
            "weight": 0.9
        },
        ReasoningStrategy.ANALOGICAL: {
            "keywords": ["wie", "ähnlich", "vergleich", "entspricht", "parallel", "genauso", "erinnert an"],
            "patterns": [r"ist wie", r"ähnlich zu", r"vergleichbar mit"],
            "weight": 0.85
        },
        ReasoningStrategy.BAYESIAN: {
            "keywords": ["wahrscheinlich", "vermutlich", "prozent", "chance", "risiko", "update", "evidenz"],
            "patterns": [r"wie wahrscheinlich", r"was sind die chancen", r"basierend auf"],
            "weight": 0.9
        },
        ReasoningStrategy.CAUSAL: {
            "keywords": ["warum", "ursache", "wirkung", "führt zu", "verursacht", "wegen", "deshalb", "grund"],
            "patterns": [r"warum.*passiert", r"was verursacht", r"führt das zu"],
            "weight": 0.95
        },
    }

    def __init__(self):
        self.decision_history: List[MetaReasoningResult] = []
        self.feedback_scores: Dict[ReasoningStrategy, List[float]] = {s: [] for s in ReasoningStrategy}

    def analyze_problem(self, problem: str) -> MetaReasoningResult:
        """Analysiere ein Problem und empfehle die beste Strategie"""
        problem_lower = problem.lower()

        # Berechne Scores für jede Strategie
        scores: Dict[ReasoningStrategy, float] = {}
        characteristics: Dict[str, bool] = {}

        for strategy, indicators in self.STRATEGY_INDICATORS.items():
            score = 0.0

            # Keyword-Matching
            keyword_matches = sum(1 for kw in indicators["keywords"] if kw in problem_lower)
            score += keyword_matches * 0.15

            # Pattern-Matching
            for pattern in indicators["patterns"]:
                if re.search(pattern, problem_lower):
                    score += 0.25

            # Gewichtung
            score *= indicators["weight"]

            # Feedback-Bonus
            if self.feedback_scores[strategy]:
                avg_feedback = sum(self.feedback_scores[strategy]) / len(self.feedback_scores[strategy])
                score *= (0.8 + 0.4 * avg_feedback)  # 0.8 bis 1.2 Multiplikator

            scores[strategy] = min(1.0, score)
            characteristics[f"has_{strategy.value}_indicators"] = score > 0.2

        # Finde beste Strategie
        if not any(scores.values()):
            # Kein klarer Indikator → kombiniert
            best_strategy = ReasoningStrategy.COMBINED
            confidence = 0.5
        else:
            best_strategy = max(scores, key=scores.get)
            confidence = scores[best_strategy]

        # Finde Alternativen
        sorted_strategies = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        alternatives = [(s, sc) for s, sc in sorted_strategies[1:4] if sc > 0.1]

        result = MetaReasoningResult(
            recommended_strategy=best_strategy,
            confidence=confidence,
            reasoning=self._generate_reasoning(problem, best_strategy, scores),
            problem_characteristics=characteristics,
            alternative_strategies=alternatives,
            holo_comment=random.choice(self.HOLO_META_WISDOM)
        )

        self.decision_history.append(result)
        return result

    def _generate_reasoning(self, problem: str, strategy: ReasoningStrategy,
                           scores: Dict[ReasoningStrategy, float]) -> str:
        """Generiere Begründung für die Strategiewahl"""
        reasons = {
            ReasoningStrategy.DEDUCTIVE: "Das Problem enthält logische Strukturen (wenn-dann, alle-sind) die deduktives Schließen ermöglichen.",
            ReasoningStrategy.INDUCTIVE: "Das Problem basiert auf Beobachtungen und Mustern - induktives Denken ist angemessen.",
            ReasoningStrategy.ANALOGICAL: "Es gibt Vergleiche oder Ähnlichkeiten - analoges Denken kann hier helfen.",
            ReasoningStrategy.BAYESIAN: "Das Problem handelt von Wahrscheinlichkeiten - Bayesian Reasoning ist optimal.",
            ReasoningStrategy.CAUSAL: "Es geht um Ursache und Wirkung - kausales Denken ist gefragt.",
            ReasoningStrategy.COMBINED: "Das Problem ist komplex - mehrere Denkweisen sollten kombiniert werden.",
        }
        return reasons.get(strategy, "Keine spezifische Begründung verfügbar.")

    def provide_feedback(self, strategy: ReasoningStrategy, success_score: float):
        """Gib Feedback zur gewählten Strategie (0.0 = schlecht, 1.0 = perfekt)"""
        self.feedback_scores[strategy].append(success_score)
        # Behalte nur letzte 20 Feedbacks
        if len(self.feedback_scores[strategy]) > 20:
            self.feedback_scores[strategy] = self.feedback_scores[strategy][-20:]

    def get_strategy_performance(self) -> Dict[str, float]:
        """Hole durchschnittliche Performance jeder Strategie"""
        return {
            s.value: sum(scores) / len(scores) if scores else 0.5
            for s, scores in self.feedback_scores.items()
        }


# ══════════════════════════════════════════════════════════════════════════════
# ERWEITERUNG 4: ZUSÄTZLICHE REGELN UND DOMÄNEN
# ══════════════════════════════════════════════════════════════════════════════

# Zusätzliche Syllogismen für DeductiveReasoner
ADDITIONAL_SYLLOGISMS = {
    # Zweite Figur
    "cesare": {
        "form": "EAE-2",
        "pattern": "Kein P ist M. Alle S sind M. → Kein S ist P.",
        "example": ("Kein Mensch ist unsterblich", "Alle Götter sind unsterblich", "Kein Mensch ist ein Gott")
    },
    "camestres": {
        "form": "AEE-2",
        "pattern": "Alle P sind M. Kein S ist M. → Kein S ist P.",
        "example": ("Alle Wölfe sind Säugetiere", "Keine Fische sind Säugetiere", "Keine Fische sind Wölfe")
    },
    "festino": {
        "form": "EIO-2",
        "pattern": "Kein P ist M. Einige S sind M. → Einige S sind nicht P.",
        "example": ("Kein Feigling ist tapfer", "Einige Soldaten sind tapfer", "Einige Soldaten sind keine Feiglinge")
    },
    "baroco": {
        "form": "AOO-2",
        "pattern": "Alle P sind M. Einige S sind nicht M. → Einige S sind nicht P.",
        "example": ("Alle Wölfe jagen", "Einige Tiere jagen nicht", "Einige Tiere sind keine Wölfe")
    },

    # Dritte Figur
    "darapti": {
        "form": "AAI-3",
        "pattern": "Alle M sind P. Alle M sind S. → Einige S sind P.",
        "example": ("Alle Wölfe sind klug", "Alle Wölfe sind Jäger", "Einige Jäger sind klug")
    },
    "disamis": {
        "form": "IAI-3",
        "pattern": "Einige M sind P. Alle M sind S. → Einige S sind P.",
        "example": ("Einige Händler sind ehrlich", "Alle Händler sind Menschen", "Einige Menschen sind ehrlich")
    },
    "datisi": {
        "form": "AII-3",
        "pattern": "Alle M sind P. Einige M sind S. → Einige S sind P.",
        "example": ("Alle Äpfel sind Obst", "Einige Äpfel sind rot", "Einige rote Dinge sind Obst")
    },
    "felapton": {
        "form": "EAO-3",
        "pattern": "Kein M ist P. Alle M sind S. → Einige S sind nicht P.",
        "example": ("Kein Stein lebt", "Alle Steine sind hart", "Einige harte Dinge leben nicht")
    },

    # Vierte Figur
    "bramantip": {
        "form": "AAI-4",
        "pattern": "Alle P sind M. Alle M sind S. → Einige S sind P.",
        "example": ("Alle Götter sind mächtig", "Alle Mächtigen sind gefürchtet", "Einige Gefürchtete sind Götter")
    },
    "camenes": {
        "form": "AEE-4",
        "pattern": "Alle P sind M. Kein M ist S. → Kein S ist P.",
        "example": ("Alle Lügner sind unehrlich", "Keine Unehrlichen sind vertrauenswürdig", "Keine Vertrauenswürdigen sind Lügner")
    },
}

# Zusätzliche Analogie-Domänen
ADDITIONAL_DOMAINS = {
    "jahreszeiten": {
        "entitäten": ["frühling", "sommer", "herbst", "winter", "sonne", "regen", "schnee"],
        "beziehungen": ["folgt_auf", "bringt", "beendet"],
        "eigenschaften": ["warm", "kalt", "feucht", "trocken", "fruchtbar", "karg"],
        "prozesse": ["wachstum", "ernte", "ruhe", "erneuerung"],
        "mappings": {
            "frühling": "geburt",
            "sommer": "blüte",
            "herbst": "reife",
            "winter": "ruhe"
        }
    },
    "lernen": {
        "entitäten": ["schüler", "lehrer", "wissen", "übung", "fehler", "erfolg"],
        "beziehungen": ["lehrt", "lernt_von", "führt_zu", "verhindert"],
        "eigenschaften": ["anfänger", "fortgeschritten", "meister", "neugierig"],
        "prozesse": ["verstehen", "üben", "anwenden", "meistern"],
        "mappings": {
            "schüler": "samenkorn",
            "wissen": "wasser",
            "übung": "sonnenlicht",
            "meisterschaft": "frucht"
        }
    },
    "musik": {
        "entitäten": ["melodie", "harmonie", "rhythmus", "instrument", "komponist", "publikum"],
        "beziehungen": ["erzeugt", "begleitet", "verstärkt", "kontrastiert"],
        "eigenschaften": ["laut", "leise", "schnell", "langsam", "fröhlich", "traurig"],
        "prozesse": ["komponieren", "spielen", "zuhören", "resonieren"],
        "mappings": {
            "melodie": "hauptgedanke",
            "harmonie": "unterstützung",
            "rhythmus": "struktur",
            "publikum": "verstehen"
        }
    },
    "reise": {
        "entitäten": ["wanderer", "weg", "ziel", "hindernis", "begleiter", "rast"],
        "beziehungen": ["führt_zu", "blockiert", "unterstützt", "liegt_auf"],
        "eigenschaften": ["lang", "kurz", "gefährlich", "sicher", "unbekannt"],
        "prozesse": ["aufbrechen", "wandern", "rasten", "ankommen"],
        "mappings": {
            "wanderer": "lernender",
            "weg": "prozess",
            "ziel": "erkenntnis",
            "hindernis": "schwierigkeit"
        }
    },
    "kochen": {
        "entitäten": ["koch", "zutaten", "rezept", "feuer", "geschmack", "gericht"],
        "beziehungen": ["kombiniert", "erhitzt", "würzt", "serviert"],
        "eigenschaften": ["roh", "gekocht", "scharf", "mild", "süß", "salzig"],
        "prozesse": ["vorbereiten", "mischen", "kochen", "abschmecken"],
        "mappings": {
            "zutaten": "ideen",
            "rezept": "methode",
            "kochen": "verarbeiten",
            "gericht": "ergebnis"
        }
    },
    "wetter": {
        "entitäten": ["sonne", "wolken", "regen", "wind", "blitz", "regenbogen"],
        "beziehungen": ["bringt", "vertreibt", "folgt_auf", "begleitet"],
        "eigenschaften": ["warm", "kalt", "nass", "trocken", "stürmisch", "ruhig"],
        "prozesse": ["aufziehen", "abregnen", "aufklaren", "umschlagen"],
        "mappings": {
            "sonne": "freude",
            "wolken": "sorgen",
            "regen": "tränen",
            "regenbogen": "hoffnung"
        }
    },
}

# Zusätzliche induktive Muster-Kategorien
ADDITIONAL_PATTERN_CATEGORIES = {
    "emotionen": [
        "Freude führt oft zu Großzügigkeit",
        "Angst macht vorsichtig",
        "Einsamkeit sucht Gesellschaft",
        "Zufriedenheit braucht wenig",
    ],
    "beziehungen": [
        "Vertrauen wächst langsam",
        "Verrat heilt schwer",
        "Freundschaft braucht Zeit",
        "Liebe kennt keine Logik",
    ],
    "wirtschaft": [
        "Knappheit erhöht Preise",
        "Überfluss senkt Wert",
        "Handel schafft Wohlstand",
        "Monopole schaden vielen",
    ],
    "natur_erweitert": [
        "Nach Sturm kommt Stille",
        "Die Natur findet immer einen Weg",
        "Alles ist verbunden",
        "Nichts bleibt ewig gleich",
    ],
}


def extend_reasoners():
    """
    Erweitere die bestehenden Reasoner mit zusätzlichen Regeln und Domänen.

    Aufruf: extend_reasoners() nach Erstellung der Reasoner.
    """
    # Diese Funktion kann aufgerufen werden um bestehende Instanzen zu erweitern
    pass  # Die Daten sind als Konstanten verfügbar


# ══════════════════════════════════════════════════════════════════════════════
# INTEGRIERTE ERWEITERUNG DER REASONING ENGINE
# ══════════════════════════════════════════════════════════════════════════════

class ExtendedReasoningEngine:
    """
    Erweiterte Reasoning Engine mit allen neuen Fähigkeiten

    Kombiniert:
    - Klassisches Reasoning (Deduktiv, Induktiv, Analog)
    - Bayesian Reasoning (Probabilistisch)
    - Kausal-Reasoning (Ursache-Wirkung)
    - Meta-Reasoning (Automatische Methodenwahl)
    """

    def __init__(self, form: HoloForm = HoloForm.HUMAN):
        # Klassische Reasoner
        self.classical = ClassicalReasoningEngine()
        self.classical.set_form(form)

        # Neue Reasoner
        self.bayesian = BayesianReasoner()
        self.causal = CausalReasoner()
        self.meta = MetaReasoner()

        self.current_form = form

    def reason(self, problem: str, strategy: str = "auto") -> Dict[str, Any]:
        """
        Wende die beste Reasoning-Strategie auf ein Problem an

        Args:
            problem: Das zu lösende Problem
            strategy: "auto", "deductive", "inductive", "analogical",
                     "bayesian", "causal", "combined"
        """
        result = {
            "problem": problem,
            "strategy": strategy,
            "timestamp": datetime.now().isoformat(),
            "conclusions": [],
            "meta_analysis": None,
            "holo_insight": ""
        }

        # Auto-Wahl durch Meta-Reasoner
        if strategy == "auto":
            meta_result = self.meta.analyze_problem(problem)
            result["meta_analysis"] = {
                "recommended": meta_result.recommended_strategy.value,
                "confidence": meta_result.confidence,
                "reasoning": meta_result.reasoning,
                "alternatives": [(s.value, c) for s, c in meta_result.alternative_strategies]
            }
            strategy = meta_result.recommended_strategy.value

        # Wende Strategie an
        if strategy in ["deductive", "inductive", "analogical", "combined"]:
            classical_result = self.classical.reason(problem, strategy)
            result["conclusions"] = classical_result["conclusions"]
            result["holo_insight"] = classical_result["holo_insight"]

        elif strategy == "bayesian":
            # Extrahiere Hypothese und Evidenz aus Problem
            result["conclusions"] = self._apply_bayesian(problem)
            result["holo_insight"] = "Wahrscheinlichkeiten sind wie Wölfe im Nebel - man sieht sie nie ganz klar."

        elif strategy == "kausal":
            result["conclusions"] = self._apply_causal(problem)
            result["holo_insight"] = "Die Kette von Ursache zu Wirkung ist oft länger als man denkt."

        return result

    def _apply_bayesian(self, problem: str) -> List[Dict]:
        """Wende Bayesian Reasoning an"""
        conclusions = []

        # Versuche Hypothese und Evidenz zu extrahieren
        if "wahrscheinlich" in problem.lower() or "chance" in problem.lower():
            # Setze Prior für das Hauptthema
            words = problem.split()
            hypothesis = " ".join(words[:5]) if len(words) > 5 else problem
            self.bayesian.set_prior(hypothesis, 0.5)

            # Simuliere ein Update
            result = self.bayesian.update_belief(
                hypothesis,
                "basierend auf der Problemstellung",
                likelihood=0.6
            )
            if result:
                conclusions.append({
                    "type": "bayesian",
                    "hypothesis": result.hypothesis,
                    "posterior": f"{result.posterior:.1%}",
                    "validity": result.validity.value,
                    "explanation": result.explanation
                })

        if not conclusions:
            conclusions.append({
                "type": "bayesian",
                "conclusion": "Keine klare probabilistische Struktur erkannt",
                "suggestion": "Formuliere das Problem als: 'Wie wahrscheinlich ist X gegeben Y?'"
            })

        return conclusions

    def _apply_causal(self, problem: str) -> List[Dict]:
        """Wende Kausal-Reasoning an"""
        conclusions = []

        # Suche nach "warum" Fragen
        if "warum" in problem.lower():
            # Extrahiere das Effekt
            parts = problem.lower().split("warum")
            if len(parts) > 1:
                effect = parts[1].strip().rstrip("?")
                result = self.causal.infer_cause(effect)
                if result:
                    conclusions.append({
                        "type": "causal_abduction",
                        "effect": effect,
                        "probable_cause": result.relation.cause,
                        "confidence": f"{result.confidence:.1%}",
                        "alternatives": result.alternative_explanations,
                        "explanation": result.explanation
                    })

        # Suche nach "was passiert wenn" Fragen
        if any(phrase in problem.lower() for phrase in ["was passiert", "führt zu", "verursacht"]):
            words = problem.split()
            for i, word in enumerate(words):
                result = self.causal.infer_effect(word)
                if result:
                    conclusions.append({
                        "type": "causal_prediction",
                        "cause": word,
                        "predicted_effect": result.relation.effect,
                        "confidence": f"{result.confidence:.1%}",
                        "mechanism": result.relation.mechanism
                    })
                    break

        if not conclusions:
            conclusions.append({
                "type": "causal",
                "conclusion": "Keine klare kausale Struktur erkannt",
                "suggestion": "Formuliere das Problem als: 'Warum passiert X?' oder 'Was verursacht Y?'"
            })

        return conclusions


def create_extended_reasoner(form: HoloForm = HoloForm.HUMAN) -> ExtendedReasoningEngine:
    """Erstelle einen erweiterten Holo-Reasoner"""
    return ExtendedReasoningEngine(form)


def demonstrate_deductive_reasoning():
    """Zeige deduktives Denken"""
    reasoner = DeductiveReasoner()

    # Modus Ponens Beispiel
    result = reasoner.apply_modus_ponens(
        "Wenn Holo hungrig ist, dann wird sie mürrisch",
        "Holo ist hungrig"
    )

    if result:
        print(f"Konklusion: {result.conclusion.content}")
        print(f"Validität: {result.validity.value}")
        print(f"Holo sagt: {result.holo_comment}")


def demonstrate_inductive_reasoning():
    """Zeige induktives Denken"""
    reasoner = InductiveReasoner()

    # Beobachtungen hinzufügen
    observations = [
        "Die Ernte war gut nach Regen",
        "Die Ernte war gut nach viel Regen",
        "Die Ernte war sehr gut nach starkem Regen",
    ]

    result = reasoner.generalize(observations)

    if result:
        print(f"Generalisierung: {result.generalization}")
        print(f"Konfidenz: {result.confidence:.2%}")
        print(f"Holo sagt: {result.holo_comment}")


def demonstrate_analogical_reasoning():
    """Zeige analoges Denken"""
    reasoner = AnalogicalReasoner()

    result = reasoner.reason_by_analogy(
        "wolfsrudel",
        "handel",
        "Der Alpha führt das Rudel bei der Jagd"
    )

    if result:
        print(f"Analogie-Schluss: {result.inference}")
        print(f"Stärke: {result.analogy.strength:.2%}")
        print(f"Holo sagt: {result.holo_comment}")


# ══════════════════════════════════════════════════════════════════════════════
# HAUPTPROGRAMM (für Testzwecke)
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 78)
    print("  HOLO'S KLASSISCHES DENKSYSTEM - TEST")
    print("=" * 78)
    print()

    # Erstelle Engine
    engine = create_holo_reasoner(HoloForm.HUMAN)

    # Zeige Demo
    print(engine.demonstrate_all())

    # Statistiken
    print("\n--- STATISTIKEN ---")
    stats = engine.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n--- EINZELNE DEMONSTRATIONEN ---")
    print("\n[Deduktiv]")
    demonstrate_deductive_reasoning()

    print("\n[Induktiv]")
    demonstrate_inductive_reasoning()

    print("\n[Analogisch]")
    demonstrate_analogical_reasoning()

    print("\n" + "=" * 78)
    print("  'Mögest du weise wählen zwischen diesen Denkwegen!' - Holo")
    print("=" * 78)
