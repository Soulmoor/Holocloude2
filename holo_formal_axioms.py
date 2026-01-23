#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO FORMAL AXIOMS - Formales Axiom-System                                  ║
║                                                                              ║
║  Implementiert ein formales axiomatisches System für:                        ║
║                                                                              ║
║  1. WISSENS-AXIOME    → Epistemische Logik (Wissen, Glauben, Gewissheit)   ║
║  2. LOGIK-AXIOME      → Klassische & nicht-klassische Logik                 ║
║  3. ETHIK-AXIOME      → Deontische Logik (Pflicht, Erlaubnis, Verbot)       ║
║  4. LERN-AXIOME       → Axiome für adaptives Lernen                         ║
║                                                                              ║
║  Basiert auf formaler Logik und erlaubt maschinelles Schließen.            ║
╚══════════════════════════════════════════════════════════════════════════════╝

Autor: Holocloude System
Version: 1.0
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set, Callable, Union
from enum import Enum, auto
from datetime import datetime
from abc import ABC, abstractmethod
import re

logger = logging.getLogger("HoloFormalAxioms")


# =============================================================================
# ENUMS
# =============================================================================

class AxiomCategory(Enum):
    """Kategorien von Axiomen"""
    KNOWLEDGE = "knowledge"        # Wissens-Axiome (Epistemische Logik)
    LOGIC = "logic"               # Logik-Axiome
    ETHICS = "ethics"             # Ethik-Axiome (Deontische Logik)
    LEARNING = "learning"         # Lern-Axiome


class LogicType(Enum):
    """Arten von Logik"""
    CLASSICAL = "classical"           # Klassische Aussagenlogik
    MODAL = "modal"                   # Modallogik (notwendig/möglich)
    EPISTEMIC = "epistemic"           # Epistemische Logik (wissen/glauben)
    DEONTIC = "deontic"               # Deontische Logik (sollen/dürfen)
    TEMPORAL = "temporal"             # Temporale Logik (immer/manchmal)
    FUZZY = "fuzzy"                   # Fuzzy-Logik (Wahrheitsgrade)


class TruthValue(Enum):
    """Wahrheitswerte"""
    TRUE = "true"
    FALSE = "false"
    UNKNOWN = "unknown"
    CONTRADICTORY = "contradictory"


class ModalOperator(Enum):
    """Modale Operatoren"""
    NECESSARY = "necessary"     # □ (notwendig)
    POSSIBLE = "possible"       # ◇ (möglich)
    KNOWS = "knows"             # K (weiß)
    BELIEVES = "believes"       # B (glaubt)
    OBLIGATORY = "obligatory"   # O (geboten)
    PERMITTED = "permitted"     # P (erlaubt)
    FORBIDDEN = "forbidden"     # F (verboten)
    ALWAYS = "always"           # G (immer)
    EVENTUALLY = "eventually"   # F (irgendwann)
    UNTIL = "until"             # U (bis)


class InferenceRule(Enum):
    """Schlussregeln"""
    MODUS_PONENS = "modus_ponens"           # A, A→B ⊢ B
    MODUS_TOLLENS = "modus_tollens"         # ¬B, A→B ⊢ ¬A
    HYPOTHETICAL_SYLLOGISM = "hypothetical" # A→B, B→C ⊢ A→C
    DISJUNCTIVE_SYLLOGISM = "disjunctive"   # A∨B, ¬A ⊢ B
    CONJUNCTION = "conjunction"              # A, B ⊢ A∧B
    SIMPLIFICATION = "simplification"        # A∧B ⊢ A
    ADDITION = "addition"                    # A ⊢ A∨B
    RESOLUTION = "resolution"                # A∨B, ¬A∨C ⊢ B∨C


# =============================================================================
# DATENSTRUKTUREN
# =============================================================================

@dataclass
class Proposition:
    """Eine logische Aussage"""
    symbol: str                     # z.B. "P", "Q", "R"
    content: str                    # Natürlichsprachliche Bedeutung
    truth_value: TruthValue = TruthValue.UNKNOWN
    confidence: float = 0.5         # Für Fuzzy-Logik
    modal_context: Optional[ModalOperator] = None
    agent: Optional[str] = None     # Für epistemische/deontische Logik


@dataclass
class Formula:
    """Eine logische Formel (zusammengesetzt)"""
    expression: str                 # z.B. "P → Q", "□P"
    propositions: List[Proposition] = field(default_factory=list)
    is_axiom: bool = False
    is_theorem: bool = False
    proof: List[str] = field(default_factory=list)
    derived_from: List[str] = field(default_factory=list)


@dataclass
class Axiom:
    """Ein formales Axiom"""
    id: str                         # Eindeutige ID
    category: AxiomCategory
    name: str                       # Name des Axioms
    formula: str                    # Formale Darstellung
    natural_language: str           # Natürlichsprachliche Beschreibung
    is_fundamental: bool = True     # Grundaxiom oder abgeleitet?
    dependencies: List[str] = field(default_factory=list)  # Abhängigkeiten
    examples: List[str] = field(default_factory=list)


@dataclass
class Inference:
    """Ein Schlussfolgerung"""
    rule: InferenceRule
    premises: List[str]             # Prämissen (Formeln)
    conclusion: str                 # Konklusion
    is_valid: bool = True
    explanation: str = ""


@dataclass
class KnowledgeState:
    """Wissenszustand eines Agenten"""
    agent: str
    known: Set[str] = field(default_factory=set)       # Gewusstes
    believed: Set[str] = field(default_factory=set)    # Geglaubtes
    unknown: Set[str] = field(default_factory=set)     # Explizit unbekannt
    certainty: Dict[str, float] = field(default_factory=dict)  # Gewissheitsgrade


# =============================================================================
# 1. WISSENS-AXIOME (Epistemische Logik)
# =============================================================================

class EpistemicAxioms:
    """
    Epistemische Axiome nach Modal-Logik S5.

    Grundoperatoren:
    - K_a(φ): Agent a weiß φ
    - B_a(φ): Agent a glaubt φ
    - C(φ): Gemeinsames Wissen (Common Knowledge)
    """

    def __init__(self):
        self.axioms: Dict[str, Axiom] = {}
        self.knowledge_states: Dict[str, KnowledgeState] = {}
        self._initialize_axioms()

    def _initialize_axioms(self):
        """Initialisiert die epistemischen Grundaxiome"""

        # K-Axiom (Distributionsaxiom)
        self.axioms["K"] = Axiom(
            id="K",
            category=AxiomCategory.KNOWLEDGE,
            name="Distributionsaxiom",
            formula="K(φ → ψ) → (Kφ → Kψ)",
            natural_language="Wenn man weiß, dass φ → ψ, und man weiß φ, dann weiß man auch ψ",
            examples=[
                "Wenn ich weiß, dass Regen → nasse Straße, und ich weiß es regnet, dann weiß ich die Straße ist nass"
            ]
        )

        # T-Axiom (Wissens-Wahrheits-Axiom / Veridicality)
        self.axioms["T"] = Axiom(
            id="T",
            category=AxiomCategory.KNOWLEDGE,
            name="Wahrheits-Axiom",
            formula="Kφ → φ",
            natural_language="Wenn man etwas weiß, dann ist es wahr (Wissen impliziert Wahrheit)",
            examples=[
                "Wenn ich weiß, dass es regnet, dann regnet es tatsächlich"
            ]
        )

        # 4-Axiom (Positive Introspektion)
        self.axioms["4"] = Axiom(
            id="4",
            category=AxiomCategory.KNOWLEDGE,
            name="Positive Introspektion",
            formula="Kφ → KKφ",
            natural_language="Wenn man etwas weiß, weiß man, dass man es weiß",
            examples=[
                "Wenn ich weiß, dass 2+2=4, dann weiß ich, dass ich weiß, dass 2+2=4"
            ]
        )

        # 5-Axiom (Negative Introspektion)
        self.axioms["5"] = Axiom(
            id="5",
            category=AxiomCategory.KNOWLEDGE,
            name="Negative Introspektion",
            formula="¬Kφ → K¬Kφ",
            natural_language="Wenn man etwas nicht weiß, weiß man, dass man es nicht weiß",
            examples=[
                "Wenn ich nicht weiß, ob es morgen regnet, dann weiß ich, dass ich es nicht weiß"
            ]
        )

        # D-Axiom (Glaubenskonsistenz)
        self.axioms["D"] = Axiom(
            id="D",
            category=AxiomCategory.KNOWLEDGE,
            name="Glaubenskonsistenz",
            formula="Bφ → ¬B¬φ",
            natural_language="Wenn man φ glaubt, glaubt man nicht gleichzeitig ¬φ",
            examples=[
                "Wenn ich glaube, dass es regnet, glaube ich nicht gleichzeitig, dass es nicht regnet"
            ]
        )

        # KB-Beziehung (Wissen impliziert Glauben)
        self.axioms["KB"] = Axiom(
            id="KB",
            category=AxiomCategory.KNOWLEDGE,
            name="Wissen-Glauben-Beziehung",
            formula="Kφ → Bφ",
            natural_language="Wissen impliziert Glauben: Wenn man etwas weiß, glaubt man es auch",
            examples=[
                "Wenn ich weiß, dass die Erde rund ist, glaube ich auch, dass die Erde rund ist"
            ]
        )

        # Gemeinsames Wissen (Common Knowledge)
        self.axioms["CK"] = Axiom(
            id="CK",
            category=AxiomCategory.KNOWLEDGE,
            name="Common Knowledge",
            formula="Cφ ↔ E(φ ∧ Cφ)",
            natural_language="Gemeinsames Wissen: Jeder weiß φ, und jeder weiß, dass jeder es weiß, ad infinitum",
            examples=[
                "Es ist gemeinsames Wissen, dass 1+1=2"
            ]
        )

        # Geschlossene-Welt-Annahme (Optional)
        self.axioms["CWA"] = Axiom(
            id="CWA",
            category=AxiomCategory.KNOWLEDGE,
            name="Closed World Assumption",
            formula="¬Kφ → K¬φ",
            natural_language="Was nicht bekannt ist, wird als falsch angenommen",
            is_fundamental=False,
            examples=[
                "Wenn in der Datenbank kein Flug steht, gibt es keinen Flug"
            ]
        )

    def create_agent(self, agent_name: str) -> KnowledgeState:
        """Erstellt einen neuen Agenten mit Wissenszustand"""
        state = KnowledgeState(agent=agent_name)
        self.knowledge_states[agent_name] = state
        return state

    def learn(self, agent: str, proposition: str, certainty: float = 1.0):
        """Agent lernt neue Information"""
        if agent not in self.knowledge_states:
            self.create_agent(agent)

        state = self.knowledge_states[agent]

        if certainty >= 0.95:
            # Wissen (hohe Gewissheit)
            state.known.add(proposition)
            state.believed.add(proposition)
        elif certainty >= 0.5:
            # Glauben (moderate Gewissheit)
            state.believed.add(proposition)
        else:
            # Ungewiss
            state.unknown.add(proposition)

        state.certainty[proposition] = certainty

    def knows(self, agent: str, proposition: str) -> bool:
        """Prüft ob Agent etwas weiß (K-Operator)"""
        if agent not in self.knowledge_states:
            return False
        return proposition in self.knowledge_states[agent].known

    def believes(self, agent: str, proposition: str) -> bool:
        """Prüft ob Agent etwas glaubt (B-Operator)"""
        if agent not in self.knowledge_states:
            return False
        return proposition in self.knowledge_states[agent].believed

    def common_knowledge(self, proposition: str) -> bool:
        """Prüft ob etwas gemeinsames Wissen ist"""
        if not self.knowledge_states:
            return False
        return all(proposition in state.known
                   for state in self.knowledge_states.values())

    def verify_axiom(self, axiom_id: str, agent: str,
                      phi: str, psi: str = None) -> Tuple[bool, str]:
        """Verifiziert ein Axiom für gegebene Propositionen"""
        if axiom_id not in self.axioms:
            return False, f"Axiom {axiom_id} nicht gefunden"

        axiom = self.axioms[axiom_id]
        state = self.knowledge_states.get(agent)

        if not state:
            return False, f"Agent {agent} nicht gefunden"

        if axiom_id == "T":
            # Kφ → φ: Wenn gewusst, dann wahr
            if self.knows(agent, phi):
                return True, f"Agent {agent} weiß {phi}, also ist {phi} wahr"
            return True, f"Agent {agent} weiß {phi} nicht - Axiom trivial erfüllt"

        elif axiom_id == "K":
            # K(φ → ψ) → (Kφ → Kψ)
            if psi is None:
                return False, "Benötigt zwei Propositionen für K-Axiom"
            impl = f"{phi} → {psi}"
            if self.knows(agent, impl) and self.knows(agent, phi):
                if self.knows(agent, psi):
                    return True, f"K-Axiom erfüllt: {agent} weiß {psi}"
                return False, f"K-Axiom verletzt: {agent} sollte {psi} wissen"
            return True, "Prämissen nicht erfüllt - Axiom trivial erfüllt"

        elif axiom_id == "4":
            # Kφ → KKφ
            if self.knows(agent, phi):
                meta = f"K({phi})"
                self.learn(agent, meta, 1.0)  # Positive Introspektion
                return True, f"Agent {agent} weiß nun, dass er {phi} weiß"
            return True, "Agent weiß φ nicht - Axiom trivial erfüllt"

        return True, "Axiom-Verifikation nicht implementiert für dieses Axiom"


# =============================================================================
# 2. LOGIK-AXIOME (Klassische & Nicht-klassische)
# =============================================================================

class LogicAxioms:
    """
    Klassische und modale Logik-Axiome.

    Aussagenlogik:
    - Identität, Widerspruchsfreiheit, Ausgeschlossenes Drittes
    - Schlussregeln: Modus Ponens, Modus Tollens, etc.

    Modallogik:
    - Notwendigkeit (□) und Möglichkeit (◇)
    - K, T, 4, 5 Axiome
    """

    def __init__(self):
        self.axioms: Dict[str, Axiom] = {}
        self.theorems: List[Formula] = []
        self.propositions: Dict[str, Proposition] = {}
        self._initialize_axioms()

    def _initialize_axioms(self):
        """Initialisiert die logischen Grundaxiome"""

        # === AUSSAGENLOGIK ===

        # Identitätsprinzip
        self.axioms["IDENTITY"] = Axiom(
            id="IDENTITY",
            category=AxiomCategory.LOGIC,
            name="Identitätsprinzip",
            formula="A → A",
            natural_language="Jede Aussage impliziert sich selbst",
            examples=["Es regnet → Es regnet"]
        )

        # Satz vom Widerspruch
        self.axioms["NON_CONTRADICTION"] = Axiom(
            id="NON_CONTRADICTION",
            category=AxiomCategory.LOGIC,
            name="Satz vom Widerspruch",
            formula="¬(A ∧ ¬A)",
            natural_language="Eine Aussage kann nicht gleichzeitig wahr und falsch sein",
            examples=["Es kann nicht gleichzeitig regnen und nicht regnen"]
        )

        # Satz vom ausgeschlossenen Dritten
        self.axioms["EXCLUDED_MIDDLE"] = Axiom(
            id="EXCLUDED_MIDDLE",
            category=AxiomCategory.LOGIC,
            name="Satz vom ausgeschlossenen Dritten",
            formula="A ∨ ¬A",
            natural_language="Jede Aussage ist entweder wahr oder falsch",
            examples=["Entweder es regnet oder es regnet nicht"]
        )

        # Doppelte Negation
        self.axioms["DOUBLE_NEGATION"] = Axiom(
            id="DOUBLE_NEGATION",
            category=AxiomCategory.LOGIC,
            name="Doppelte Negation",
            formula="¬¬A ↔ A",
            natural_language="Die Verneinung einer Verneinung ergibt die ursprüngliche Aussage",
            examples=["'Es ist nicht der Fall, dass es nicht regnet' = 'Es regnet'"]
        )

        # Kontraposition
        self.axioms["CONTRAPOSITION"] = Axiom(
            id="CONTRAPOSITION",
            category=AxiomCategory.LOGIC,
            name="Kontraposition",
            formula="(A → B) ↔ (¬B → ¬A)",
            natural_language="Eine Implikation ist äquivalent zu ihrer Kontraposition",
            examples=["'Wenn es regnet, ist die Straße nass' ↔ 'Wenn die Straße trocken ist, regnet es nicht'"]
        )

        # De Morgansche Gesetze
        self.axioms["DE_MORGAN_1"] = Axiom(
            id="DE_MORGAN_1",
            category=AxiomCategory.LOGIC,
            name="De Morgan 1",
            formula="¬(A ∧ B) ↔ (¬A ∨ ¬B)",
            natural_language="Die Negation einer Konjunktion ist die Disjunktion der Negationen",
            examples=["'Nicht (A und B)' = 'Nicht-A oder Nicht-B'"]
        )

        self.axioms["DE_MORGAN_2"] = Axiom(
            id="DE_MORGAN_2",
            category=AxiomCategory.LOGIC,
            name="De Morgan 2",
            formula="¬(A ∨ B) ↔ (¬A ∧ ¬B)",
            natural_language="Die Negation einer Disjunktion ist die Konjunktion der Negationen",
            examples=["'Nicht (A oder B)' = 'Nicht-A und Nicht-B'"]
        )

        # === MODALLOGIK ===

        # Dualität von □ und ◇
        self.axioms["MODAL_DUALITY"] = Axiom(
            id="MODAL_DUALITY",
            category=AxiomCategory.LOGIC,
            name="Modale Dualität",
            formula="□A ↔ ¬◇¬A",
            natural_language="Notwendig A ≡ Nicht-möglich Nicht-A",
            examples=["'Es ist notwendig, dass 2+2=4' ↔ 'Es ist nicht möglich, dass 2+2≠4'"]
        )

        # Necessitation Rule
        self.axioms["NECESSITATION"] = Axiom(
            id="NECESSITATION",
            category=AxiomCategory.LOGIC,
            name="Necessitation",
            formula="⊢ A ⇒ ⊢ □A",
            natural_language="Wenn A ein Theorem ist, dann ist □A auch ein Theorem",
            examples=["Da '2+2=4' ein Theorem ist, ist '□(2+2=4)' auch ein Theorem"]
        )

        # K-Axiom (Modal)
        self.axioms["K_MODAL"] = Axiom(
            id="K_MODAL",
            category=AxiomCategory.LOGIC,
            name="K-Axiom (Modal)",
            formula="□(A → B) → (□A → □B)",
            natural_language="Notwendigkeit distribuiert über Implikation",
            examples=["Wenn notwendig (A → B) und notwendig A, dann notwendig B"]
        )

    def add_proposition(self, symbol: str, content: str,
                        truth_value: TruthValue = TruthValue.UNKNOWN) -> Proposition:
        """Fügt eine Proposition hinzu"""
        prop = Proposition(symbol=symbol, content=content, truth_value=truth_value)
        self.propositions[symbol] = prop
        return prop

    def evaluate(self, formula: str, assignment: Dict[str, bool]) -> TruthValue:
        """
        Evaluiert eine Formel unter einer Belegung.

        Args:
            formula: z.B. "P ∧ Q", "P → Q"
            assignment: {"P": True, "Q": False}
        """
        # Normalisiere Formel
        expr = formula
        for symbol, value in assignment.items():
            expr = expr.replace(symbol, str(value))

        # Ersetze logische Operatoren durch Python-Äquivalente
        expr = expr.replace("∧", " and ")
        expr = expr.replace("∨", " or ")
        expr = expr.replace("¬", " not ")
        expr = expr.replace("→", " <= ")  # Implikation: A→B ≡ ¬A∨B ≡ A≤B
        expr = expr.replace("↔", " == ")

        try:
            result = eval(expr)
            return TruthValue.TRUE if result else TruthValue.FALSE
        except Exception as e:
            logger.error(f"Fehler bei Evaluation: {e}")
            return TruthValue.UNKNOWN

    def apply_inference(self, rule: InferenceRule,
                        premises: List[str]) -> Optional[Inference]:
        """
        Wendet eine Schlussregel an.
        """
        if rule == InferenceRule.MODUS_PONENS:
            # A, A→B ⊢ B
            if len(premises) >= 2:
                # Finde Implikation
                for i, p1 in enumerate(premises):
                    if "→" in p1:
                        parts = p1.split("→")
                        if len(parts) == 2:
                            antecedent = parts[0].strip()
                            consequent = parts[1].strip()
                            # Prüfe ob Antecedent in anderen Prämissen
                            for j, p2 in enumerate(premises):
                                if i != j and p2.strip() == antecedent:
                                    return Inference(
                                        rule=rule,
                                        premises=premises,
                                        conclusion=consequent,
                                        explanation=f"Aus '{antecedent}' und '{p1}' folgt '{consequent}'"
                                    )

        elif rule == InferenceRule.MODUS_TOLLENS:
            # ¬B, A→B ⊢ ¬A
            if len(premises) >= 2:
                for p1 in premises:
                    if "→" in p1:
                        parts = p1.split("→")
                        if len(parts) == 2:
                            antecedent = parts[0].strip()
                            consequent = parts[1].strip()
                            neg_consequent = f"¬{consequent}"
                            for p2 in premises:
                                if p2.strip() == neg_consequent or p2.strip() == f"¬({consequent})":
                                    conclusion = f"¬{antecedent}"
                                    return Inference(
                                        rule=rule,
                                        premises=premises,
                                        conclusion=conclusion,
                                        explanation=f"Aus '{neg_consequent}' und '{p1}' folgt '{conclusion}'"
                                    )

        elif rule == InferenceRule.CONJUNCTION:
            # A, B ⊢ A∧B
            if len(premises) >= 2:
                conclusion = " ∧ ".join(premises)
                return Inference(
                    rule=rule,
                    premises=premises,
                    conclusion=conclusion,
                    explanation=f"Aus {premises} folgt die Konjunktion '{conclusion}'"
                )

        elif rule == InferenceRule.SIMPLIFICATION:
            # A∧B ⊢ A
            if len(premises) >= 1 and "∧" in premises[0]:
                parts = premises[0].split("∧")
                conclusion = parts[0].strip()
                return Inference(
                    rule=rule,
                    premises=premises,
                    conclusion=conclusion,
                    explanation=f"Aus '{premises[0]}' folgt '{conclusion}'"
                )

        return None

    def is_tautology(self, formula: str, variables: List[str]) -> bool:
        """Prüft ob eine Formel eine Tautologie ist"""
        from itertools import product

        for values in product([True, False], repeat=len(variables)):
            assignment = dict(zip(variables, values))
            result = self.evaluate(formula, assignment)
            if result != TruthValue.TRUE:
                return False
        return True

    def is_contradiction(self, formula: str, variables: List[str]) -> bool:
        """Prüft ob eine Formel eine Kontradiktion ist"""
        from itertools import product

        for values in product([True, False], repeat=len(variables)):
            assignment = dict(zip(variables, values))
            result = self.evaluate(formula, assignment)
            if result == TruthValue.TRUE:
                return False
        return True


# =============================================================================
# 3. ETHIK-AXIOME (Deontische Logik)
# =============================================================================

class EthicsAxioms:
    """
    Deontische Axiome für ethisches Reasoning.

    Operatoren:
    - O(φ): Es ist geboten/verpflichtend, dass φ
    - P(φ): Es ist erlaubt, dass φ
    - F(φ): Es ist verboten, dass φ

    Standard Deontische Logik (SDL):
    F(φ) ↔ O(¬φ) ↔ ¬P(φ)
    """

    def __init__(self):
        self.axioms: Dict[str, Axiom] = {}
        self.norms: List[Dict] = []
        self.ethical_principles: List[str] = []
        self._initialize_axioms()

    def _initialize_axioms(self):
        """Initialisiert die deontischen Grundaxiome"""

        # Deontische Dualität
        self.axioms["DEONTIC_DUALITY"] = Axiom(
            id="DEONTIC_DUALITY",
            category=AxiomCategory.ETHICS,
            name="Deontische Dualität",
            formula="O(φ) ↔ ¬P(¬φ)",
            natural_language="Geboten φ ≡ Nicht erlaubt Nicht-φ",
            examples=["'Du sollst nicht lügen' ↔ 'Es ist nicht erlaubt zu lügen'"]
        )

        # Verbot-Definition
        self.axioms["FORBIDDEN_DEF"] = Axiom(
            id="FORBIDDEN_DEF",
            category=AxiomCategory.ETHICS,
            name="Definition von Verbot",
            formula="F(φ) ↔ O(¬φ)",
            natural_language="Verboten φ ≡ Geboten Nicht-φ",
            examples=["'Lügen ist verboten' ↔ 'Es ist geboten, nicht zu lügen'"]
        )

        # D-Axiom (Deontische Konsistenz)
        self.axioms["D_DEONTIC"] = Axiom(
            id="D_DEONTIC",
            category=AxiomCategory.ETHICS,
            name="Deontische Konsistenz",
            formula="O(φ) → P(φ)",
            natural_language="Was geboten ist, ist auch erlaubt (Ought implies Can)",
            examples=["Wenn du die Wahrheit sagen sollst, dann darfst du sie auch sagen"]
        )

        # K-Axiom (Deontisch)
        self.axioms["K_DEONTIC"] = Axiom(
            id="K_DEONTIC",
            category=AxiomCategory.ETHICS,
            name="Deontisches K-Axiom",
            formula="O(φ → ψ) → (O(φ) → O(ψ))",
            natural_language="Pflicht distribuiert über Implikation",
            examples=["Wenn du verpflichtet bist: (A impliziert B) und verpflichtet zu A, dann auch zu B"]
        )

        # Keine Pflicht zum Unmöglichen
        self.axioms["OUGHT_CAN"] = Axiom(
            id="OUGHT_CAN",
            category=AxiomCategory.ETHICS,
            name="Ought Implies Can",
            formula="O(φ) → ◇φ",
            natural_language="Wenn φ geboten ist, muss φ auch möglich sein",
            examples=["Man kann nur verpflichtet sein zu etwas, das man auch tun kann"]
        )

        # Universalisierbarkeit (Kant)
        self.axioms["UNIVERSALIZABILITY"] = Axiom(
            id="UNIVERSALIZABILITY",
            category=AxiomCategory.ETHICS,
            name="Universalisierbarkeit",
            formula="O_a(φ) → ∀x O_x(φ)",
            natural_language="Was für einen geboten ist, sollte für alle unter gleichen Umständen gelten",
            examples=["Wenn ich nicht lügen soll, dann soll niemand lügen (ceteris paribus)"]
        )

        # Prima Facie vs. All-Things-Considered
        self.axioms["PRIMA_FACIE"] = Axiom(
            id="PRIMA_FACIE",
            category=AxiomCategory.ETHICS,
            name="Prima Facie Pflicht",
            formula="O_pf(φ) ∧ O_pf(ψ) ∧ ¬◇(φ ∧ ψ) → Override(φ, ψ) ∨ Override(ψ, φ)",
            natural_language="Bei konfligierenden Prima-Facie-Pflichten muss eine die andere überwiegen",
            examples=["Wahrheit vs. Schutz: Eine Pflicht kann die andere in einem Konflikt überwiegen"]
        )

        # Goldene Regel
        self.axioms["GOLDEN_RULE"] = Axiom(
            id="GOLDEN_RULE",
            category=AxiomCategory.ETHICS,
            name="Goldene Regel",
            formula="O(Do(a, φ, b)) → O(Accept(a, Do(x, φ, a)))",
            natural_language="Handle so, wie du auch von anderen behandelt werden möchtest",
            examples=["Wenn du andere respektierst, solltest du akzeptieren, selbst respektiert zu werden"]
        )

        # Schaden-Prinzip (Mill)
        self.axioms["HARM_PRINCIPLE"] = Axiom(
            id="HARM_PRINCIPLE",
            category=AxiomCategory.ETHICS,
            name="Schadensprinzip",
            formula="P(φ) ↔ ¬Harm(φ, others)",
            natural_language="Eine Handlung ist erlaubt, solange sie anderen nicht schadet",
            examples=["Freiheit ist erlaubt, solange sie die Freiheit anderer nicht einschränkt"]
        )

    def add_norm(self, action: str, deontic_status: str,
                  conditions: List[str] = None, priority: int = 1) -> Dict:
        """
        Fügt eine Norm zum System hinzu.

        Args:
            action: Die Handlung
            deontic_status: "obligatory", "permitted", "forbidden"
            conditions: Bedingungen unter denen die Norm gilt
            priority: Priorität bei Konflikten (höher = wichtiger)
        """
        norm = {
            "action": action,
            "status": deontic_status,
            "conditions": conditions or [],
            "priority": priority,
            "added": datetime.now().isoformat()
        }
        self.norms.append(norm)
        return norm

    def evaluate_action(self, action: str,
                         context: Dict[str, bool] = None) -> Dict[str, Any]:
        """
        Bewertet eine Handlung ethisch.

        Args:
            action: Die zu bewertende Handlung
            context: Kontextbedingungen

        Returns:
            Ethische Bewertung
        """
        context = context or {}
        applicable_norms = []

        for norm in self.norms:
            # Prüfe ob Bedingungen erfüllt
            conditions_met = all(
                context.get(cond, False)
                for cond in norm["conditions"]
            ) if norm["conditions"] else True

            if conditions_met and norm["action"].lower() in action.lower():
                applicable_norms.append(norm)

        if not applicable_norms:
            return {
                "action": action,
                "status": "permitted",  # Default: Erlaubt wenn nicht explizit verboten
                "reasoning": "Keine anwendbaren Normen gefunden - permissive default",
                "confidence": 0.5
            }

        # Sortiere nach Priorität
        applicable_norms.sort(key=lambda n: n["priority"], reverse=True)
        primary_norm = applicable_norms[0]

        # Prüfe auf Konflikte
        conflicts = []
        for norm in applicable_norms[1:]:
            if norm["status"] != primary_norm["status"]:
                conflicts.append(norm)

        return {
            "action": action,
            "status": primary_norm["status"],
            "primary_norm": primary_norm,
            "conflicts": conflicts,
            "reasoning": f"Basierend auf Norm: {primary_norm['action']} ist {primary_norm['status']}",
            "confidence": 0.9 if not conflicts else 0.6
        }

    def check_consistency(self) -> Tuple[bool, List[str]]:
        """Prüft die Konsistenz der Normen"""
        issues = []

        # Prüfe D-Axiom: O(φ) → P(φ)
        for norm in self.norms:
            if norm["status"] == "obligatory":
                # Suche nach widersprüchlichen Verboten
                for other in self.norms:
                    if (other["action"] == norm["action"] and
                        other["status"] == "forbidden" and
                        other["conditions"] == norm["conditions"]):
                        issues.append(
                            f"Inkonsistenz: '{norm['action']}' ist sowohl geboten als auch verboten"
                        )

        # Prüfe Widerspruchsfreiheit
        for norm in self.norms:
            if norm["status"] == "forbidden":
                for other in self.norms:
                    if (other["action"] == norm["action"] and
                        other["status"] == "permitted" and
                        other["conditions"] == norm["conditions"] and
                        other["priority"] == norm["priority"]):
                        issues.append(
                            f"Inkonsistenz: '{norm['action']}' ist sowohl verboten als auch erlaubt (gleiche Priorität)"
                        )

        return len(issues) == 0, issues


# =============================================================================
# 4. LERN-AXIOME
# =============================================================================

class LearningAxioms:
    """
    Axiome für adaptives Lernen.

    Formalisiert:
    - Wie Wissen erworben wird
    - Wie Überzeugungen aktualisiert werden
    - Wie aus Erfahrung gelernt wird
    """

    def __init__(self):
        self.axioms: Dict[str, Axiom] = {}
        self.learning_history: List[Dict] = []
        self.belief_updates: List[Dict] = []
        self._initialize_axioms()

    def _initialize_axioms(self):
        """Initialisiert die Lern-Axiome"""

        # Konditionalisierung (Bayesianisches Update)
        self.axioms["CONDITIONALIZATION"] = Axiom(
            id="CONDITIONALIZATION",
            category=AxiomCategory.LEARNING,
            name="Bayesianische Konditionalisierung",
            formula="P_new(H) = P_old(H|E) wenn E beobachtet",
            natural_language="Die neue Überzeugung in H nach Beobachtung von E ist die alte bedingte Wahrscheinlichkeit",
            examples=["Nach Beobachtung von Symptom E wird P(Krankheit) zu P(Krankheit|Symptom)"]
        )

        # Prinzip der totalen Evidenz
        self.axioms["TOTAL_EVIDENCE"] = Axiom(
            id="TOTAL_EVIDENCE",
            category=AxiomCategory.LEARNING,
            name="Prinzip der totalen Evidenz",
            formula="∀e ∈ Evidence: Consider(e) in Update",
            natural_language="Bei der Aktualisierung muss alle verfügbare Evidenz berücksichtigt werden",
            examples=["Ignoriere nicht unangenehme Daten - berücksichtige alle Beobachtungen"]
        )

        # Konservativismus
        self.axioms["CONSERVATISM"] = Axiom(
            id="CONSERVATISM",
            category=AxiomCategory.LEARNING,
            name="Konservativismus",
            formula="¬E → P_new(H) = P_old(H)",
            natural_language="Ohne neue Evidenz ändere deine Überzeugungen nicht",
            examples=["Wenn nichts Neues gelernt wird, behalte die alten Überzeugungen"]
        )

        # Regularität
        self.axioms["REGULARITY"] = Axiom(
            id="REGULARITY",
            category=AxiomCategory.LEARNING,
            name="Regularität",
            formula="P(φ) > 0 für alle logisch möglichen φ",
            natural_language="Schließe keine logisch möglichen Hypothesen a priori aus",
            examples=["Jede Hypothese verdient mindestens minimale Anfangswahrscheinlichkeit"]
        )

        # Lernen aus Beispielen
        self.axioms["INDUCTIVE_LEARNING"] = Axiom(
            id="INDUCTIVE_LEARNING",
            category=AxiomCategory.LEARNING,
            name="Induktives Lernen",
            formula="∀i P(φ|e_i) > P(φ|e_{i-1}) wenn e_i bestätigt φ",
            natural_language="Jedes bestätigende Beispiel erhöht die Überzeugung",
            examples=["Jeder weiße Schwan, den ich sehe, erhöht meine Überzeugung, dass alle Schwäne weiß sind"]
        )

        # Vergessen (kontrolliert)
        self.axioms["FORGETTING"] = Axiom(
            id="FORGETTING",
            category=AxiomCategory.LEARNING,
            name="Kontrolliertes Vergessen",
            formula="Relevance(φ, t) < θ → Decay(P(φ))",
            natural_language="Nicht-relevantes Wissen kann mit der Zeit verblassen",
            examples=["Veraltete Information verliert an Gewicht in der Wissensbasis"]
        )

        # Transfer Learning
        self.axioms["TRANSFER"] = Axiom(
            id="TRANSFER",
            category=AxiomCategory.LEARNING,
            name="Transfer Learning",
            formula="Similarity(D_1, D_2) > θ → Knowledge(D_1) applies_to D_2",
            natural_language="Wissen aus ähnlichen Domänen kann übertragen werden",
            examples=["Wissen über Katzen hilft beim Verstehen von Hunden"]
        )

        # Curiosity-Driven Learning
        self.axioms["CURIOSITY"] = Axiom(
            id="CURIOSITY",
            category=AxiomCategory.LEARNING,
            name="Neugier-Axiom",
            formula="High_Entropy(φ) → Prioritize_Learning(φ)",
            natural_language="Priorisiere das Lernen von unsicherem Wissen",
            examples=["Fokussiere auf Bereiche, in denen du am wenigsten weißt"]
        )

        # Meta-Learning
        self.axioms["META_LEARNING"] = Axiom(
            id="META_LEARNING",
            category=AxiomCategory.LEARNING,
            name="Meta-Lernen",
            formula="Optimize(Learning_Strategy) based_on Performance_History",
            natural_language="Lerne, wie du am besten lernst",
            examples=["Wenn visuelle Beispiele besser funktionieren, nutze mehr davon"]
        )

    def record_learning_event(self, topic: str, evidence: str,
                               prior: float, posterior: float,
                               method: str = "conditionalization") -> Dict:
        """Zeichnet ein Lernereignis auf"""
        event = {
            "topic": topic,
            "evidence": evidence,
            "prior": prior,
            "posterior": posterior,
            "method": method,
            "timestamp": datetime.now().isoformat(),
            "change": posterior - prior
        }
        self.learning_history.append(event)
        return event

    def bayesian_update(self, prior: float, likelihood: float,
                         evidence_probability: float) -> float:
        """
        Führt ein Bayesianisches Update durch.

        P(H|E) = P(E|H) * P(H) / P(E)
        """
        if evidence_probability == 0:
            return prior

        posterior = (likelihood * prior) / evidence_probability
        return max(0.0, min(1.0, posterior))

    def calculate_information_gain(self, prior_entropy: float,
                                     posterior_entropy: float) -> float:
        """Berechnet den Informationsgewinn"""
        return max(0.0, prior_entropy - posterior_entropy)

    def get_learning_summary(self) -> Dict[str, Any]:
        """Gibt eine Zusammenfassung der Lernhistorie"""
        if not self.learning_history:
            return {"events": 0, "total_change": 0.0}

        total_change = sum(e["change"] for e in self.learning_history)
        avg_change = total_change / len(self.learning_history)

        topics = {}
        for event in self.learning_history:
            topic = event["topic"]
            if topic not in topics:
                topics[topic] = []
            topics[topic].append(event["posterior"])

        return {
            "events": len(self.learning_history),
            "total_change": total_change,
            "avg_change": avg_change,
            "topics": {t: {"current": vals[-1], "changes": len(vals)}
                      for t, vals in topics.items()}
        }


# =============================================================================
# KOMBINIERTES AXIOM-SYSTEM
# =============================================================================

class FormalAxiomSystem:
    """
    Kombiniertes formales Axiom-System.
    """

    def __init__(self):
        self.epistemic = EpistemicAxioms()
        self.logic = LogicAxioms()
        self.ethics = EthicsAxioms()
        self.learning = LearningAxioms()

        self.all_axioms: Dict[str, Axiom] = {}
        self._collect_all_axioms()

    def _collect_all_axioms(self):
        """Sammelt alle Axiome"""
        for aid, axiom in self.epistemic.axioms.items():
            self.all_axioms[f"EPISTEMIC_{aid}"] = axiom

        for aid, axiom in self.logic.axioms.items():
            self.all_axioms[f"LOGIC_{aid}"] = axiom

        for aid, axiom in self.ethics.axioms.items():
            self.all_axioms[f"ETHICS_{aid}"] = axiom

        for aid, axiom in self.learning.axioms.items():
            self.all_axioms[f"LEARNING_{aid}"] = axiom

    def get_axiom(self, axiom_id: str) -> Optional[Axiom]:
        """Gibt ein Axiom nach ID zurück"""
        return self.all_axioms.get(axiom_id)

    def list_axioms_by_category(self, category: AxiomCategory) -> List[Axiom]:
        """Listet alle Axiome einer Kategorie"""
        return [a for a in self.all_axioms.values() if a.category == category]

    def verify_consistency(self) -> Tuple[bool, List[str]]:
        """Verifiziert die Konsistenz des gesamten Systems"""
        issues = []

        # Ethik-Konsistenz
        ethics_consistent, ethics_issues = self.ethics.check_consistency()
        if not ethics_consistent:
            issues.extend(ethics_issues)

        # Weitere Konsistenzprüfungen können hier hinzugefügt werden

        return len(issues) == 0, issues

    def reason(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Führt formales Reasoning auf einer Anfrage durch.
        """
        context = context or {}
        result = {
            "query": query,
            "applicable_axioms": [],
            "inferences": [],
            "conclusion": "",
            "confidence": 0.5
        }

        # Identifiziere relevante Axiome
        query_lower = query.lower()

        if any(kw in query_lower for kw in ["weiß", "wissen", "know", "believe", "glauben"]):
            result["applicable_axioms"].extend(
                self.list_axioms_by_category(AxiomCategory.KNOWLEDGE)
            )

        if any(kw in query_lower for kw in ["soll", "darf", "muss", "erlaubt", "verboten"]):
            result["applicable_axioms"].extend(
                self.list_axioms_by_category(AxiomCategory.ETHICS)
            )

        if any(kw in query_lower for kw in ["wenn", "dann", "oder", "und", "nicht", "folgt"]):
            result["applicable_axioms"].extend(
                self.list_axioms_by_category(AxiomCategory.LOGIC)
            )

        if any(kw in query_lower for kw in ["lernen", "update", "ändern", "anpassen"]):
            result["applicable_axioms"].extend(
                self.list_axioms_by_category(AxiomCategory.LEARNING)
            )

        # Vereinfachtes Reasoning
        if result["applicable_axioms"]:
            axiom_names = [a.name for a in result["applicable_axioms"][:3]]
            result["conclusion"] = f"Relevante Axiome: {', '.join(axiom_names)}"
            result["confidence"] = 0.7

        return result

    def get_summary(self) -> str:
        """Gibt eine Zusammenfassung des Axiom-Systems"""
        summary = ["=" * 60]
        summary.append("FORMAL AXIOM SYSTEM - Zusammenfassung")
        summary.append("=" * 60)

        summary.append(f"\nGesamtzahl Axiome: {len(self.all_axioms)}")

        for category in AxiomCategory:
            axioms = self.list_axioms_by_category(category)
            summary.append(f"\n--- {category.value.upper()} ({len(axioms)} Axiome) ---")
            for axiom in axioms[:3]:
                summary.append(f"  • {axiom.name}: {axiom.formula}")
            if len(axioms) > 3:
                summary.append(f"  ... und {len(axioms) - 3} weitere")

        # Konsistenzprüfung
        consistent, issues = self.verify_consistency()
        summary.append(f"\nKonsistenz: {'✓ Konsistent' if consistent else '✗ Inkonsistenzen gefunden'}")
        if issues:
            for issue in issues[:3]:
                summary.append(f"  ⚠ {issue}")

        return "\n".join(summary)


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_formal_axiom_system() -> FormalAxiomSystem:
    """Erstellt ein formales Axiom-System"""
    return FormalAxiomSystem()


# =============================================================================
# BEISPIEL / TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("📜 Formal Axiom System - Demo\n")

    system = create_formal_axiom_system()

    # Epistemisches Beispiel
    print("--- Epistemische Logik ---")
    system.epistemic.create_agent("Holo")
    system.epistemic.learn("Holo", "Die Erde ist rund", certainty=1.0)
    system.epistemic.learn("Holo", "Es wird morgen regnen", certainty=0.6)

    print(f"Holo weiß 'Erde ist rund': {system.epistemic.knows('Holo', 'Die Erde ist rund')}")
    print(f"Holo glaubt 'Regen morgen': {system.epistemic.believes('Holo', 'Es wird morgen regnen')}")

    # Verifikation des T-Axioms
    valid, reason = system.epistemic.verify_axiom("T", "Holo", "Die Erde ist rund")
    print(f"T-Axiom Verifikation: {valid} - {reason}")

    # Logik-Beispiel
    print("\n--- Klassische Logik ---")
    result = system.logic.evaluate("P ∧ Q", {"P": True, "Q": True})
    print(f"P ∧ Q (P=True, Q=True): {result.value}")

    result = system.logic.evaluate("P → Q", {"P": True, "Q": False})
    print(f"P → Q (P=True, Q=False): {result.value}")

    # Tautologie-Prüfung
    is_taut = system.logic.is_tautology("P ∨ ¬P", ["P"])
    print(f"'P ∨ ¬P' ist Tautologie: {is_taut}")

    # Modus Ponens
    inference = system.logic.apply_inference(
        InferenceRule.MODUS_PONENS,
        ["P", "P → Q"]
    )
    if inference:
        print(f"Modus Ponens: {inference.explanation}")

    # Ethik-Beispiel
    print("\n--- Deontische Logik ---")
    system.ethics.add_norm("lügen", "forbidden", priority=2)
    system.ethics.add_norm("helfen", "obligatory", priority=1)
    system.ethics.add_norm("spielen", "permitted", priority=1)

    eval_result = system.ethics.evaluate_action("lügen")
    print(f"Bewertung 'lügen': {eval_result['status']} ({eval_result['reasoning']})")

    consistent, issues = system.ethics.check_consistency()
    print(f"Normensystem konsistent: {consistent}")

    # Lern-Beispiel
    print("\n--- Lern-Axiome ---")
    # Bayesianisches Update
    prior = 0.3
    likelihood = 0.8
    evidence_prob = 0.5
    posterior = system.learning.bayesian_update(prior, likelihood, evidence_prob)
    print(f"Bayesian Update: P(H)={prior} → P(H|E)={posterior:.3f}")

    system.learning.record_learning_event(
        topic="Wetter",
        evidence="Dunkle Wolken beobachtet",
        prior=0.3,
        posterior=0.7
    )

    # Reasoning-Beispiel
    print("\n--- Kombiniertes Reasoning ---")
    reasoning_result = system.reason("Was darf ich wissen und was soll ich tun?")
    print(f"Anwendbare Axiome: {len(reasoning_result['applicable_axioms'])}")

    # Zusammenfassung
    print("\n" + system.get_summary())
