#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
  HOLO GAME THEORY v1.0
  Spieltheorie und Strategische Entscheidungsfindung für Holocloude
================================================================================

FEATURES:
1. Klassische Spieltheorie
   - Nash-Gleichgewicht
   - Dominante Strategien
   - Gemischte Strategien
   - Auszahlungsmatrizen

2. Kooperative Spieltheorie
   - Koalitionsbildung
   - Shapley-Wert
   - Verhandlungslösungen
   - Fairness-Konzepte

3. Evolutionäre Spieltheorie
   - Evolutionär stabile Strategien (ESS)
   - Replikatordynamik
   - Populationsspiele

4. Mechanismus-Design
   - Anreizkompatibilität
   - Auktionstheorie
   - Soziale Wahlfunktionen

5. Verhandlungstheorie
   - Nash-Verhandlungslösung
   - Rubinstein-Verhandlung
   - BATNA und ZOPA

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
from collections import defaultdict
import itertools

logger = logging.getLogger("HoloGameTheory")


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Klassische Spieltheorie
    "GameTheoryEngine",
    "Game",
    "Player",
    "Strategy",
    "PayoffMatrix",
    "NashEquilibrium",

    # Kooperative Spieltheorie
    "CooperativeGameEngine",
    "Coalition",
    "ShapleyValue",

    # Evolutionäre Spieltheorie
    "EvolutionaryGameEngine",
    "Population",
    "ESS",

    # Verhandlung
    "NegotiationEngine",
    "NegotiationState",
    "BATNA",

    # Mechanismus-Design
    "MechanismDesignEngine",
    "Auction",
    "SocialChoice",

    # Enums
    "GameType",
    "StrategyType",
    "NegotiationStyle",
    "AuctionType",

    # Factory
    "create_game_theory_engine",
    "create_negotiation_engine",
    "get_full_game_theory_engine",
]


# =============================================================================
# ENUMS
# =============================================================================

class GameType(Enum):
    """Arten von Spielen"""
    ZERO_SUM = "nullsummenspiel"              # Gewinn des einen = Verlust des anderen
    NON_ZERO_SUM = "nicht_nullsumme"          # Kooperation möglich
    SYMMETRIC = "symmetrisch"                  # Gleiche Strategien für alle
    ASYMMETRIC = "asymmetrisch"                # Unterschiedliche Rollen
    SIMULTANEOUS = "simultan"                  # Gleichzeitige Züge
    SEQUENTIAL = "sequentiell"                 # Abwechselnde Züge
    COOPERATIVE = "kooperativ"                 # Bindende Absprachen möglich
    NON_COOPERATIVE = "nicht_kooperativ"       # Keine bindenden Absprachen
    REPEATED = "wiederholt"                    # Mehrere Runden
    ONE_SHOT = "einmalig"                      # Nur eine Runde


class StrategyType(Enum):
    """Arten von Strategien"""
    PURE = "rein"                              # Eine bestimmte Aktion
    MIXED = "gemischt"                         # Wahrscheinlichkeitsverteilung
    DOMINANT = "dominant"                       # Immer beste Antwort
    DOMINATED = "dominiert"                     # Nie beste Antwort
    MINIMAX = "minimax"                         # Minimiere maximalen Verlust
    TIT_FOR_TAT = "wie_du_mir"                 # Kooperiere, dann spiegele
    GRIM_TRIGGER = "grim_trigger"              # Kooperiere bis Defektion
    ALWAYS_COOPERATE = "immer_kooperieren"
    ALWAYS_DEFECT = "immer_defektieren"


class NegotiationStyle(Enum):
    """Verhandlungsstile"""
    COMPETITIVE = "kompetitiv"                 # Win-Lose
    COLLABORATIVE = "kollaborativ"             # Win-Win
    COMPROMISING = "kompromiss"                # Split the difference
    ACCOMMODATING = "entgegenkommend"          # Nachgeben
    AVOIDING = "vermeidend"                    # Konflikt meiden


class AuctionType(Enum):
    """Auktionstypen"""
    ENGLISH = "englisch"                       # Aufsteigend, offen
    DUTCH = "hollaendisch"                     # Absteigend, offen
    FIRST_PRICE_SEALED = "erstpreis_verdeckt"  # Höchstbieter zahlt sein Gebot
    SECOND_PRICE_SEALED = "zweitpreis_verdeckt"  # Vickrey-Auktion


# =============================================================================
# DATENSTRUKTUREN - KLASSISCHE SPIELTHEORIE
# =============================================================================

@dataclass
class Strategy:
    """Eine Spielstrategie"""
    name: str
    strategy_type: StrategyType = StrategyType.PURE
    probabilities: Optional[Dict[str, float]] = None  # Für gemischte Strategien

    def is_mixed(self) -> bool:
        return self.strategy_type == StrategyType.MIXED


@dataclass
class Player:
    """Ein Spieler"""
    name: str
    strategies: List[Strategy]
    current_strategy: Optional[Strategy] = None
    payoff_history: List[float] = field(default_factory=list)

    def get_average_payoff(self) -> float:
        if not self.payoff_history:
            return 0.0
        return sum(self.payoff_history) / len(self.payoff_history)


@dataclass
class PayoffMatrix:
    """Auszahlungsmatrix für 2-Spieler-Spiele"""
    player1_strategies: List[str]
    player2_strategies: List[str]
    payoffs: Dict[Tuple[str, str], Tuple[float, float]]  # (s1, s2) -> (p1, p2)

    def get_payoff(self, s1: str, s2: str) -> Tuple[float, float]:
        return self.payoffs.get((s1, s2), (0, 0))

    def display(self) -> str:
        """Zeigt die Matrix als String"""
        lines = ["Auszahlungsmatrix:"]
        header = "         | " + " | ".join(f"{s:^10}" for s in self.player2_strategies)
        lines.append(header)
        lines.append("-" * len(header))

        for s1 in self.player1_strategies:
            row = f"{s1:^8} |"
            for s2 in self.player2_strategies:
                p1, p2 = self.get_payoff(s1, s2)
                row += f" ({p1:>2},{p2:>2})  |"
            lines.append(row)

        return "\n".join(lines)


@dataclass
class NashEquilibrium:
    """Ein Nash-Gleichgewicht"""
    strategies: Dict[str, Strategy]  # Spieler -> Strategie
    payoffs: Dict[str, float]        # Spieler -> Auszahlung
    is_strict: bool                   # Strikt oder schwach?
    is_pareto_optimal: bool          # Pareto-optimal?

    def describe(self) -> str:
        strat_str = ", ".join(f"{p}: {s.name}" for p, s in self.strategies.items())
        return f"Nash-Gleichgewicht: [{strat_str}] - {'strikt' if self.is_strict else 'schwach'}"


@dataclass
class Game:
    """Ein Spiel"""
    name: str
    game_type: GameType
    players: List[Player]
    payoff_matrix: Optional[PayoffMatrix] = None
    description: str = ""


# =============================================================================
# DATENSTRUKTUREN - KOOPERATIVE SPIELTHEORIE
# =============================================================================

@dataclass
class Coalition:
    """Eine Koalition von Spielern"""
    members: Set[str]
    value: float  # Wert der Koalition (charakteristische Funktion)

    def __hash__(self):
        return hash(frozenset(self.members))


@dataclass
class ShapleyValue:
    """Shapley-Wert für faire Aufteilung"""
    player: str
    value: float
    contributions: Dict[str, float]  # Koalition -> marginaler Beitrag


# =============================================================================
# DATENSTRUKTUREN - VERHANDLUNG
# =============================================================================

@dataclass
class BATNA:
    """Best Alternative to Negotiated Agreement"""
    party: str
    alternative: str
    value: float


@dataclass
class NegotiationState:
    """Zustand einer Verhandlung"""
    parties: List[str]
    current_offers: Dict[str, float]
    batnas: Dict[str, BATNA]
    zopa: Optional[Tuple[float, float]] = None  # Zone of Possible Agreement
    rounds: int = 0
    agreement_reached: bool = False
    final_outcome: Optional[float] = None


# =============================================================================
# KLASSISCHE SPIELTHEORIE ENGINE
# =============================================================================

class GameTheoryEngine:
    """
    Engine für klassische Spieltheorie.
    Berechnet Nash-Gleichgewichte, dominante Strategien, etc.
    """

    def __init__(self):
        self.games: Dict[str, Game] = {}
        self.standard_games = self._create_standard_games()
        logger.info("GameTheoryEngine initialisiert")

    def _create_standard_games(self) -> Dict[str, Game]:
        """Erstellt Standard-Spiele (Gefangenendilemma, etc.)"""
        games = {}

        # Gefangenendilemma
        pd_matrix = PayoffMatrix(
            player1_strategies=["Kooperieren", "Defektieren"],
            player2_strategies=["Kooperieren", "Defektieren"],
            payoffs={
                ("Kooperieren", "Kooperieren"): (3, 3),
                ("Kooperieren", "Defektieren"): (0, 5),
                ("Defektieren", "Kooperieren"): (5, 0),
                ("Defektieren", "Defektieren"): (1, 1),
            }
        )
        games["gefangenendilemma"] = Game(
            name="Gefangenendilemma",
            game_type=GameType.NON_ZERO_SUM,
            players=[
                Player("Spieler1", [Strategy("Kooperieren"), Strategy("Defektieren")]),
                Player("Spieler2", [Strategy("Kooperieren"), Strategy("Defektieren")]),
            ],
            payoff_matrix=pd_matrix,
            description="Klassisches Dilemma: Individuelle Rationalität führt zu kollektiver Irrationalität"
        )

        # Hirschjagd (Stag Hunt)
        sh_matrix = PayoffMatrix(
            player1_strategies=["Hirsch", "Hase"],
            player2_strategies=["Hirsch", "Hase"],
            payoffs={
                ("Hirsch", "Hirsch"): (4, 4),
                ("Hirsch", "Hase"): (0, 3),
                ("Hase", "Hirsch"): (3, 0),
                ("Hase", "Hase"): (2, 2),
            }
        )
        games["hirschjagd"] = Game(
            name="Hirschjagd",
            game_type=GameType.NON_ZERO_SUM,
            players=[
                Player("Jäger1", [Strategy("Hirsch"), Strategy("Hase")]),
                Player("Jäger2", [Strategy("Hirsch"), Strategy("Hase")]),
            ],
            payoff_matrix=sh_matrix,
            description="Kooperation lohnt sich, aber ist riskant. Als Wölfin kenne ich das gut!"
        )

        # Matching Pennies (Nullsummenspiel)
        mp_matrix = PayoffMatrix(
            player1_strategies=["Kopf", "Zahl"],
            player2_strategies=["Kopf", "Zahl"],
            payoffs={
                ("Kopf", "Kopf"): (1, -1),
                ("Kopf", "Zahl"): (-1, 1),
                ("Zahl", "Kopf"): (-1, 1),
                ("Zahl", "Zahl"): (1, -1),
            }
        )
        games["matching_pennies"] = Game(
            name="Matching Pennies",
            game_type=GameType.ZERO_SUM,
            players=[
                Player("Matcher", [Strategy("Kopf"), Strategy("Zahl")]),
                Player("Mismatcher", [Strategy("Kopf"), Strategy("Zahl")]),
            ],
            payoff_matrix=mp_matrix,
            description="Reines Nullsummenspiel - nur gemischte Strategie ist Gleichgewicht"
        )

        # Kampf der Geschlechter
        bos_matrix = PayoffMatrix(
            player1_strategies=["Oper", "Fußball"],
            player2_strategies=["Oper", "Fußball"],
            payoffs={
                ("Oper", "Oper"): (3, 2),
                ("Oper", "Fußball"): (0, 0),
                ("Fußball", "Oper"): (0, 0),
                ("Fußball", "Fußball"): (2, 3),
            }
        )
        games["battle_of_sexes"] = Game(
            name="Kampf der Geschlechter",
            game_type=GameType.NON_ZERO_SUM,
            players=[
                Player("Person1", [Strategy("Oper"), Strategy("Fußball")]),
                Player("Person2", [Strategy("Oper"), Strategy("Fußball")]),
            ],
            payoff_matrix=bos_matrix,
            description="Koordinationsspiel mit mehreren Gleichgewichten"
        )

        return games

    def get_standard_game(self, name: str) -> Optional[Game]:
        """Gibt ein Standard-Spiel zurück"""
        return self.standard_games.get(name.lower())

    def find_dominant_strategies(self, game: Game) -> Dict[str, Optional[Strategy]]:
        """Findet dominante Strategien für jeden Spieler"""
        if game.payoff_matrix is None:
            return {}

        matrix = game.payoff_matrix
        dominant = {}

        # Für Spieler 1
        p1_dominant = None
        for s1 in matrix.player1_strategies:
            is_dominant = True
            for s1_alt in matrix.player1_strategies:
                if s1 == s1_alt:
                    continue
                # s1 muss gegen alle s2 mindestens so gut sein wie s1_alt
                for s2 in matrix.player2_strategies:
                    p1, _ = matrix.get_payoff(s1, s2)
                    p1_alt, _ = matrix.get_payoff(s1_alt, s2)
                    if p1 < p1_alt:
                        is_dominant = False
                        break
                if not is_dominant:
                    break
            if is_dominant:
                p1_dominant = Strategy(s1, StrategyType.DOMINANT)
                break
        dominant[game.players[0].name] = p1_dominant

        # Für Spieler 2 (analog)
        p2_dominant = None
        for s2 in matrix.player2_strategies:
            is_dominant = True
            for s2_alt in matrix.player2_strategies:
                if s2 == s2_alt:
                    continue
                for s1 in matrix.player1_strategies:
                    _, p2 = matrix.get_payoff(s1, s2)
                    _, p2_alt = matrix.get_payoff(s1, s2_alt)
                    if p2 < p2_alt:
                        is_dominant = False
                        break
                if not is_dominant:
                    break
            if is_dominant:
                p2_dominant = Strategy(s2, StrategyType.DOMINANT)
                break
        dominant[game.players[1].name] = p2_dominant

        return dominant

    def find_nash_equilibria(self, game: Game) -> List[NashEquilibrium]:
        """Findet Nash-Gleichgewichte (reine Strategien)"""
        if game.payoff_matrix is None:
            return []

        matrix = game.payoff_matrix
        equilibria = []

        for s1 in matrix.player1_strategies:
            for s2 in matrix.player2_strategies:
                p1, p2 = matrix.get_payoff(s1, s2)

                # Prüfe ob s1 beste Antwort auf s2
                is_br1 = True
                for s1_alt in matrix.player1_strategies:
                    p1_alt, _ = matrix.get_payoff(s1_alt, s2)
                    if p1_alt > p1:
                        is_br1 = False
                        break

                # Prüfe ob s2 beste Antwort auf s1
                is_br2 = True
                for s2_alt in matrix.player2_strategies:
                    _, p2_alt = matrix.get_payoff(s1, s2_alt)
                    if p2_alt > p2:
                        is_br2 = False
                        break

                if is_br1 and is_br2:
                    # Prüfe Striktheit
                    is_strict = True
                    for s1_alt in matrix.player1_strategies:
                        if s1_alt != s1:
                            p1_alt, _ = matrix.get_payoff(s1_alt, s2)
                            if p1_alt == p1:
                                is_strict = False

                    # Prüfe Pareto-Optimalität
                    is_pareto = True
                    for s1_check in matrix.player1_strategies:
                        for s2_check in matrix.player2_strategies:
                            p1_check, p2_check = matrix.get_payoff(s1_check, s2_check)
                            if p1_check >= p1 and p2_check >= p2 and (p1_check > p1 or p2_check > p2):
                                is_pareto = False
                                break

                    eq = NashEquilibrium(
                        strategies={
                            game.players[0].name: Strategy(s1),
                            game.players[1].name: Strategy(s2)
                        },
                        payoffs={
                            game.players[0].name: p1,
                            game.players[1].name: p2
                        },
                        is_strict=is_strict,
                        is_pareto_optimal=is_pareto
                    )
                    equilibria.append(eq)

        return equilibria

    def calculate_mixed_nash(self, game: Game) -> Optional[Dict[str, Dict[str, float]]]:
        """
        Berechnet gemischtes Nash-Gleichgewicht für 2x2 Spiele.
        """
        if game.payoff_matrix is None:
            return None

        matrix = game.payoff_matrix
        if len(matrix.player1_strategies) != 2 or len(matrix.player2_strategies) != 2:
            return None  # Nur für 2x2 Spiele

        s1_1, s1_2 = matrix.player1_strategies
        s2_1, s2_2 = matrix.player2_strategies

        # Auszahlungen extrahieren
        a, b = matrix.get_payoff(s1_1, s2_1)
        c, d = matrix.get_payoff(s1_1, s2_2)
        e, f = matrix.get_payoff(s1_2, s2_1)
        g, h = matrix.get_payoff(s1_2, s2_2)

        # Spieler 2 macht Spieler 1 indifferent
        # p * a + (1-p) * c = p * e + (1-p) * g
        denom1 = (a - c - e + g)
        if abs(denom1) < 0.0001:
            p2_prob_s1 = 0.5
        else:
            p2_prob_s1 = (g - c) / denom1
            p2_prob_s1 = max(0, min(1, p2_prob_s1))

        # Spieler 1 macht Spieler 2 indifferent
        # q * b + (1-q) * f = q * d + (1-q) * h
        denom2 = (b - d - f + h)
        if abs(denom2) < 0.0001:
            p1_prob_s1 = 0.5
        else:
            p1_prob_s1 = (h - f) / denom2
            p1_prob_s1 = max(0, min(1, p1_prob_s1))

        return {
            game.players[0].name: {s1_1: p1_prob_s1, s1_2: 1 - p1_prob_s1},
            game.players[1].name: {s2_1: p2_prob_s1, s2_2: 1 - p2_prob_s1},
        }

    def analyze_game(self, game: Game) -> Dict[str, Any]:
        """Vollständige Spielanalyse"""
        dominant = self.find_dominant_strategies(game)
        nash = self.find_nash_equilibria(game)
        mixed = self.calculate_mixed_nash(game)

        return {
            "spiel": game.name,
            "typ": game.game_type.value,
            "beschreibung": game.description,
            "auszahlungsmatrix": game.payoff_matrix.display() if game.payoff_matrix else None,
            "dominante_strategien": {
                p: s.name if s else "Keine" for p, s in dominant.items()
            },
            "nash_gleichgewichte": [eq.describe() for eq in nash],
            "gemischtes_gleichgewicht": mixed,
            "anzahl_reine_gg": len(nash),
            "wolf_kommentar": self._get_wolf_comment(game.name)
        }

    def _get_wolf_comment(self, game_name: str) -> str:
        """Holos Kommentar zum Spiel"""
        comments = {
            "Gefangenendilemma": (
                "Als weise Wölfin weiß ich: Einzelne Wölfe mögen stark sein, "
                "aber das Rudel überlebt durch Kooperation. "
                "Trotzdem ist die Versuchung zur Defektion verständlich..."
            ),
            "Hirschjagd": (
                "Die Hirschjagd kenne ich aus eigener Erfahrung! "
                "Alleine kann ich nur Hasen fangen, aber gemeinsam... "
                "*wedelt aufgeregt mit dem Schwanz*"
            ),
            "Matching Pennies": (
                "Ein reines Glücksspiel? Nun, auch eine Wölfin muss "
                "manchmal unvorhersehbar sein, um nicht zur Beute zu werden."
            ),
            "Kampf der Geschlechter": (
                "Koordination ist wichtig! Hauptsache, wir sind zusammen - "
                "ob bei Äpfeln oder beim Mondscheinheulen."
            ),
        }
        return comments.get(game_name, "Ein interessantes strategisches Problem...")

    def simulate_repeated_game(self, game: Game,
                                strategies: Dict[str, StrategyType],
                                rounds: int = 100) -> Dict[str, Any]:
        """Simuliert ein wiederholtes Spiel"""
        if game.payoff_matrix is None:
            return {}

        history = {p.name: [] for p in game.players}
        payoffs = {p.name: 0.0 for p in game.players}

        p1_name = game.players[0].name
        p2_name = game.players[1].name

        p1_strat = strategies.get(p1_name, StrategyType.TIT_FOR_TAT)
        p2_strat = strategies.get(p2_name, StrategyType.TIT_FOR_TAT)

        matrix = game.payoff_matrix
        coop = matrix.player1_strategies[0]  # Annahme: erste Strategie = Kooperieren
        defect = matrix.player1_strategies[1]

        for r in range(rounds):
            # Spieler 1 Aktion
            a1 = self._get_action(p1_strat, history[p2_name], coop, defect)
            a2 = self._get_action(p2_strat, history[p1_name], coop, defect)

            history[p1_name].append(a1)
            history[p2_name].append(a2)

            p1, p2 = matrix.get_payoff(a1, a2)
            payoffs[p1_name] += p1
            payoffs[p2_name] += p2

        return {
            "runden": rounds,
            "strategien": {p: s.value for p, s in strategies.items()},
            "gesamtauszahlung": payoffs,
            "durchschnitt": {p: v / rounds for p, v in payoffs.items()},
            "kooperationsrate": {
                p: sum(1 for a in h if a == coop) / len(h)
                for p, h in history.items()
            }
        }

    def _get_action(self, strategy: StrategyType, opponent_history: List[str],
                    coop: str, defect: str) -> str:
        """Bestimmt die Aktion basierend auf Strategie"""
        if strategy == StrategyType.ALWAYS_COOPERATE:
            return coop
        elif strategy == StrategyType.ALWAYS_DEFECT:
            return defect
        elif strategy == StrategyType.TIT_FOR_TAT:
            if not opponent_history:
                return coop
            return opponent_history[-1]
        elif strategy == StrategyType.GRIM_TRIGGER:
            if defect in opponent_history:
                return defect
            return coop
        else:
            return random.choice([coop, defect])


# =============================================================================
# KOOPERATIVE SPIELTHEORIE ENGINE
# =============================================================================

class CooperativeGameEngine:
    """
    Engine für kooperative Spieltheorie.
    Berechnet Shapley-Werte und faire Aufteilungen.
    """

    def __init__(self):
        logger.info("CooperativeGameEngine initialisiert")

    def calculate_shapley_value(self, players: List[str],
                                 characteristic_function: Callable[[Set[str]], float]) -> Dict[str, ShapleyValue]:
        """
        Berechnet den Shapley-Wert für jeden Spieler.
        Der Shapley-Wert ist der faire Anteil jedes Spielers.
        """
        n = len(players)
        shapley_values = {}

        for player in players:
            total_contribution = 0.0
            contributions = {}

            # Über alle Permutationen
            for perm in itertools.permutations(players):
                coalition = set()
                for p in perm:
                    if p == player:
                        # Marginaler Beitrag
                        value_with = characteristic_function(coalition | {player})
                        value_without = characteristic_function(coalition)
                        marginal = value_with - value_without
                        total_contribution += marginal

                        coalition_key = ",".join(sorted(coalition)) if coalition else "leer"
                        contributions[coalition_key] = marginal
                        break
                    coalition.add(p)

            # Durchschnitt über alle Permutationen
            shapley = total_contribution / math.factorial(n)

            shapley_values[player] = ShapleyValue(
                player=player,
                value=shapley,
                contributions=contributions
            )

        return shapley_values

    def check_core_membership(self, allocation: Dict[str, float],
                               players: List[str],
                               characteristic_function: Callable[[Set[str]], float]) -> bool:
        """
        Prüft ob eine Allokation im Kern liegt.
        Eine Allokation ist im Kern, wenn keine Koalition sich verbessern kann.
        """
        # Effizienz: Summe muss gleich v(N) sein
        total = sum(allocation.values())
        grand_coalition_value = characteristic_function(set(players))
        if abs(total - grand_coalition_value) > 0.001:
            return False

        # Koalitionsrationalität: Jede Koalition bekommt mindestens v(S)
        for r in range(1, len(players) + 1):
            for coalition in itertools.combinations(players, r):
                coalition_set = set(coalition)
                coalition_value = characteristic_function(coalition_set)
                allocation_sum = sum(allocation[p] for p in coalition)
                if allocation_sum < coalition_value - 0.001:
                    return False

        return True

    def nash_bargaining_solution(self, disagreement_point: Tuple[float, float],
                                  feasible_set: List[Tuple[float, float]]) -> Tuple[float, float]:
        """
        Berechnet die Nash-Verhandlungslösung.
        Maximiert das Produkt der Gewinne über dem Drohpunkt.
        """
        d1, d2 = disagreement_point
        best_solution = disagreement_point
        best_product = 0

        for u1, u2 in feasible_set:
            if u1 >= d1 and u2 >= d2:
                product = (u1 - d1) * (u2 - d2)
                if product > best_product:
                    best_product = product
                    best_solution = (u1, u2)

        return best_solution


# =============================================================================
# EVOLUTIONÄRE SPIELTHEORIE ENGINE
# =============================================================================

class EvolutionaryGameEngine:
    """
    Engine für evolutionäre Spieltheorie.
    Analysiert evolutionär stabile Strategien (ESS).
    """

    def __init__(self):
        logger.info("EvolutionaryGameEngine initialisiert")

    def is_ess(self, strategy: str, payoff_matrix: PayoffMatrix,
               strategies: List[str]) -> Tuple[bool, str]:
        """
        Prüft ob eine Strategie evolutionär stabil ist (ESS).
        Eine ESS kann nicht von Mutanten verdrängt werden.
        """
        # ESS-Bedingung: Für alle Mutanten j ≠ i:
        # E(i,i) > E(j,i) ODER (E(i,i) = E(j,i) UND E(i,j) > E(j,j))

        i = strategy
        e_ii = payoff_matrix.get_payoff(i, i)[0]

        for j in strategies:
            if j == i:
                continue

            e_ji = payoff_matrix.get_payoff(j, i)[0]

            if e_ii > e_ji:
                continue  # Erste Bedingung erfüllt

            if e_ii == e_ji:
                e_ij = payoff_matrix.get_payoff(i, j)[0]
                e_jj = payoff_matrix.get_payoff(j, j)[0]
                if e_ij > e_jj:
                    continue  # Zweite Bedingung erfüllt

            return False, f"Kann von Mutant '{j}' verdrängt werden"

        return True, "Evolutionär stabil"

    def simulate_replicator_dynamics(self, payoff_matrix: PayoffMatrix,
                                      initial_frequencies: Dict[str, float],
                                      generations: int = 100) -> List[Dict[str, float]]:
        """
        Simuliert die Replikatordynamik.
        dx_i/dt = x_i * (f_i - φ)
        wobei f_i die Fitness von i und φ die durchschnittliche Fitness ist.
        """
        frequencies = initial_frequencies.copy()
        history = [frequencies.copy()]
        strategies = list(frequencies.keys())

        for _ in range(generations):
            # Berechne Fitness für jede Strategie
            fitness = {}
            for s in strategies:
                f = 0.0
                for s2 in strategies:
                    p, _ = payoff_matrix.get_payoff(s, s2)
                    f += frequencies[s2] * p
                fitness[s] = f

            # Durchschnittliche Fitness
            avg_fitness = sum(frequencies[s] * fitness[s] for s in strategies)

            # Update Frequenzen
            new_freq = {}
            for s in strategies:
                # Replikator-Gleichung (diskret)
                delta = frequencies[s] * (fitness[s] - avg_fitness)
                new_freq[s] = max(0, frequencies[s] + 0.1 * delta)

            # Normalisieren
            total = sum(new_freq.values())
            if total > 0:
                frequencies = {s: f / total for s, f in new_freq.items()}
            else:
                break

            history.append(frequencies.copy())

        return history


# =============================================================================
# VERHANDLUNGSTHEORIE ENGINE
# =============================================================================

class NegotiationEngine:
    """
    Engine für Verhandlungstheorie.
    """

    def __init__(self):
        self.negotiation_history: List[NegotiationState] = []
        logger.info("NegotiationEngine initialisiert")

    def analyze_negotiation(self, party1_batna: BATNA, party2_batna: BATNA,
                            party1_aspiration: float, party2_aspiration: float) -> NegotiationState:
        """
        Analysiert eine Verhandlungssituation.
        """
        # ZOPA berechnen (Zone of Possible Agreement)
        # Party1 will möglichst viel, Party2 möglichst wenig zahlen
        zopa = None
        if party1_batna.value < party2_batna.value:
            zopa = (party1_batna.value, party2_batna.value)

        state = NegotiationState(
            parties=[party1_batna.party, party2_batna.party],
            current_offers={
                party1_batna.party: party1_aspiration,
                party2_batna.party: party2_aspiration,
            },
            batnas={
                party1_batna.party: party1_batna,
                party2_batna.party: party2_batna,
            },
            zopa=zopa,
            agreement_reached=False
        )

        self.negotiation_history.append(state)
        return state

    def suggest_fair_split(self, state: NegotiationState) -> Optional[float]:
        """Schlägt eine faire Aufteilung vor"""
        if state.zopa is None:
            return None

        # Nash-Verhandlungslösung: Mitte der ZOPA
        return (state.zopa[0] + state.zopa[1]) / 2

    def get_negotiation_advice(self, party: str, state: NegotiationState) -> Dict[str, Any]:
        """Gibt Verhandlungsratschläge"""
        batna = state.batnas.get(party)
        if batna is None:
            return {"fehler": "Partei nicht gefunden"}

        advice = {
            "partei": party,
            "ihr_batna": batna.value,
            "zopa_existiert": state.zopa is not None,
        }

        if state.zopa:
            if party == state.parties[0]:
                advice["empfehlung"] = (
                    f"Fordern Sie nahe {state.zopa[1]:.2f}, "
                    f"akzeptieren Sie nicht unter {state.zopa[0]:.2f}"
                )
            else:
                advice["empfehlung"] = (
                    f"Bieten Sie nahe {state.zopa[0]:.2f}, "
                    f"gehen Sie nicht über {state.zopa[1]:.2f}"
                )
            advice["wolf_tipp"] = (
                "Als erfahrene Händlerin rate ich: Zeige nicht sofort alle Karten, "
                "aber sei bereit, einen fairen Deal zu machen. *zwinkert*"
            )
        else:
            advice["empfehlung"] = "Keine Einigung möglich - BATNA nutzen"
            advice["wolf_tipp"] = (
                "Manchmal ist der beste Deal kein Deal. "
                "Kenne deinen Wert und geh' weiter."
            )

        return advice


# =============================================================================
# MECHANISMUS-DESIGN ENGINE
# =============================================================================

class MechanismDesignEngine:
    """
    Engine für Mechanismus-Design.
    Entwirft Regeln für strategische Situationen.
    """

    def __init__(self):
        logger.info("MechanismDesignEngine initialisiert")

    def analyze_auction(self, auction_type: AuctionType,
                        bidder_values: Dict[str, float]) -> Dict[str, Any]:
        """Analysiert eine Auktion"""

        result = {
            "auktionstyp": auction_type.value,
            "bieter": list(bidder_values.keys()),
            "analyse": {},
        }

        sorted_bidders = sorted(bidder_values.items(), key=lambda x: -x[1])
        winner = sorted_bidders[0][0]
        winner_value = sorted_bidders[0][1]
        second_value = sorted_bidders[1][1] if len(sorted_bidders) > 1 else 0

        if auction_type == AuctionType.SECOND_PRICE_SEALED:
            result["analyse"] = {
                "gewinner": winner,
                "preis": second_value,
                "gewinn_des_gewinners": winner_value - second_value,
                "dominante_strategie": "Wahren Wert bieten (anreizkompatibel)",
                "erklaerung": (
                    "In der Vickrey-Auktion ist es optimal, den wahren Wert zu bieten. "
                    "Man zahlt nur den zweithöchsten Preis!"
                )
            }
        elif auction_type == AuctionType.FIRST_PRICE_SEALED:
            result["analyse"] = {
                "gewinner": winner,
                "preis": "Abhängig von Gebot (strategisch)",
                "dominante_strategie": "Keine - hängt von Erwartungen über andere ab",
                "erklaerung": (
                    "In der Erstpreis-Auktion muss man unter seinem wahren Wert bieten, "
                    "um Gewinn zu machen. Aber wie viel?"
                )
            }
        elif auction_type == AuctionType.ENGLISH:
            result["analyse"] = {
                "gewinner": winner,
                "preis": second_value + 0.01,  # Knapp über Zweithöchstem
                "dominante_strategie": "Bis zum wahren Wert mitbieten",
            }

        result["wolf_kommentar"] = (
            "Ich habe in meinen Handelsjahren viele Auktionen erlebt. "
            "Die Vickrey-Auktion ist elegant - sie belohnt Ehrlichkeit!"
        )

        return result

    def check_incentive_compatibility(self, mechanism: str) -> Dict[str, Any]:
        """Prüft Anreizkompatibilität bekannter Mechanismen"""

        mechanisms = {
            "vickrey_auktion": {
                "anreizkompatibel": True,
                "dominante_strategie": "Wahren Wert bieten",
                "erklaerung": "Wahres Bieten ist dominant, unabhängig von anderen"
            },
            "erstpreis_auktion": {
                "anreizkompatibel": False,
                "dominante_strategie": None,
                "erklaerung": "Optimales Gebot hängt von Überzeugungen über andere ab"
            },
            "vcg_mechanismus": {
                "anreizkompatibel": True,
                "dominante_strategie": "Wahre Präferenzen offenbaren",
                "erklaerung": "Vickrey-Clarke-Groves: Allgemeine anreizkompatible Mechanismen"
            },
            "mehrheitswahl": {
                "anreizkompatibel": False,
                "dominante_strategie": None,
                "erklaerung": "Strategisches Wählen kann sich lohnen (Gibbard-Satterthwaite)"
            }
        }

        return mechanisms.get(mechanism.lower(), {
            "fehler": "Mechanismus nicht bekannt",
            "bekannte_mechanismen": list(mechanisms.keys())
        })


# =============================================================================
# KOMBINIERTE ENGINE
# =============================================================================

class FullGameTheoryEngine:
    """Kombiniert alle spieltheoretischen Engines"""

    def __init__(self):
        self.classic = GameTheoryEngine()
        self.cooperative = CooperativeGameEngine()
        self.evolutionary = EvolutionaryGameEngine()
        self.negotiation = NegotiationEngine()
        self.mechanism = MechanismDesignEngine()

        logger.info("FullGameTheoryEngine initialisiert")

    def get_wolf_wisdom(self) -> str:
        """Holos Weisheit zur Spieltheorie"""
        wisdoms = [
            "Im Rudel überlebt man besser als allein - aber vertraue weise.",
            "Kooperation lohnt sich langfristig, auch wenn Defektion kurzfristig lockt.",
            "Ein guter Händler kennt beide Seiten des Deals.",
            "Manchmal ist der beste Zug, keinen Zug zu machen.",
            "Vertrauen baut sich langsam auf, zerbricht aber schnell.",
            "Die Hirschjagd lehrt: Große Beute erfordert großes Vertrauen.",
        ]
        return random.choice(wisdoms)


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

_game_theory_engine: Optional[GameTheoryEngine] = None
_negotiation_engine: Optional[NegotiationEngine] = None
_full_engine: Optional[FullGameTheoryEngine] = None


def create_game_theory_engine() -> GameTheoryEngine:
    """Factory: Erstellt GameTheoryEngine"""
    global _game_theory_engine
    if _game_theory_engine is None:
        _game_theory_engine = GameTheoryEngine()
    return _game_theory_engine


def create_negotiation_engine() -> NegotiationEngine:
    """Factory: Erstellt NegotiationEngine"""
    global _negotiation_engine
    if _negotiation_engine is None:
        _negotiation_engine = NegotiationEngine()
    return _negotiation_engine


def get_full_game_theory_engine() -> FullGameTheoryEngine:
    """Factory: Erstellt FullGameTheoryEngine"""
    global _full_engine
    if _full_engine is None:
        _full_engine = FullGameTheoryEngine()
    return _full_engine


# =============================================================================
# MAIN (TEST)
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 70)
    print("HOLO GAME THEORY v1.0 - Demo")
    print("=" * 70)

    engine = get_full_game_theory_engine()

    # Gefangenendilemma analysieren
    print("\n--- GEFANGENENDILEMMA ---")
    pd = engine.classic.get_standard_game("gefangenendilemma")
    analysis = engine.classic.analyze_game(pd)
    print(analysis["auszahlungsmatrix"])
    print(f"Nash-Gleichgewichte: {analysis['nash_gleichgewichte']}")
    print(f"Dominante Strategien: {analysis['dominante_strategien']}")
    print(f"Holo sagt: {analysis['wolf_kommentar']}")

    # Hirschjagd
    print("\n--- HIRSCHJAGD ---")
    sh = engine.classic.get_standard_game("hirschjagd")
    analysis = engine.classic.analyze_game(sh)
    print(analysis["auszahlungsmatrix"])
    print(f"Nash-Gleichgewichte: {analysis['nash_gleichgewichte']}")

    # Wiederholtes Spiel
    print("\n--- WIEDERHOLTES GEFANGENENDILEMMA ---")
    result = engine.classic.simulate_repeated_game(
        pd,
        {"Spieler1": StrategyType.TIT_FOR_TAT, "Spieler2": StrategyType.TIT_FOR_TAT},
        rounds=100
    )
    print(f"Tit-for-Tat vs Tit-for-Tat: {result['durchschnitt']}")

    result = engine.classic.simulate_repeated_game(
        pd,
        {"Spieler1": StrategyType.ALWAYS_DEFECT, "Spieler2": StrategyType.TIT_FOR_TAT},
        rounds=100
    )
    print(f"Always Defect vs Tit-for-Tat: {result['durchschnitt']}")

    # Shapley-Wert
    print("\n--- SHAPLEY-WERT ---")
    def coalition_value(coalition: Set[str]) -> float:
        if not coalition:
            return 0
        if len(coalition) == 1:
            return 10
        if len(coalition) == 2:
            return 30
        return 50

    shapley = engine.cooperative.calculate_shapley_value(
        ["A", "B", "C"], coalition_value
    )
    for player, sv in shapley.items():
        print(f"Spieler {player}: Shapley-Wert = {sv.value:.2f}")

    # Verhandlung
    print("\n--- VERHANDLUNG ---")
    state = engine.negotiation.analyze_negotiation(
        BATNA("Käufer", "Anderes Produkt kaufen", 80),
        BATNA("Verkäufer", "An anderen verkaufen", 120),
        party1_aspiration=70,
        party2_aspiration=150
    )
    print(f"ZOPA: {state.zopa}")
    fair = engine.negotiation.suggest_fair_split(state)
    print(f"Faire Aufteilung: {fair}")
    advice = engine.negotiation.get_negotiation_advice("Käufer", state)
    print(f"Empfehlung: {advice['empfehlung']}")

    # Auktion
    print("\n--- VICKREY-AUKTION ---")
    auction = engine.mechanism.analyze_auction(
        AuctionType.SECOND_PRICE_SEALED,
        {"Alice": 100, "Bob": 80, "Carol": 90}
    )
    print(f"Gewinner: {auction['analyse']['gewinner']}")
    print(f"Preis: {auction['analyse']['preis']}")
    print(f"Strategie: {auction['analyse']['dominante_strategie']}")

    # Weisheit
    print("\n--- WOLFSWEISHEIT ---")
    print(f"*legt Ohren an* {engine.get_wolf_wisdom()}")

    print("\n" + "=" * 70)
    print("Demo abgeschlossen!")
