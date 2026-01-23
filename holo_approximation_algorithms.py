#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO APPROXIMATION ALGORITHMS - Heuristische Optimierung                   ║
║                                                                              ║
║  Implementiert Approximationsalgorithmen für komplexe Optimierungsprobleme: ║
║                                                                              ║
║  1. SIMULATED ANNEALING  → Metallurgisch inspirierte Optimierung            ║
║  2. PSO                  → Particle Swarm Optimization (Schwarmverhalten)   ║
║  3. BRANCH & BOUND       → Systematische Enumeration mit Pruning            ║
║                                                                              ║
║  Diese Algorithmen finden gute Lösungen für NP-schwere Probleme.           ║
╚══════════════════════════════════════════════════════════════════════════════╝

Autor: Holocloude System
Version: 1.0
"""

import math
import random
import logging
import copy
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable, Set, TypeVar, Generic
from enum import Enum, auto
from datetime import datetime
from abc import ABC, abstractmethod
import heapq
from collections import defaultdict

logger = logging.getLogger("HoloApproximation")

# Type variable für generische Lösungen
T = TypeVar('T')


# =============================================================================
# ENUMS
# =============================================================================

class OptimizationType(Enum):
    """Optimierungsrichtung"""
    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"


class AlgorithmStatus(Enum):
    """Status eines Algorithmus"""
    INITIALIZED = "initialized"
    RUNNING = "running"
    CONVERGED = "converged"
    MAX_ITERATIONS = "max_iterations"
    TIMEOUT = "timeout"
    FAILED = "failed"


class CoolingSchedule(Enum):
    """Abkühlungsschema für Simulated Annealing"""
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    LOGARITHMIC = "logarithmic"
    ADAPTIVE = "adaptive"


class PSO_Topology(Enum):
    """Topologie für PSO"""
    GLOBAL_BEST = "global_best"    # Alle Partikel kennen das globale Beste
    LOCAL_BEST = "local_best"      # Nur Nachbarn kennen sich
    RING = "ring"                   # Ring-Topologie


class BranchStrategy(Enum):
    """Branching-Strategie für Branch & Bound"""
    DEPTH_FIRST = "depth_first"
    BREADTH_FIRST = "breadth_first"
    BEST_FIRST = "best_first"


# =============================================================================
# DATENSTRUKTUREN
# =============================================================================

@dataclass
class Solution:
    """Eine Lösung mit ihrem Wert"""
    state: Any                      # Der Lösungszustand
    value: float                    # Der Zielfunktionswert
    is_feasible: bool = True        # Ist die Lösung zulässig?
    iteration: int = 0              # In welcher Iteration gefunden?
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationResult:
    """Ergebnis einer Optimierung"""
    best_solution: Solution
    history: List[Tuple[int, float]]  # (Iteration, Wert)
    algorithm: str
    status: AlgorithmStatus
    iterations: int
    elapsed_time_ms: float
    parameters: Dict[str, Any]


@dataclass
class Particle:
    """Ein Partikel für PSO"""
    position: List[float]           # Aktuelle Position
    velocity: List[float]           # Aktuelle Geschwindigkeit
    best_position: List[float]      # Persönlich beste Position
    best_value: float               # Persönlich bester Wert
    current_value: float = float('inf')


@dataclass
class BBNode:
    """Ein Knoten für Branch & Bound"""
    state: Any                      # Partieller Lösungszustand
    bound: float                    # Schranke (lower/upper bound)
    depth: int                      # Tiefe im Baum
    parent: Optional['BBNode'] = None
    is_feasible: bool = True
    is_pruned: bool = False

    def __lt__(self, other):
        """Für Heap-Vergleiche"""
        return self.bound < other.bound


# =============================================================================
# ABSTRAKTE BASIS-KLASSE
# =============================================================================

class OptimizationAlgorithm(ABC):
    """Abstrakte Basisklasse für Optimierungsalgorithmen"""

    def __init__(self, objective_function: Callable[[Any], float],
                 optimization_type: OptimizationType = OptimizationType.MINIMIZE):
        self.objective = objective_function
        self.optimization_type = optimization_type
        self.best_solution: Optional[Solution] = None
        self.history: List[Tuple[int, float]] = []
        self.status = AlgorithmStatus.INITIALIZED

    @abstractmethod
    def optimize(self, initial_solution: Any, max_iterations: int = 1000) -> OptimizationResult:
        """Führt die Optimierung durch"""
        pass

    def is_better(self, new_value: float, current_value: float) -> bool:
        """Prüft ob ein neuer Wert besser ist"""
        if self.optimization_type == OptimizationType.MINIMIZE:
            return new_value < current_value
        else:
            return new_value > current_value

    def compare_value(self) -> float:
        """Gibt den Vergleichswert für Initialisierung zurück"""
        if self.optimization_type == OptimizationType.MINIMIZE:
            return float('inf')
        else:
            return float('-inf')


# =============================================================================
# 1. SIMULATED ANNEALING - Metallurgisch inspirierte Optimierung
# =============================================================================

class SimulatedAnnealing(OptimizationAlgorithm):
    """
    Simulated Annealing Algorithmus.

    Inspiriert vom Abkühlen von Metallen:
    - Hohe Temperatur: Akzeptiere auch schlechtere Lösungen (Exploration)
    - Niedrige Temperatur: Nur bessere Lösungen (Exploitation)

    Akzeptanzwahrscheinlichkeit: P = exp(-ΔE/T)
    """

    def __init__(self, objective_function: Callable[[Any], float],
                 neighbor_function: Callable[[Any], Any],
                 optimization_type: OptimizationType = OptimizationType.MINIMIZE,
                 initial_temperature: float = 1000.0,
                 cooling_rate: float = 0.95,
                 cooling_schedule: CoolingSchedule = CoolingSchedule.EXPONENTIAL,
                 min_temperature: float = 0.01):
        super().__init__(objective_function, optimization_type)
        self.neighbor = neighbor_function
        self.initial_temp = initial_temperature
        self.cooling_rate = cooling_rate
        self.cooling_schedule = cooling_schedule
        self.min_temp = min_temperature
        self.temperature = initial_temperature

        # Adaptive Annealing Parameter
        self.accepted_moves = 0
        self.total_moves = 0
        self.target_acceptance = 0.4

    def optimize(self, initial_solution: Any, max_iterations: int = 1000) -> OptimizationResult:
        """
        Führt Simulated Annealing durch.

        Args:
            initial_solution: Startlösung
            max_iterations: Maximale Iterationen

        Returns:
            OptimizationResult mit bester gefundener Lösung
        """
        start_time = datetime.now()
        self.status = AlgorithmStatus.RUNNING
        self.temperature = self.initial_temp
        self.history = []

        # Initialisiere aktuelle und beste Lösung
        current_state = initial_solution
        current_value = self.objective(current_state)

        best_state = copy.deepcopy(current_state)
        best_value = current_value

        self.best_solution = Solution(
            state=best_state,
            value=best_value,
            iteration=0
        )
        self.history.append((0, best_value))

        # Hauptschleife
        for iteration in range(1, max_iterations + 1):
            # Generiere Nachbarlösung
            neighbor_state = self.neighbor(current_state)
            neighbor_value = self.objective(neighbor_state)

            # Entscheide ob Nachbar akzeptiert wird
            if self._accept(current_value, neighbor_value):
                current_state = neighbor_state
                current_value = neighbor_value
                self.accepted_moves += 1

                # Update beste Lösung
                if self.is_better(current_value, best_value):
                    best_state = copy.deepcopy(current_state)
                    best_value = current_value
                    self.best_solution = Solution(
                        state=best_state,
                        value=best_value,
                        iteration=iteration
                    )

            self.total_moves += 1
            self.history.append((iteration, best_value))

            # Kühle ab
            self._cool_down(iteration, max_iterations)

            # Prüfe Abbruchkriterium
            if self.temperature < self.min_temp:
                self.status = AlgorithmStatus.CONVERGED
                break

        if self.status == AlgorithmStatus.RUNNING:
            self.status = AlgorithmStatus.MAX_ITERATIONS

        elapsed = (datetime.now() - start_time).total_seconds() * 1000

        return OptimizationResult(
            best_solution=self.best_solution,
            history=self.history,
            algorithm="Simulated Annealing",
            status=self.status,
            iterations=iteration,
            elapsed_time_ms=elapsed,
            parameters={
                "initial_temperature": self.initial_temp,
                "cooling_rate": self.cooling_rate,
                "cooling_schedule": self.cooling_schedule.value,
                "final_temperature": self.temperature,
                "acceptance_rate": self.accepted_moves / max(1, self.total_moves)
            }
        )

    def _accept(self, current_value: float, new_value: float) -> bool:
        """
        Entscheidet ob eine neue Lösung akzeptiert wird.

        Bessere Lösungen werden immer akzeptiert.
        Schlechtere mit Wahrscheinlichkeit exp(-ΔE/T).
        """
        if self.is_better(new_value, current_value):
            return True

        # Berechne Akzeptanzwahrscheinlichkeit
        if self.optimization_type == OptimizationType.MINIMIZE:
            delta = new_value - current_value
        else:
            delta = current_value - new_value

        if self.temperature <= 0:
            return False

        probability = math.exp(-delta / self.temperature)
        return random.random() < probability

    def _cool_down(self, iteration: int, max_iterations: int):
        """Reduziert die Temperatur nach dem gewählten Schema"""
        if self.cooling_schedule == CoolingSchedule.EXPONENTIAL:
            self.temperature *= self.cooling_rate

        elif self.cooling_schedule == CoolingSchedule.LINEAR:
            self.temperature = self.initial_temp * (1 - iteration / max_iterations)

        elif self.cooling_schedule == CoolingSchedule.LOGARITHMIC:
            self.temperature = self.initial_temp / math.log(iteration + 2)

        elif self.cooling_schedule == CoolingSchedule.ADAPTIVE:
            # Passe Abkühlung basierend auf Akzeptanzrate an
            if self.total_moves > 0:
                acceptance_rate = self.accepted_moves / self.total_moves
                if acceptance_rate > self.target_acceptance:
                    # Zu viele Akzeptanzen → schneller abkühlen
                    self.temperature *= self.cooling_rate * 0.95
                else:
                    # Zu wenige Akzeptanzen → langsamer abkühlen
                    self.temperature *= self.cooling_rate * 1.02

    def reheat(self, factor: float = 2.0):
        """Erhöht die Temperatur (Reheating für Escape aus lokalen Minima)"""
        self.temperature = min(self.initial_temp, self.temperature * factor)
        self.accepted_moves = 0
        self.total_moves = 0


# =============================================================================
# 2. PARTICLE SWARM OPTIMIZATION - Schwarmverhalten
# =============================================================================

class ParticleSwarmOptimization(OptimizationAlgorithm):
    """
    Particle Swarm Optimization (PSO).

    Inspiriert vom Schwarmverhalten von Vögeln/Fischen:
    - Partikel bewegen sich durch den Lösungsraum
    - Jedes Partikel merkt sich seine beste Position
    - Der Schwarm kennt die global beste Position
    - Bewegung: Balance zwischen Exploration und Exploitation

    Geschwindigkeits-Update:
    v = w*v + c1*r1*(p_best - x) + c2*r2*(g_best - x)
    """

    def __init__(self, objective_function: Callable[[List[float]], float],
                 dimensions: int,
                 bounds: List[Tuple[float, float]],
                 optimization_type: OptimizationType = OptimizationType.MINIMIZE,
                 num_particles: int = 30,
                 inertia_weight: float = 0.7,
                 cognitive_weight: float = 1.5,
                 social_weight: float = 1.5,
                 topology: PSO_Topology = PSO_Topology.GLOBAL_BEST):
        super().__init__(objective_function, optimization_type)
        self.dimensions = dimensions
        self.bounds = bounds
        self.num_particles = num_particles
        self.w = inertia_weight        # Trägheitsgewicht
        self.c1 = cognitive_weight     # Kognitive Komponente
        self.c2 = social_weight        # Soziale Komponente
        self.topology = topology

        self.particles: List[Particle] = []
        self.global_best_position: List[float] = []
        self.global_best_value: float = self.compare_value()

    def optimize(self, initial_solution: Any = None, max_iterations: int = 1000) -> OptimizationResult:
        """
        Führt PSO durch.

        Args:
            initial_solution: Optional - wird hier ignoriert, da Partikel zufällig initialisiert
            max_iterations: Maximale Iterationen

        Returns:
            OptimizationResult
        """
        start_time = datetime.now()
        self.status = AlgorithmStatus.RUNNING
        self.history = []

        # Initialisiere Schwarm
        self._initialize_swarm()

        # Hauptschleife
        for iteration in range(max_iterations):
            for particle in self.particles:
                # Evaluiere aktuelle Position
                particle.current_value = self.objective(particle.position)

                # Update persönlich beste Position
                if self.is_better(particle.current_value, particle.best_value):
                    particle.best_position = particle.position.copy()
                    particle.best_value = particle.current_value

                # Update global beste Position
                if self.is_better(particle.current_value, self.global_best_value):
                    self.global_best_position = particle.position.copy()
                    self.global_best_value = particle.current_value

            # Update Geschwindigkeiten und Positionen
            for particle in self.particles:
                self._update_particle(particle)

            self.history.append((iteration, self.global_best_value))

            # Adaptive Inertia (optional)
            self._adapt_inertia(iteration, max_iterations)

        self.status = AlgorithmStatus.MAX_ITERATIONS
        elapsed = (datetime.now() - start_time).total_seconds() * 1000

        self.best_solution = Solution(
            state=self.global_best_position,
            value=self.global_best_value,
            iteration=max_iterations
        )

        return OptimizationResult(
            best_solution=self.best_solution,
            history=self.history,
            algorithm="Particle Swarm Optimization",
            status=self.status,
            iterations=max_iterations,
            elapsed_time_ms=elapsed,
            parameters={
                "num_particles": self.num_particles,
                "inertia_weight": self.w,
                "cognitive_weight": self.c1,
                "social_weight": self.c2,
                "topology": self.topology.value,
                "dimensions": self.dimensions
            }
        )

    def _initialize_swarm(self):
        """Initialisiert den Partikelschwarm"""
        self.particles = []
        self.global_best_value = self.compare_value()

        for _ in range(self.num_particles):
            # Zufällige Position innerhalb der Grenzen
            position = [
                random.uniform(low, high)
                for low, high in self.bounds
            ]

            # Zufällige Geschwindigkeit
            velocity = [
                random.uniform(-(high-low)/10, (high-low)/10)
                for low, high in self.bounds
            ]

            value = self.objective(position)

            particle = Particle(
                position=position,
                velocity=velocity,
                best_position=position.copy(),
                best_value=value,
                current_value=value
            )

            self.particles.append(particle)

            # Update globales Bestes
            if self.is_better(value, self.global_best_value):
                self.global_best_position = position.copy()
                self.global_best_value = value

    def _update_particle(self, particle: Particle):
        """Aktualisiert Geschwindigkeit und Position eines Partikels"""
        new_velocity = []
        new_position = []

        for d in range(self.dimensions):
            r1 = random.random()
            r2 = random.random()

            # Geschwindigkeits-Update
            # v = w*v + c1*r1*(p_best - x) + c2*r2*(g_best - x)
            cognitive = self.c1 * r1 * (particle.best_position[d] - particle.position[d])
            social = self.c2 * r2 * (self.global_best_position[d] - particle.position[d])
            v = self.w * particle.velocity[d] + cognitive + social

            # Geschwindigkeitsbegrenzung
            max_v = (self.bounds[d][1] - self.bounds[d][0]) / 2
            v = max(-max_v, min(max_v, v))
            new_velocity.append(v)

            # Positions-Update
            x = particle.position[d] + v

            # Positionsbegrenzung (reflektierende Grenzen)
            if x < self.bounds[d][0]:
                x = self.bounds[d][0]
                new_velocity[d] *= -0.5  # Reflexion
            elif x > self.bounds[d][1]:
                x = self.bounds[d][1]
                new_velocity[d] *= -0.5  # Reflexion

            new_position.append(x)

        particle.velocity = new_velocity
        particle.position = new_position

    def _adapt_inertia(self, iteration: int, max_iterations: int):
        """Adaptiert das Trägheitsgewicht über die Zeit"""
        # Linear abnehmende Inertia
        w_max = 0.9
        w_min = 0.4
        self.w = w_max - (w_max - w_min) * iteration / max_iterations

    def get_swarm_diversity(self) -> float:
        """Berechnet die Diversität des Schwarms"""
        if not self.particles:
            return 0.0

        # Durchschnittliche Distanz zum Zentrum
        center = [
            sum(p.position[d] for p in self.particles) / len(self.particles)
            for d in range(self.dimensions)
        ]

        total_distance = 0.0
        for particle in self.particles:
            distance = sum(
                (particle.position[d] - center[d]) ** 2
                for d in range(self.dimensions)
            ) ** 0.5
            total_distance += distance

        return total_distance / len(self.particles)


# =============================================================================
# 3. BRANCH AND BOUND - Systematische Enumeration
# =============================================================================

class BranchAndBound(OptimizationAlgorithm):
    """
    Branch and Bound Algorithmus.

    Systematische Enumeration des Lösungsraums mit:
    - Branching: Aufteilen des Problems in Teilprobleme
    - Bounding: Berechnung von Schranken
    - Pruning: Abschneiden von Zweigen die nicht besser sein können

    Garantiert optimale Lösung (wenn vollständig durchlaufen).
    """

    def __init__(self, objective_function: Callable[[Any], float],
                 branching_function: Callable[[Any], List[Any]],
                 bounding_function: Callable[[Any], float],
                 is_complete_function: Callable[[Any], bool],
                 optimization_type: OptimizationType = OptimizationType.MINIMIZE,
                 strategy: BranchStrategy = BranchStrategy.BEST_FIRST):
        super().__init__(objective_function, optimization_type)
        self.branch = branching_function
        self.bound = bounding_function
        self.is_complete = is_complete_function
        self.strategy = strategy

        self.nodes_explored = 0
        self.nodes_pruned = 0

    def optimize(self, initial_solution: Any, max_iterations: int = 10000) -> OptimizationResult:
        """
        Führt Branch and Bound durch.

        Args:
            initial_solution: Anfangszustand (normalerweise leer/partial)
            max_iterations: Maximale Knoten zu explorieren

        Returns:
            OptimizationResult
        """
        start_time = datetime.now()
        self.status = AlgorithmStatus.RUNNING
        self.history = []
        self.nodes_explored = 0
        self.nodes_pruned = 0

        # Beste bekannte Lösung
        best_value = self.compare_value()
        best_solution = None

        # Initialisiere mit Wurzelknoten
        root = BBNode(
            state=initial_solution,
            bound=self.bound(initial_solution),
            depth=0
        )

        # Prioritätswarteschlange (Heap)
        if self.strategy == BranchStrategy.BEST_FIRST:
            # Min-Heap für Minimierung, Max-Heap für Maximierung
            queue = [root]
            heapq.heapify(queue)
        else:
            queue = [root]  # LIFO für Depth-First, FIFO für Breadth-First

        while queue and self.nodes_explored < max_iterations:
            # Wähle nächsten Knoten basierend auf Strategie
            if self.strategy == BranchStrategy.BEST_FIRST:
                node = heapq.heappop(queue)
            elif self.strategy == BranchStrategy.DEPTH_FIRST:
                node = queue.pop()  # LIFO
            else:  # BREADTH_FIRST
                node = queue.pop(0)  # FIFO

            self.nodes_explored += 1

            # Pruning: Kann dieser Zweig besser sein?
            if not self._can_improve(node.bound, best_value):
                self.nodes_pruned += 1
                continue

            # Ist es eine vollständige Lösung?
            if self.is_complete(node.state):
                value = self.objective(node.state)
                if self.is_better(value, best_value):
                    best_value = value
                    best_solution = copy.deepcopy(node.state)
                    self.history.append((self.nodes_explored, best_value))
                continue

            # Branching: Erzeuge Kindknoten
            children_states = self.branch(node.state)

            for child_state in children_states:
                child_bound = self.bound(child_state)

                # Pruning beim Erstellen
                if self._can_improve(child_bound, best_value):
                    child = BBNode(
                        state=child_state,
                        bound=child_bound,
                        depth=node.depth + 1,
                        parent=node
                    )

                    if self.strategy == BranchStrategy.BEST_FIRST:
                        heapq.heappush(queue, child)
                    else:
                        queue.append(child)
                else:
                    self.nodes_pruned += 1

        # Bestimme Status
        if not queue:
            self.status = AlgorithmStatus.CONVERGED
        else:
            self.status = AlgorithmStatus.MAX_ITERATIONS

        elapsed = (datetime.now() - start_time).total_seconds() * 1000

        self.best_solution = Solution(
            state=best_solution,
            value=best_value,
            iteration=self.nodes_explored
        ) if best_solution else Solution(state=initial_solution, value=best_value)

        return OptimizationResult(
            best_solution=self.best_solution,
            history=self.history,
            algorithm="Branch and Bound",
            status=self.status,
            iterations=self.nodes_explored,
            elapsed_time_ms=elapsed,
            parameters={
                "strategy": self.strategy.value,
                "nodes_explored": self.nodes_explored,
                "nodes_pruned": self.nodes_pruned,
                "pruning_efficiency": self.nodes_pruned / max(1, self.nodes_explored + self.nodes_pruned)
            }
        )

    def _can_improve(self, bound: float, best_value: float) -> bool:
        """Prüft ob die Schranke besser sein kann als die beste Lösung"""
        if self.optimization_type == OptimizationType.MINIMIZE:
            return bound < best_value
        else:
            return bound > best_value


# =============================================================================
# KOMBINIERTER APPROXIMATION ENGINE
# =============================================================================

class ApproximationEngine:
    """
    Kombiniert alle Approximationsalgorithmen zu einem integrierten System.
    """

    def __init__(self):
        self.results: List[OptimizationResult] = []
        self.comparison_log: List[Dict] = []

    # -------------------------------------------------------------------------
    # FACTORY METHODS
    # -------------------------------------------------------------------------

    def create_simulated_annealing(self,
                                    objective: Callable[[Any], float],
                                    neighbor: Callable[[Any], Any],
                                    **kwargs) -> SimulatedAnnealing:
        """Erstellt einen Simulated Annealing Optimierer"""
        return SimulatedAnnealing(objective, neighbor, **kwargs)

    def create_pso(self,
                    objective: Callable[[List[float]], float],
                    dimensions: int,
                    bounds: List[Tuple[float, float]],
                    **kwargs) -> ParticleSwarmOptimization:
        """Erstellt einen PSO Optimierer"""
        return ParticleSwarmOptimization(objective, dimensions, bounds, **kwargs)

    def create_branch_and_bound(self,
                                 objective: Callable[[Any], float],
                                 branch: Callable[[Any], List[Any]],
                                 bound: Callable[[Any], float],
                                 is_complete: Callable[[Any], bool],
                                 **kwargs) -> BranchAndBound:
        """Erstellt einen Branch and Bound Optimierer"""
        return BranchAndBound(objective, branch, bound, is_complete, **kwargs)

    # -------------------------------------------------------------------------
    # PROBLEM-SPEZIFISCHE LÖSUNGEN
    # -------------------------------------------------------------------------

    def solve_continuous_optimization(self,
                                       objective: Callable[[List[float]], float],
                                       dimensions: int,
                                       bounds: List[Tuple[float, float]],
                                       method: str = "pso") -> OptimizationResult:
        """
        Löst ein kontinuierliches Optimierungsproblem.

        Args:
            objective: Zielfunktion f(x) -> float
            dimensions: Anzahl Variablen
            bounds: [(min, max)] für jede Variable
            method: "pso" oder "sa"
        """
        if method == "pso":
            optimizer = self.create_pso(objective, dimensions, bounds)
            result = optimizer.optimize(max_iterations=500)
        else:
            # Simulated Annealing für kontinuierliche Probleme
            def neighbor(x):
                return [
                    max(bounds[i][0], min(bounds[i][1],
                        xi + random.gauss(0, (bounds[i][1] - bounds[i][0]) / 10)))
                    for i, xi in enumerate(x)
                ]

            initial = [random.uniform(low, high) for low, high in bounds]
            optimizer = self.create_simulated_annealing(objective, neighbor)
            result = optimizer.optimize(initial, max_iterations=5000)

        self.results.append(result)
        return result

    def solve_combinatorial_optimization(self,
                                          objective: Callable[[List[int]], float],
                                          n_items: int,
                                          method: str = "sa") -> OptimizationResult:
        """
        Löst ein kombinatorisches Optimierungsproblem (z.B. TSP, Knapsack).

        Args:
            objective: Zielfunktion f(permutation) -> float
            n_items: Anzahl Elemente
            method: "sa" oder "bb"
        """
        if method == "sa":
            # Nachbarschaft: 2-opt swap
            def neighbor(perm):
                new_perm = perm.copy()
                i, j = sorted(random.sample(range(n_items), 2))
                new_perm[i:j+1] = reversed(new_perm[i:j+1])
                return new_perm

            initial = list(range(n_items))
            random.shuffle(initial)

            optimizer = self.create_simulated_annealing(objective, neighbor)
            result = optimizer.optimize(initial, max_iterations=10000)

        else:
            # Branch and Bound für kombinatorische Probleme
            def branch(partial):
                if len(partial) >= n_items:
                    return []
                used = set(partial)
                return [partial + [i] for i in range(n_items) if i not in used]

            def bound(partial):
                # Einfache untere Schranke
                return objective(partial + list(set(range(n_items)) - set(partial)))

            def is_complete(partial):
                return len(partial) == n_items

            optimizer = self.create_branch_and_bound(
                objective, branch, bound, is_complete,
                strategy=BranchStrategy.BEST_FIRST
            )
            result = optimizer.optimize([], max_iterations=10000)

        self.results.append(result)
        return result

    def compare_algorithms(self,
                            objective: Callable[[List[float]], float],
                            dimensions: int,
                            bounds: List[Tuple[float, float]],
                            runs: int = 5) -> Dict[str, Any]:
        """
        Vergleicht verschiedene Algorithmen auf demselben Problem.
        """
        comparison = {
            "problem": f"{dimensions}D Optimization",
            "runs": runs,
            "algorithms": {}
        }

        # PSO
        pso_results = []
        for _ in range(runs):
            result = self.solve_continuous_optimization(
                objective, dimensions, bounds, method="pso"
            )
            pso_results.append(result.best_solution.value)

        comparison["algorithms"]["PSO"] = {
            "best": min(pso_results),
            "worst": max(pso_results),
            "mean": sum(pso_results) / len(pso_results),
            "std": (sum((x - sum(pso_results)/len(pso_results))**2 for x in pso_results) / len(pso_results)) ** 0.5
        }

        # Simulated Annealing
        sa_results = []
        for _ in range(runs):
            result = self.solve_continuous_optimization(
                objective, dimensions, bounds, method="sa"
            )
            sa_results.append(result.best_solution.value)

        comparison["algorithms"]["SA"] = {
            "best": min(sa_results),
            "worst": max(sa_results),
            "mean": sum(sa_results) / len(sa_results),
            "std": (sum((x - sum(sa_results)/len(sa_results))**2 for x in sa_results) / len(sa_results)) ** 0.5
        }

        self.comparison_log.append(comparison)
        return comparison

    def get_summary(self) -> str:
        """Gibt eine Zusammenfassung aller Optimierungen"""
        summary = ["=" * 60]
        summary.append("APPROXIMATION ENGINE - Zusammenfassung")
        summary.append("=" * 60)

        summary.append(f"\nDurchgeführte Optimierungen: {len(self.results)}")

        # Gruppiere nach Algorithmus
        by_algorithm = defaultdict(list)
        for result in self.results:
            by_algorithm[result.algorithm].append(result)

        for algo, results in by_algorithm.items():
            summary.append(f"\n--- {algo} ---")
            summary.append(f"Läufe: {len(results)}")
            values = [r.best_solution.value for r in results]
            summary.append(f"Beste Lösung: {min(values):.6f}")
            summary.append(f"Durchschnitt: {sum(values)/len(values):.6f}")

            avg_time = sum(r.elapsed_time_ms for r in results) / len(results)
            summary.append(f"Durchschnittliche Zeit: {avg_time:.1f}ms")

        return "\n".join(summary)


# =============================================================================
# BENCHMARK-FUNKTIONEN
# =============================================================================

class BenchmarkFunctions:
    """Standard-Benchmark-Funktionen für Optimierung"""

    @staticmethod
    def sphere(x: List[float]) -> float:
        """Sphere Function - Minimum bei (0, 0, ..., 0)"""
        return sum(xi ** 2 for xi in x)

    @staticmethod
    def rastrigin(x: List[float]) -> float:
        """Rastrigin Function - Viele lokale Minima"""
        A = 10
        n = len(x)
        return A * n + sum(xi**2 - A * math.cos(2 * math.pi * xi) for xi in x)

    @staticmethod
    def rosenbrock(x: List[float]) -> float:
        """Rosenbrock Function - Banana Valley"""
        return sum(100 * (x[i+1] - x[i]**2)**2 + (1 - x[i])**2
                   for i in range(len(x) - 1))

    @staticmethod
    def ackley(x: List[float]) -> float:
        """Ackley Function - Viele lokale Minima"""
        n = len(x)
        sum1 = sum(xi**2 for xi in x)
        sum2 = sum(math.cos(2 * math.pi * xi) for xi in x)
        return -20 * math.exp(-0.2 * math.sqrt(sum1 / n)) \
               - math.exp(sum2 / n) + 20 + math.e

    @staticmethod
    def schwefel(x: List[float]) -> float:
        """Schwefel Function - Globales Minimum weit von lokalen"""
        n = len(x)
        return 418.9829 * n - sum(xi * math.sin(math.sqrt(abs(xi))) for xi in x)


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_approximation_engine() -> ApproximationEngine:
    """Erstellt eine Approximation Engine"""
    return ApproximationEngine()


# =============================================================================
# BEISPIEL / TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("🔬 Approximation Algorithms Engine - Demo\n")

    engine = create_approximation_engine()

    # Test Simulated Annealing auf Rastrigin
    print("--- Simulated Annealing auf Rastrigin ---")
    result_sa = engine.solve_continuous_optimization(
        BenchmarkFunctions.rastrigin,
        dimensions=5,
        bounds=[(-5.12, 5.12)] * 5,
        method="sa"
    )
    print(f"Beste Lösung: {result_sa.best_solution.value:.6f}")
    print(f"Status: {result_sa.status.value}")
    print(f"Zeit: {result_sa.elapsed_time_ms:.1f}ms")

    # Test PSO auf Sphere
    print("\n--- PSO auf Sphere Function ---")
    result_pso = engine.solve_continuous_optimization(
        BenchmarkFunctions.sphere,
        dimensions=10,
        bounds=[(-100, 100)] * 10,
        method="pso"
    )
    print(f"Beste Lösung: {result_pso.best_solution.value:.6f}")
    print(f"Position: {[f'{x:.4f}' for x in result_pso.best_solution.state[:3]]}...")
    print(f"Zeit: {result_pso.elapsed_time_ms:.1f}ms")

    # Test Branch and Bound auf kleinem TSP
    print("\n--- Branch and Bound auf Mini-TSP ---")
    # Distanzmatrix für 5 Städte
    distances = [
        [0, 10, 15, 20, 25],
        [10, 0, 35, 25, 30],
        [15, 35, 0, 30, 20],
        [20, 25, 30, 0, 15],
        [25, 30, 20, 15, 0]
    ]

    def tsp_cost(route):
        if len(route) < 2:
            return 0
        cost = sum(distances[route[i]][route[i+1]] for i in range(len(route)-1))
        if len(route) == 5:
            cost += distances[route[-1]][route[0]]  # Zurück zum Start
        return cost

    def tsp_branch(partial):
        if len(partial) >= 5:
            return []
        used = set(partial)
        return [partial + [i] for i in range(5) if i not in used]

    def tsp_bound(partial):
        if not partial:
            return 0
        return tsp_cost(partial)  # Einfache Schranke

    def tsp_complete(partial):
        return len(partial) == 5

    bb = engine.create_branch_and_bound(
        tsp_cost, tsp_branch, tsp_bound, tsp_complete,
        strategy=BranchStrategy.BEST_FIRST
    )
    result_bb = bb.optimize([], max_iterations=1000)
    print(f"Beste Route: {result_bb.best_solution.state}")
    print(f"Kosten: {result_bb.best_solution.value}")
    print(f"Knoten exploriert: {result_bb.parameters['nodes_explored']}")
    print(f"Knoten gepruned: {result_bb.parameters['nodes_pruned']}")

    # Algorithmen-Vergleich
    print("\n--- Algorithmen-Vergleich auf Ackley ---")
    comparison = engine.compare_algorithms(
        BenchmarkFunctions.ackley,
        dimensions=5,
        bounds=[(-5, 5)] * 5,
        runs=3
    )
    for algo, stats in comparison["algorithms"].items():
        print(f"{algo}: best={stats['best']:.4f}, mean={stats['mean']:.4f}")

    # Zusammenfassung
    print("\n" + engine.get_summary())
