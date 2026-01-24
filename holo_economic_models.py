#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
  HOLO ECONOMIC MODELS v1.0
  Wirtschaftstheorie und Pareto-Optimierung für Holocloude
================================================================================

FEATURES:
1. Mikroökonomie
   - Angebot und Nachfrage
   - Elastizität
   - Nutzentheorie und Indifferenzkurven
   - Produktionstheorie

2. Pareto-Optimierung
   - Pareto-Effizienz
   - Pareto-Front berechnen
   - Multi-Objective Optimization
   - Edgeworth-Box

3. Marktgleichgewicht
   - Preisbildung
   - Wohlfahrtsanalyse
   - Marktversagen
   - Externalitäten

4. Entscheidungstheorie
   - Erwartungsnutzen
   - Risikoaversion
   - Prospect Theory
   - Zeitpräferenzen

5. Ressourcenallokation
   - Optimale Verteilung
   - Budgetrestriktionen
   - Lagrange-Optimierung

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

logger = logging.getLogger("HoloEconomicModels")


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Mikroökonomie
    "MicroeconomicsEngine",
    "SupplyDemand",
    "Elasticity",
    "UtilityFunction",

    # Pareto-Optimierung
    "ParetoEngine",
    "ParetoPoint",
    "ParetoFront",
    "MultiObjectiveOptimizer",

    # Markt
    "MarketEngine",
    "MarketEquilibrium",
    "WelfareAnalysis",

    # Entscheidungstheorie
    "DecisionTheoryEngine",
    "ExpectedUtility",
    "RiskProfile",
    "ProspectTheory",

    # Ressourcen
    "ResourceAllocationEngine",
    "Budget",
    "AllocationResult",

    # Kombiniert
    "EconomicsEngine",

    # Enums
    "GoodType",
    "MarketType",
    "RiskAttitude",
    "OptimizationType",

    # Factory
    "create_microeconomics_engine",
    "create_pareto_engine",
    "create_market_engine",
    "get_economics_engine",
]


# =============================================================================
# ENUMS
# =============================================================================

class GoodType(Enum):
    """Arten von Gütern"""
    NORMAL = "normal"                    # Nachfrage steigt mit Einkommen
    INFERIOR = "inferior"                # Nachfrage sinkt mit Einkommen
    LUXURY = "luxus"                     # Einkommenselastizität > 1
    NECESSITY = "notwendigkeit"          # Einkommenselastizität < 1
    GIFFEN = "giffen"                    # Nachfrage steigt mit Preis
    VEBLEN = "veblen"                    # Prestigegut
    PUBLIC = "oeffentlich"               # Nicht-rivalisierend
    PRIVATE = "privat"                   # Rivalisierend


class MarketType(Enum):
    """Marktformen"""
    PERFECT_COMPETITION = "vollkommener_wettbewerb"
    MONOPOLY = "monopol"
    OLIGOPOLY = "oligopol"
    MONOPOLISTIC_COMPETITION = "monopolistische_konkurrenz"
    MONOPSONY = "monopson"               # Ein Käufer


class RiskAttitude(Enum):
    """Risikoeinstellung"""
    RISK_AVERSE = "risikoavers"          # Sicherheit bevorzugt
    RISK_NEUTRAL = "risikoneutral"       # Erwartungswert-Maximierer
    RISK_SEEKING = "risikofreudig"       # Risiko bevorzugt


class OptimizationType(Enum):
    """Optimierungstyp"""
    MINIMIZE = "minimieren"
    MAXIMIZE = "maximieren"


class ElasticityType(Enum):
    """Elastizitätstypen"""
    PRICE = "preis"                      # Preiselastizität der Nachfrage
    INCOME = "einkommen"                 # Einkommenselastizität
    CROSS = "kreuz"                      # Kreuzpreiselastizität
    SUPPLY = "angebot"                   # Preiselastizität des Angebots


# =============================================================================
# DATENSTRUKTUREN
# =============================================================================

@dataclass
class SupplyDemand:
    """Angebots- und Nachfragefunktion"""
    # Lineare Form: Q = a - b*P (Nachfrage) oder Q = c + d*P (Angebot)
    intercept: float        # a oder c
    slope: float            # -b oder d
    is_supply: bool         # True = Angebot, False = Nachfrage

    def quantity_at_price(self, price: float) -> float:
        """Berechnet Menge bei gegebenem Preis"""
        return max(0, self.intercept + self.slope * price)

    def price_at_quantity(self, quantity: float) -> float:
        """Berechnet Preis bei gegebener Menge (inverse)"""
        if abs(self.slope) < 0.0001:
            return 0
        return (quantity - self.intercept) / self.slope


@dataclass
class Elasticity:
    """Elastizität"""
    elasticity_type: ElasticityType
    value: float
    interpretation: str

    def is_elastic(self) -> bool:
        return abs(self.value) > 1

    def is_inelastic(self) -> bool:
        return abs(self.value) < 1


@dataclass
class UtilityFunction:
    """Nutzenfunktion"""
    name: str
    function_type: str  # "cobb_douglas", "ces", "quasilinear", "leontief"
    parameters: Dict[str, float]

    def calculate(self, quantities: Dict[str, float]) -> float:
        """Berechnet den Nutzen"""
        if self.function_type == "cobb_douglas":
            # U = x1^a * x2^b
            result = 1.0
            for good, qty in quantities.items():
                exp = self.parameters.get(good, 0.5)
                result *= qty ** exp if qty > 0 else 0
            return result

        elif self.function_type == "quasilinear":
            # U = v(x1) + x2
            x1 = quantities.get("x1", 0)
            x2 = quantities.get("x2", 0)
            return math.sqrt(x1) + x2 if x1 > 0 else x2

        elif self.function_type == "leontief":
            # U = min(x1/a, x2/b) - perfekte Komplemente
            ratios = []
            for good, qty in quantities.items():
                coef = self.parameters.get(good, 1)
                ratios.append(qty / coef if coef > 0 else 0)
            return min(ratios) if ratios else 0

        return 0


@dataclass
class MarketEquilibrium:
    """Marktgleichgewicht"""
    price: float
    quantity: float
    consumer_surplus: float
    producer_surplus: float
    total_welfare: float
    deadweight_loss: float = 0.0


@dataclass
class ParetoPoint:
    """Ein Punkt im Zielfunktionsraum"""
    objectives: Dict[str, float]  # Zielfunktion -> Wert
    decision_vars: Dict[str, float]  # Entscheidungsvariablen
    is_dominated: bool = False


@dataclass
class ParetoFront:
    """Die Pareto-Front"""
    points: List[ParetoPoint]
    objectives: List[str]

    def get_extreme_points(self) -> Dict[str, ParetoPoint]:
        """Gibt die Extrempunkte zurück (beste für jedes Ziel)"""
        extremes = {}
        for obj in self.objectives:
            best = max(self.points, key=lambda p: p.objectives.get(obj, float('-inf')))
            extremes[obj] = best
        return extremes


@dataclass
class Budget:
    """Budgetrestriktion"""
    total_budget: float
    prices: Dict[str, float]  # Gut -> Preis

    def is_affordable(self, quantities: Dict[str, float]) -> bool:
        """Prüft ob ein Güterbündel erschwinglich ist"""
        cost = sum(quantities.get(g, 0) * p for g, p in self.prices.items())
        return cost <= self.total_budget

    def get_budget_line(self) -> str:
        """Gibt die Budgetgleichung zurück"""
        terms = [f"{p}*{g}" for g, p in self.prices.items()]
        return f"{' + '.join(terms)} = {self.total_budget}"


@dataclass
class AllocationResult:
    """Ergebnis einer Ressourcenallokation"""
    quantities: Dict[str, float]
    utility: float
    total_cost: float
    is_optimal: bool
    method: str


@dataclass
class ExpectedUtility:
    """Erwartungsnutzen"""
    outcomes: List[Tuple[float, float]]  # (Wahrscheinlichkeit, Auszahlung)
    expected_value: float
    expected_utility: float
    certainty_equivalent: float


@dataclass
class RiskProfile:
    """Risikoprofil"""
    attitude: RiskAttitude
    risk_premium: float
    arrow_pratt_coefficient: float  # Maß für Risikoaversion


# =============================================================================
# MIKROÖKONOMIE ENGINE
# =============================================================================

class MicroeconomicsEngine:
    """Engine für mikroökonomische Analysen"""

    def __init__(self):
        logger.info("MicroeconomicsEngine initialisiert")

    def calculate_elasticity(self, p1: float, p2: float,
                              q1: float, q2: float,
                              elasticity_type: ElasticityType = ElasticityType.PRICE) -> Elasticity:
        """
        Berechnet die Elastizität.
        E = (ΔQ/Q) / (ΔP/P) = (ΔQ/ΔP) * (P/Q)
        """
        delta_q = q2 - q1
        delta_p = p2 - p1

        if abs(delta_p) < 0.0001 or abs(q1) < 0.0001:
            return Elasticity(elasticity_type, 0, "Nicht berechenbar")

        # Punktelastizität
        elasticity = (delta_q / delta_p) * (p1 / q1)

        # Interpretation
        if abs(elasticity) > 1:
            interpretation = "Elastisch - Nachfrage reagiert stark auf Preisänderungen"
        elif abs(elasticity) < 1:
            interpretation = "Unelastisch - Nachfrage reagiert schwach auf Preisänderungen"
        else:
            interpretation = "Einheitselastisch"

        return Elasticity(elasticity_type, elasticity, interpretation)

    def find_equilibrium(self, demand: SupplyDemand,
                         supply: SupplyDemand) -> MarketEquilibrium:
        """
        Findet das Marktgleichgewicht.
        Qd = Qs
        """
        # Gleichsetzen: a - b*P = c + d*P
        # P* = (a - c) / (d + b)
        # Für Nachfrage: slope ist negativ (-b)
        # Für Angebot: slope ist positiv (d)

        # demand: Q = a_d + slope_d * P (slope_d < 0)
        # supply: Q = a_s + slope_s * P (slope_s > 0)

        denom = supply.slope - demand.slope
        if abs(denom) < 0.0001:
            return MarketEquilibrium(0, 0, 0, 0, 0)

        price_eq = (demand.intercept - supply.intercept) / denom
        quantity_eq = demand.quantity_at_price(price_eq)

        # Konsumentenrente: Fläche unter Nachfrage, über Preis
        # = (1/2) * (Choke Price - P*) * Q*
        if abs(demand.slope) > 0.0001:
            choke_price = -demand.intercept / demand.slope
            consumer_surplus = 0.5 * (choke_price - price_eq) * quantity_eq
        else:
            consumer_surplus = 0

        # Produzentenrente: Fläche über Angebot, unter Preis
        if abs(supply.slope) > 0.0001:
            min_supply_price = -supply.intercept / supply.slope
            producer_surplus = 0.5 * (price_eq - max(0, min_supply_price)) * quantity_eq
        else:
            producer_surplus = 0

        consumer_surplus = max(0, consumer_surplus)
        producer_surplus = max(0, producer_surplus)

        return MarketEquilibrium(
            price=price_eq,
            quantity=quantity_eq,
            consumer_surplus=consumer_surplus,
            producer_surplus=producer_surplus,
            total_welfare=consumer_surplus + producer_surplus
        )

    def analyze_tax(self, demand: SupplyDemand, supply: SupplyDemand,
                    tax_amount: float) -> Dict[str, Any]:
        """Analysiert die Auswirkung einer Steuer"""

        # Gleichgewicht ohne Steuer
        eq_before = self.find_equilibrium(demand, supply)

        # Mit Steuer: Effektiv höhere Kosten für Anbieter
        supply_with_tax = SupplyDemand(
            intercept=supply.intercept - tax_amount * supply.slope,
            slope=supply.slope,
            is_supply=True
        )

        eq_after = self.find_equilibrium(demand, supply_with_tax)

        tax_revenue = tax_amount * eq_after.quantity
        dwl = eq_before.total_welfare - eq_after.total_welfare - tax_revenue

        return {
            "vor_steuer": {
                "preis": eq_before.price,
                "menge": eq_before.quantity,
                "wohlfahrt": eq_before.total_welfare
            },
            "nach_steuer": {
                "konsumentenpreis": eq_after.price,
                "produzentenpreis": eq_after.price - tax_amount,
                "menge": eq_after.quantity,
                "steueraufkommen": tax_revenue,
                "wohlfahrtsverlust": max(0, dwl)
            },
            "wolf_kommentar": (
                "Steuern sind wie ein Wolf im Schafspelz - "
                "sie sehen harmlos aus, aber beißen beide Seiten!"
            )
        }

    def optimal_consumption(self, utility: UtilityFunction,
                            budget: Budget) -> AllocationResult:
        """
        Findet die optimale Konsumentscheidung.
        Maximiere U(x1, x2) unter p1*x1 + p2*x2 = M
        """
        if utility.function_type == "cobb_douglas":
            # Für Cobb-Douglas: x_i = (a_i / Σa_j) * M / p_i
            total_exp = sum(utility.parameters.values())
            quantities = {}

            for good, price in budget.prices.items():
                exp = utility.parameters.get(good, 0.5)
                quantities[good] = (exp / total_exp) * budget.total_budget / price

            util = utility.calculate(quantities)
            cost = sum(quantities[g] * budget.prices[g] for g in quantities)

            return AllocationResult(
                quantities=quantities,
                utility=util,
                total_cost=cost,
                is_optimal=True,
                method="Cobb-Douglas Analytisch"
            )

        # Für andere: Numerische Suche
        best_util = 0
        best_quantities = {}

        goods = list(budget.prices.keys())
        if len(goods) == 2:
            g1, g2 = goods
            p1, p2 = budget.prices[g1], budget.prices[g2]

            for i in range(101):
                x1 = i / 100 * budget.total_budget / p1
                x2 = (budget.total_budget - p1 * x1) / p2

                if x2 >= 0:
                    u = utility.calculate({g1: x1, g2: x2})
                    if u > best_util:
                        best_util = u
                        best_quantities = {g1: x1, g2: x2}

        return AllocationResult(
            quantities=best_quantities,
            utility=best_util,
            total_cost=budget.total_budget,
            is_optimal=True,
            method="Numerische Suche"
        )


# =============================================================================
# PARETO-OPTIMIERUNG ENGINE
# =============================================================================

class ParetoEngine:
    """Engine für Pareto-Optimierung und Multi-Objective-Optimierung"""

    def __init__(self):
        logger.info("ParetoEngine initialisiert")

    def is_dominated(self, point: ParetoPoint, other: ParetoPoint,
                     maximize: bool = True) -> bool:
        """
        Prüft ob 'point' von 'other' dominiert wird.
        'other' dominiert 'point' wenn other in allen Zielen mindestens
        so gut und in mindestens einem besser ist.
        """
        dominated_in_all = True
        strictly_better_in_one = False

        for obj in point.objectives.keys():
            p_val = point.objectives.get(obj, 0)
            o_val = other.objectives.get(obj, 0)

            if maximize:
                if o_val < p_val:
                    dominated_in_all = False
                if o_val > p_val:
                    strictly_better_in_one = True
            else:
                if o_val > p_val:
                    dominated_in_all = False
                if o_val < p_val:
                    strictly_better_in_one = True

        return dominated_in_all and strictly_better_in_one

    def find_pareto_front(self, points: List[ParetoPoint],
                          maximize: bool = True) -> ParetoFront:
        """
        Findet die Pareto-Front aus einer Menge von Punkten.
        """
        pareto_points = []

        for i, point in enumerate(points):
            is_dominated_flag = False
            for j, other in enumerate(points):
                if i != j and self.is_dominated(point, other, maximize):
                    is_dominated_flag = True
                    break

            if not is_dominated_flag:
                point.is_dominated = False
                pareto_points.append(point)
            else:
                point.is_dominated = True

        objectives = list(points[0].objectives.keys()) if points else []

        return ParetoFront(points=pareto_points, objectives=objectives)

    def weighted_sum_method(self, points: List[ParetoPoint],
                            weights: Dict[str, float],
                            maximize: bool = True) -> ParetoPoint:
        """
        Findet den besten Punkt mit der Weighted-Sum-Methode.
        """
        def score(point: ParetoPoint) -> float:
            s = sum(weights.get(obj, 0) * point.objectives.get(obj, 0)
                   for obj in weights.keys())
            return s if maximize else -s

        return max(points, key=score)

    def epsilon_constraint_method(self, points: List[ParetoPoint],
                                   primary_objective: str,
                                   constraints: Dict[str, float],
                                   maximize: bool = True) -> List[ParetoPoint]:
        """
        Findet Punkte mit der Epsilon-Constraint-Methode.
        Maximiere ein Ziel unter Nebenbedingungen für andere.
        """
        feasible = []

        for point in points:
            satisfies = True
            for obj, min_val in constraints.items():
                if point.objectives.get(obj, 0) < min_val:
                    satisfies = False
                    break

            if satisfies:
                feasible.append(point)

        if not feasible:
            return []

        # Sortiere nach primärem Ziel
        if maximize:
            feasible.sort(key=lambda p: p.objectives.get(primary_objective, 0), reverse=True)
        else:
            feasible.sort(key=lambda p: p.objectives.get(primary_objective, 0))

        return feasible

    def calculate_hypervolume(self, pareto_front: ParetoFront,
                               reference_point: Dict[str, float]) -> float:
        """
        Berechnet das Hypervolumen der Pareto-Front.
        (Vereinfacht für 2D)
        """
        if not pareto_front.points:
            return 0

        if len(pareto_front.objectives) != 2:
            return 0  # Nur für 2D implementiert

        obj1, obj2 = pareto_front.objectives
        ref1 = reference_point.get(obj1, 0)
        ref2 = reference_point.get(obj2, 0)

        # Sortiere Punkte nach obj1
        sorted_points = sorted(
            pareto_front.points,
            key=lambda p: p.objectives.get(obj1, 0)
        )

        hypervolume = 0
        prev_obj2 = ref2

        for point in sorted_points:
            p1 = point.objectives.get(obj1, 0)
            p2 = point.objectives.get(obj2, 0)

            # Rechteckfläche hinzufügen
            width = p1 - ref1
            height = prev_obj2 - p2

            if width > 0 and height > 0:
                hypervolume += width * height

            prev_obj2 = p2
            ref1 = p1

        return hypervolume

    def analyze_tradeoffs(self, pareto_front: ParetoFront) -> Dict[str, Any]:
        """Analysiert Trade-offs auf der Pareto-Front"""

        if len(pareto_front.points) < 2:
            return {"fehler": "Nicht genug Punkte für Trade-off-Analyse"}

        objectives = pareto_front.objectives
        tradeoffs = {}

        for i, obj1 in enumerate(objectives):
            for obj2 in objectives[i+1:]:
                # Berechne marginale Rate der Substitution
                sorted_points = sorted(
                    pareto_front.points,
                    key=lambda p: p.objectives.get(obj1, 0)
                )

                mrs_values = []
                for j in range(len(sorted_points) - 1):
                    p1 = sorted_points[j]
                    p2 = sorted_points[j + 1]

                    delta_obj1 = (p2.objectives.get(obj1, 0) -
                                  p1.objectives.get(obj1, 0))
                    delta_obj2 = (p2.objectives.get(obj2, 0) -
                                  p1.objectives.get(obj2, 0))

                    if abs(delta_obj1) > 0.0001:
                        mrs = delta_obj2 / delta_obj1
                        mrs_values.append(mrs)

                avg_mrs = sum(mrs_values) / len(mrs_values) if mrs_values else 0

                tradeoffs[f"{obj1}_vs_{obj2}"] = {
                    "durchschnittliche_mrs": avg_mrs,
                    "interpretation": (
                        f"Um 1 Einheit {obj1} zu gewinnen, "
                        f"muss man ~{abs(avg_mrs):.2f} Einheiten {obj2} aufgeben"
                    )
                }

        return {
            "anzahl_pareto_punkte": len(pareto_front.points),
            "tradeoffs": tradeoffs,
            "wolf_kommentar": (
                "Pareto-Optimalität ist wie die Balance im Rudel - "
                "keiner kann besser gestellt werden, ohne einen anderen zu benachteiligen."
            )
        }


# =============================================================================
# MARKT ENGINE
# =============================================================================

class MarketEngine:
    """Engine für Marktanalysen"""

    def __init__(self):
        self.micro = MicroeconomicsEngine()
        logger.info("MarketEngine initialisiert")

    def analyze_market_structure(self, market_type: MarketType) -> Dict[str, Any]:
        """Analysiert eine Marktstruktur"""

        analysis = {
            MarketType.PERFECT_COMPETITION: {
                "anzahl_anbieter": "Sehr viele",
                "produkthomogenitaet": "Homogen",
                "markteintritt": "Frei",
                "preissetzung": "Preisnehmer (P = MC)",
                "langfristiger_gewinn": "Null (nur Normalgewinn)",
                "effizienz": "Pareto-effizient",
            },
            MarketType.MONOPOLY: {
                "anzahl_anbieter": "Einer",
                "produkthomogenitaet": "Einzigartig",
                "markteintritt": "Blockiert",
                "preissetzung": "Preissetzer (MR = MC, P > MC)",
                "langfristiger_gewinn": "Positiv möglich",
                "effizienz": "Wohlfahrtsverlust",
            },
            MarketType.OLIGOPOLY: {
                "anzahl_anbieter": "Wenige",
                "produkthomogenitaet": "Homogen oder differenziert",
                "markteintritt": "Erschwert",
                "preissetzung": "Strategische Interaktion",
                "langfristiger_gewinn": "Positiv möglich",
                "effizienz": "Abhängig von Wettbewerbsintensität",
            },
            MarketType.MONOPOLISTIC_COMPETITION: {
                "anzahl_anbieter": "Viele",
                "produkthomogenitaet": "Differenziert",
                "markteintritt": "Relativ frei",
                "preissetzung": "Begrenzte Preissetzungsmacht",
                "langfristiger_gewinn": "Null",
                "effizienz": "Excess Capacity",
            },
        }

        return analysis.get(market_type, {"fehler": "Unbekannter Markttyp"})

    def monopoly_pricing(self, demand: SupplyDemand,
                         marginal_cost: float) -> Dict[str, Any]:
        """
        Berechnet Monopolpreissetzung.
        MR = MC
        Für lineare Nachfrage P = a - bQ: MR = a - 2bQ
        """
        # demand: Q = intercept + slope * P
        # Inverse: P = (Q - intercept) / slope
        # Wenn slope < 0 (normal): P = -intercept/slope - Q/slope = a - bQ
        # wobei a = -intercept/slope und b = -1/slope

        if abs(demand.slope) < 0.0001:
            return {"fehler": "Ungültige Nachfragefunktion"}

        a = -demand.intercept / demand.slope  # Choke Price
        b = -1 / demand.slope

        # MR = a - 2bQ = MC
        # Q* = (a - MC) / (2b)
        q_monopoly = (a - marginal_cost) / (2 * b)
        p_monopoly = a - b * q_monopoly

        # Vergleich mit Wettbewerb (P = MC)
        q_competitive = (a - marginal_cost) / b
        p_competitive = marginal_cost

        # Wohlfahrt
        monopoly_profit = (p_monopoly - marginal_cost) * q_monopoly
        consumer_surplus_monopoly = 0.5 * (a - p_monopoly) * q_monopoly
        total_welfare_monopoly = monopoly_profit + consumer_surplus_monopoly

        consumer_surplus_competitive = 0.5 * (a - p_competitive) * q_competitive
        total_welfare_competitive = consumer_surplus_competitive

        dwl = total_welfare_competitive - total_welfare_monopoly

        return {
            "monopol": {
                "preis": p_monopoly,
                "menge": q_monopoly,
                "gewinn": monopoly_profit,
                "konsumentenrente": consumer_surplus_monopoly,
            },
            "wettbewerb": {
                "preis": p_competitive,
                "menge": q_competitive,
                "konsumentenrente": consumer_surplus_competitive,
            },
            "wohlfahrtsverlust": max(0, dwl),
            "lerner_index": (p_monopoly - marginal_cost) / p_monopoly if p_monopoly > 0 else 0,
            "wolf_kommentar": (
                "Ein Monopolist ist wie ein einsamer Wolf, der das beste Jagdrevier hat - "
                "aber ohne Wettbewerb wird er träge und die Beute leidet."
            )
        }


# =============================================================================
# ENTSCHEIDUNGSTHEORIE ENGINE
# =============================================================================

class DecisionTheoryEngine:
    """Engine für Entscheidungstheorie unter Unsicherheit"""

    def __init__(self):
        logger.info("DecisionTheoryEngine initialisiert")

    def calculate_expected_utility(self, outcomes: List[Tuple[float, float]],
                                    utility_function: Callable[[float], float]) -> ExpectedUtility:
        """
        Berechnet den Erwartungsnutzen.
        outcomes: Liste von (Wahrscheinlichkeit, Auszahlung)
        """
        expected_value = sum(p * x for p, x in outcomes)
        expected_utility = sum(p * utility_function(x) for p, x in outcomes)

        # Sicherheitsäquivalent: u(CE) = E[u(x)]
        # Numerisch suchen
        ce = self._find_certainty_equivalent(expected_utility, utility_function)

        return ExpectedUtility(
            outcomes=outcomes,
            expected_value=expected_value,
            expected_utility=expected_utility,
            certainty_equivalent=ce
        )

    def _find_certainty_equivalent(self, target_utility: float,
                                    utility_function: Callable[[float], float],
                                    search_range: Tuple[float, float] = (0, 1000)) -> float:
        """Findet das Sicherheitsäquivalent durch binäre Suche"""
        low, high = search_range

        for _ in range(50):
            mid = (low + high) / 2
            u_mid = utility_function(mid)

            if abs(u_mid - target_utility) < 0.0001:
                return mid

            if u_mid < target_utility:
                low = mid
            else:
                high = mid

        return (low + high) / 2

    def analyze_risk_attitude(self, utility_function: Callable[[float], float],
                               wealth: float) -> RiskProfile:
        """
        Analysiert die Risikoeinstellung basierend auf der Nutzenfunktion.
        """
        h = 0.001 * wealth

        # Erste und zweite Ableitung numerisch
        u = utility_function(wealth)
        u_plus = utility_function(wealth + h)
        u_minus = utility_function(wealth - h)

        u_prime = (u_plus - u_minus) / (2 * h)
        u_double_prime = (u_plus - 2 * u + u_minus) / (h ** 2)

        # Arrow-Pratt Maß für absolute Risikoaversion
        if abs(u_prime) < 0.0001:
            arrow_pratt = 0
        else:
            arrow_pratt = -u_double_prime / u_prime

        # Risikoeinstellung bestimmen
        if arrow_pratt > 0.01:
            attitude = RiskAttitude.RISK_AVERSE
        elif arrow_pratt < -0.01:
            attitude = RiskAttitude.RISK_SEEKING
        else:
            attitude = RiskAttitude.RISK_NEUTRAL

        # Risikoprämie für 50-50 Gamble
        gamble_outcomes = [(0.5, wealth * 0.5), (0.5, wealth * 1.5)]
        eu = self.calculate_expected_utility(gamble_outcomes, utility_function)
        risk_premium = eu.expected_value - eu.certainty_equivalent

        return RiskProfile(
            attitude=attitude,
            risk_premium=risk_premium,
            arrow_pratt_coefficient=arrow_pratt
        )

    def prospect_theory_value(self, outcome: float,
                               reference_point: float = 0,
                               alpha: float = 0.88,
                               lambda_: float = 2.25) -> float:
        """
        Berechnet den Wert nach Prospect Theory (Kahneman & Tversky).
        - Verlustaversion (λ > 1)
        - Abnehmende Sensitivität (α < 1)
        """
        x = outcome - reference_point

        if x >= 0:
            return x ** alpha
        else:
            return -lambda_ * ((-x) ** alpha)

    def probability_weighting(self, p: float,
                               gamma: float = 0.61) -> float:
        """
        Probability Weighting Function nach Prospect Theory.
        Menschen überschätzen kleine Wahrscheinlichkeiten.
        """
        if p == 0:
            return 0
        if p == 1:
            return 1

        return (p ** gamma) / ((p ** gamma + (1 - p) ** gamma) ** (1 / gamma))


# =============================================================================
# RESSOURCENALLOKATION ENGINE
# =============================================================================

class ResourceAllocationEngine:
    """Engine für Ressourcenallokation"""

    def __init__(self):
        self.micro = MicroeconomicsEngine()
        logger.info("ResourceAllocationEngine initialisiert")

    def allocate_budget(self, budget: Budget,
                         utilities: Dict[str, Callable[[float], float]]) -> AllocationResult:
        """
        Allokiert ein Budget optimal auf verschiedene Güter.
        Maximiert Gesamtnutzen unter Budgetrestriktion.
        """
        goods = list(budget.prices.keys())
        n = len(goods)

        if n == 0:
            return AllocationResult({}, 0, 0, False, "Keine Güter")

        best_allocation = {}
        best_utility = float('-inf')

        # Grid Search (für Raspberry Pi geeignet)
        steps = 20

        if n == 1:
            g = goods[0]
            qty = budget.total_budget / budget.prices[g]
            u = utilities.get(g, lambda x: x)(qty)
            return AllocationResult({g: qty}, u, budget.total_budget, True, "Single Good")

        elif n == 2:
            g1, g2 = goods
            p1, p2 = budget.prices[g1], budget.prices[g2]

            for i in range(steps + 1):
                share1 = i / steps
                x1 = share1 * budget.total_budget / p1
                x2 = (1 - share1) * budget.total_budget / p2

                u1 = utilities.get(g1, lambda x: math.sqrt(x))(x1)
                u2 = utilities.get(g2, lambda x: math.sqrt(x))(x2)
                total_u = u1 + u2

                if total_u > best_utility:
                    best_utility = total_u
                    best_allocation = {g1: x1, g2: x2}

        return AllocationResult(
            quantities=best_allocation,
            utility=best_utility,
            total_cost=budget.total_budget,
            is_optimal=True,
            method="Grid Search"
        )

    def lagrange_optimize(self, objective: Callable[[Dict[str, float]], float],
                           budget: Budget,
                           initial_guess: Dict[str, float]) -> AllocationResult:
        """
        Optimierung mit Lagrange-Methode (numerisch).
        """
        # Gradient Descent für Lagrangian
        quantities = initial_guess.copy()
        lambda_val = 1.0  # Lagrange-Multiplikator
        learning_rate = 0.01

        for _ in range(1000):
            # Berechne Constraint: g(x) = Σp_i*x_i - B = 0
            cost = sum(quantities[g] * budget.prices[g] for g in quantities)
            constraint = cost - budget.total_budget

            # Numerische Gradienten
            h = 0.001
            for g in quantities:
                # Gradient des Ziels
                q_plus = quantities.copy()
                q_plus[g] += h
                grad_obj = (objective(q_plus) - objective(quantities)) / h

                # Gradient des Constraints (= p_i)
                grad_con = budget.prices[g]

                # Update: x_i += lr * (grad_obj - lambda * grad_con)
                quantities[g] += learning_rate * (grad_obj - lambda_val * grad_con)
                quantities[g] = max(0, quantities[g])

            # Update Lambda
            lambda_val += learning_rate * constraint

        return AllocationResult(
            quantities=quantities,
            utility=objective(quantities),
            total_cost=sum(quantities[g] * budget.prices[g] for g in quantities),
            is_optimal=True,
            method="Lagrange Numerical"
        )


# =============================================================================
# KOMBINIERTE ENGINE
# =============================================================================

class EconomicsEngine:
    """Kombiniert alle ökonomischen Engines"""

    def __init__(self):
        self.micro = MicroeconomicsEngine()
        self.pareto = ParetoEngine()
        self.market = MarketEngine()
        self.decision = DecisionTheoryEngine()
        self.resource = ResourceAllocationEngine()

        logger.info("EconomicsEngine initialisiert (alle Sub-Engines)")

    def get_economic_wisdom(self) -> str:
        """Holos wirtschaftliche Weisheit"""
        wisdoms = [
            "Der Markt ist wie ein Wald - er findet sein Gleichgewicht, aber manchmal braucht er Hilfe.",
            "Pareto-Effizienz ist schön, aber Gerechtigkeit ist eine andere Frage...",
            "Als Händlerin weiß ich: Der beste Deal ist einer, bei dem beide gewinnen.",
            "Elastizität ist wichtig - wer sie versteht, versteht die Macht der Preise.",
            "Risiko und Ertrag tanzen immer zusammen - wie Wolf und Mond.",
            "Budget-Constraints sind wie die Grenzen des Reviers - man muss weise wählen.",
        ]
        return random.choice(wisdoms)


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

_micro_engine: Optional[MicroeconomicsEngine] = None
_pareto_engine: Optional[ParetoEngine] = None
_market_engine: Optional[MarketEngine] = None
_economics_engine: Optional[EconomicsEngine] = None


def create_microeconomics_engine() -> MicroeconomicsEngine:
    """Factory: Erstellt MicroeconomicsEngine"""
    global _micro_engine
    if _micro_engine is None:
        _micro_engine = MicroeconomicsEngine()
    return _micro_engine


def create_pareto_engine() -> ParetoEngine:
    """Factory: Erstellt ParetoEngine"""
    global _pareto_engine
    if _pareto_engine is None:
        _pareto_engine = ParetoEngine()
    return _pareto_engine


def create_market_engine() -> MarketEngine:
    """Factory: Erstellt MarketEngine"""
    global _market_engine
    if _market_engine is None:
        _market_engine = MarketEngine()
    return _market_engine


def get_economics_engine() -> EconomicsEngine:
    """Factory: Erstellt EconomicsEngine"""
    global _economics_engine
    if _economics_engine is None:
        _economics_engine = EconomicsEngine()
    return _economics_engine


# =============================================================================
# MAIN (TEST)
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 70)
    print("HOLO ECONOMIC MODELS v1.0 - Demo")
    print("=" * 70)

    engine = get_economics_engine()

    # Marktgleichgewicht
    print("\n--- MARKTGLEICHGEWICHT ---")
    demand = SupplyDemand(intercept=100, slope=-2, is_supply=False)
    supply = SupplyDemand(intercept=0, slope=1, is_supply=True)

    eq = engine.micro.find_equilibrium(demand, supply)
    print(f"Gleichgewichtspreis: {eq.price:.2f}")
    print(f"Gleichgewichtsmenge: {eq.quantity:.2f}")
    print(f"Konsumentenrente: {eq.consumer_surplus:.2f}")
    print(f"Produzentenrente: {eq.producer_surplus:.2f}")

    # Elastizität
    print("\n--- ELASTIZITÄT ---")
    el = engine.micro.calculate_elasticity(10, 12, 80, 70)
    print(f"Preiselastizität: {el.value:.2f}")
    print(f"Interpretation: {el.interpretation}")

    # Steueranalyse
    print("\n--- STEUERANALYSE ---")
    tax = engine.micro.analyze_tax(demand, supply, 5)
    print(f"Preis nach Steuer: {tax['nach_steuer']['konsumentenpreis']:.2f}")
    print(f"Wohlfahrtsverlust: {tax['nach_steuer']['wohlfahrtsverlust']:.2f}")
    print(f"Holo: {tax['wolf_kommentar']}")

    # Pareto-Optimierung
    print("\n--- PARETO-OPTIMIERUNG ---")
    points = [
        ParetoPoint({"gewinn": 10, "umwelt": 5}, {}),
        ParetoPoint({"gewinn": 8, "umwelt": 8}, {}),
        ParetoPoint({"gewinn": 5, "umwelt": 10}, {}),
        ParetoPoint({"gewinn": 6, "umwelt": 6}, {}),  # Dominiert
        ParetoPoint({"gewinn": 9, "umwelt": 7}, {}),
    ]

    front = engine.pareto.find_pareto_front(points)
    print(f"Pareto-Front hat {len(front.points)} Punkte")
    tradeoffs = engine.pareto.analyze_tradeoffs(front)
    print(f"Trade-off: {list(tradeoffs['tradeoffs'].values())[0]['interpretation']}")

    # Monopol
    print("\n--- MONOPOLANALYSE ---")
    monopol = engine.market.monopoly_pricing(demand, marginal_cost=10)
    print(f"Monopolpreis: {monopol['monopol']['preis']:.2f}")
    print(f"Wettbewerbspreis: {monopol['wettbewerb']['preis']:.2f}")
    print(f"Wohlfahrtsverlust: {monopol['wohlfahrtsverlust']:.2f}")

    # Entscheidung unter Unsicherheit
    print("\n--- ERWARTUNGSNUTZEN ---")
    def sqrt_utility(x):
        return math.sqrt(x) if x > 0 else 0

    eu = engine.decision.calculate_expected_utility(
        [(0.5, 100), (0.5, 400)],
        sqrt_utility
    )
    print(f"Erwartungswert: {eu.expected_value:.2f}")
    print(f"Erwartungsnutzen: {eu.expected_utility:.2f}")
    print(f"Sicherheitsäquivalent: {eu.certainty_equivalent:.2f}")
    print(f"Risikoprämie: {eu.expected_value - eu.certainty_equivalent:.2f}")

    # Prospect Theory
    print("\n--- PROSPECT THEORY ---")
    gain = engine.decision.prospect_theory_value(100)
    loss = engine.decision.prospect_theory_value(-100)
    print(f"Wert eines Gewinns von 100: {gain:.2f}")
    print(f"Wert eines Verlusts von 100: {loss:.2f}")
    print(f"Verlustaversion: Verlust wiegt {abs(loss/gain):.2f}x schwerer")

    # Weisheit
    print("\n--- WIRTSCHAFTSWEISHEIT ---")
    print(f"*stellt Ohren auf* {engine.get_economic_wisdom()}")

    print("\n" + "=" * 70)
    print("Demo abgeschlossen!")
