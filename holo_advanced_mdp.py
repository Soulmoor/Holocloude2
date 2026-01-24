#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
  HOLO ADVANCED MDP v1.0
  Erweiterte Markov-Entscheidungsprozesse für Holocloude
================================================================================

FEATURES:
1. Bellman-Gleichungen
   - Value Iteration
   - Policy Iteration
   - Optimale Wertfunktion

2. Temporal Difference Learning
   - TD(0), TD(λ)
   - SARSA
   - Q-Learning Varianten

3. Policy Gradient Methoden
   - REINFORCE
   - Actor-Critic
   - Advantage Estimation

4. Partially Observable MDPs (POMDP)
   - Belief States
   - Belief Update
   - POMDP Planung

5. Model-based RL
   - Dynamik-Modell lernen
   - Dyna-Q
   - Planung mit Modell

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
import copy

logger = logging.getLogger("HoloAdvancedMDP")


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # MDP Grundlagen
    "MDP",
    "MDPState",
    "MDPAction",
    "TransitionModel",
    "RewardFunction",

    # Bellman
    "BellmanEngine",
    "ValueFunction",
    "Policy",

    # TD Learning
    "TDLearningEngine",
    "SARSAAgent",
    "QLearningAgent",
    "TDLambdaAgent",

    # Policy Gradient
    "PolicyGradientEngine",
    "REINFORCEAgent",
    "ActorCriticAgent",
    "AdvantageEstimator",

    # POMDP
    "POMDPEngine",
    "POMDP",
    "BeliefState",
    "Observation",

    # Model-based
    "ModelBasedEngine",
    "DynaQAgent",
    "WorldModel",

    # Kombiniert
    "AdvancedMDPEngine",

    # Enums
    "LearningAlgorithm",
    "ExplorationStrategy",

    # Factory
    "create_bellman_engine",
    "create_td_learning_engine",
    "create_policy_gradient_engine",
    "create_pomdp_engine",
    "get_advanced_mdp_engine",
]


# =============================================================================
# ENUMS
# =============================================================================

class LearningAlgorithm(Enum):
    """Lernalgorithmen"""
    VALUE_ITERATION = "value_iteration"
    POLICY_ITERATION = "policy_iteration"
    Q_LEARNING = "q_learning"
    SARSA = "sarsa"
    TD_LAMBDA = "td_lambda"
    REINFORCE = "reinforce"
    ACTOR_CRITIC = "actor_critic"
    DYNA_Q = "dyna_q"


class ExplorationStrategy(Enum):
    """Explorationsstrategien"""
    EPSILON_GREEDY = "epsilon_greedy"
    BOLTZMANN = "boltzmann"
    UCB = "ucb"                          # Upper Confidence Bound
    THOMPSON_SAMPLING = "thompson"


# =============================================================================
# DATENSTRUKTUREN
# =============================================================================

@dataclass
class MDPState:
    """Ein Zustand im MDP"""
    id: str
    features: Dict[str, float] = field(default_factory=dict)
    is_terminal: bool = False

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, MDPState):
            return self.id == other.id
        return False


@dataclass
class MDPAction:
    """Eine Aktion im MDP"""
    id: str
    cost: float = 0.0

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, MDPAction):
            return self.id == other.id
        return False


@dataclass
class TransitionModel:
    """
    Übergangsmodell P(s'|s,a).
    Speichert Übergangswahrscheinlichkeiten.
    """
    transitions: Dict[Tuple[str, str], Dict[str, float]] = field(default_factory=dict)

    def get_probability(self, state: str, action: str, next_state: str) -> float:
        """P(next_state | state, action)"""
        key = (state, action)
        if key in self.transitions:
            return self.transitions[key].get(next_state, 0.0)
        return 0.0

    def get_next_states(self, state: str, action: str) -> Dict[str, float]:
        """Gibt alle möglichen Nachfolgezustände mit Wahrscheinlichkeiten"""
        key = (state, action)
        return self.transitions.get(key, {})

    def set_transition(self, state: str, action: str,
                       next_state: str, probability: float):
        """Setzt eine Übergangswahrscheinlichkeit"""
        key = (state, action)
        if key not in self.transitions:
            self.transitions[key] = {}
        self.transitions[key][next_state] = probability


@dataclass
class RewardFunction:
    """
    Belohnungsfunktion R(s,a,s').
    """
    rewards: Dict[Tuple[str, str, str], float] = field(default_factory=dict)
    state_rewards: Dict[str, float] = field(default_factory=dict)

    def get_reward(self, state: str, action: str,
                   next_state: Optional[str] = None) -> float:
        """Gibt die Belohnung zurück"""
        if next_state:
            key = (state, action, next_state)
            if key in self.rewards:
                return self.rewards[key]

        # Fallback auf Zustandsbelohnung
        return self.state_rewards.get(next_state or state, 0.0)

    def set_reward(self, state: str, action: str,
                   next_state: str, reward: float):
        """Setzt eine Belohnung"""
        self.rewards[(state, action, next_state)] = reward


@dataclass
class MDP:
    """
    Ein vollständiger Markov-Entscheidungsprozess.
    MDP = (S, A, P, R, γ)
    """
    states: List[MDPState]
    actions: List[MDPAction]
    transition_model: TransitionModel
    reward_function: RewardFunction
    gamma: float = 0.95  # Diskontfaktor
    initial_state: Optional[MDPState] = None

    def get_state_ids(self) -> List[str]:
        return [s.id for s in self.states]

    def get_action_ids(self) -> List[str]:
        return [a.id for a in self.actions]


@dataclass
class ValueFunction:
    """Wertfunktion V(s) oder Q(s,a)"""
    values: Dict[str, float] = field(default_factory=dict)
    q_values: Dict[Tuple[str, str], float] = field(default_factory=dict)

    def V(self, state: str) -> float:
        """V(s) - Zustandswert"""
        return self.values.get(state, 0.0)

    def Q(self, state: str, action: str) -> float:
        """Q(s,a) - Aktionswert"""
        return self.q_values.get((state, action), 0.0)

    def set_V(self, state: str, value: float):
        self.values[state] = value

    def set_Q(self, state: str, action: str, value: float):
        self.q_values[(state, action)] = value


@dataclass
class Policy:
    """
    Eine Policy π(a|s).
    Kann deterministisch oder stochastisch sein.
    """
    action_probs: Dict[str, Dict[str, float]] = field(default_factory=dict)
    deterministic: Dict[str, str] = field(default_factory=dict)

    def get_action(self, state: str) -> str:
        """Gibt die beste Aktion für einen Zustand zurück"""
        if state in self.deterministic:
            return self.deterministic[state]

        if state in self.action_probs:
            probs = self.action_probs[state]
            return max(probs.keys(), key=lambda a: probs[a])

        return ""

    def get_probability(self, state: str, action: str) -> float:
        """π(a|s)"""
        if state in self.deterministic:
            return 1.0 if self.deterministic[state] == action else 0.0

        if state in self.action_probs:
            return self.action_probs[state].get(action, 0.0)

        return 0.0

    def set_deterministic(self, state: str, action: str):
        """Setzt deterministische Aktion"""
        self.deterministic[state] = action

    def set_stochastic(self, state: str, action_probs: Dict[str, float]):
        """Setzt stochastische Policy"""
        self.action_probs[state] = action_probs


# =============================================================================
# BELLMAN ENGINE
# =============================================================================

class BellmanEngine:
    """
    Engine für Bellman-Gleichungen und dynamische Programmierung.

    Bellman-Gleichung für V:
    V*(s) = max_a Σ_s' P(s'|s,a) [R(s,a,s') + γ V*(s')]

    Bellman-Gleichung für Q:
    Q*(s,a) = Σ_s' P(s'|s,a) [R(s,a,s') + γ max_a' Q*(s',a')]
    """

    def __init__(self):
        logger.info("BellmanEngine initialisiert")

    def value_iteration(self, mdp: MDP,
                        theta: float = 0.0001,
                        max_iterations: int = 1000) -> Tuple[ValueFunction, Policy]:
        """
        Value Iteration Algorithmus.

        Iteriert die Bellman-Optimalitätsgleichung bis zur Konvergenz:
        V_{k+1}(s) = max_a Σ_s' P(s'|s,a) [R(s,a,s') + γ V_k(s')]
        """
        V = ValueFunction()
        states = mdp.get_state_ids()
        actions = mdp.get_action_ids()

        # Initialisiere V(s) = 0
        for s in states:
            V.set_V(s, 0.0)

        for iteration in range(max_iterations):
            delta = 0.0

            for s in states:
                # Terminale Zustände haben Wert 0
                state_obj = next((st for st in mdp.states if st.id == s), None)
                if state_obj and state_obj.is_terminal:
                    continue

                v_old = V.V(s)

                # Bellman Update: V(s) = max_a Q(s,a)
                best_value = float('-inf')
                for a in actions:
                    q_value = self._compute_q_value(mdp, V, s, a)
                    if q_value > best_value:
                        best_value = q_value

                V.set_V(s, best_value if best_value > float('-inf') else 0)

                delta = max(delta, abs(v_old - V.V(s)))

            if delta < theta:
                logger.info(f"Value Iteration konvergiert nach {iteration + 1} Iterationen")
                break

        # Extrahiere optimale Policy
        policy = self._extract_policy(mdp, V)

        return V, policy

    def policy_iteration(self, mdp: MDP,
                         max_iterations: int = 100) -> Tuple[ValueFunction, Policy]:
        """
        Policy Iteration Algorithmus.

        1. Policy Evaluation: Berechne V^π
        2. Policy Improvement: Verbessere π
        """
        states = mdp.get_state_ids()
        actions = mdp.get_action_ids()

        # Initialisiere zufällige Policy
        policy = Policy()
        for s in states:
            policy.set_deterministic(s, random.choice(actions))

        for iteration in range(max_iterations):
            # Policy Evaluation
            V = self._policy_evaluation(mdp, policy)

            # Policy Improvement
            policy_stable = True
            for s in states:
                old_action = policy.get_action(s)

                # Finde beste Aktion
                best_action = old_action
                best_value = float('-inf')
                for a in actions:
                    q_value = self._compute_q_value(mdp, V, s, a)
                    if q_value > best_value:
                        best_value = q_value
                        best_action = a

                policy.set_deterministic(s, best_action)

                if old_action != best_action:
                    policy_stable = False

            if policy_stable:
                logger.info(f"Policy Iteration konvergiert nach {iteration + 1} Iterationen")
                break

        return V, policy

    def _compute_q_value(self, mdp: MDP, V: ValueFunction,
                         state: str, action: str) -> float:
        """
        Berechnet Q(s,a) = Σ_s' P(s'|s,a) [R(s,a,s') + γ V(s')]

        Dies ist die Bellman-Gleichung für Aktionswerte.
        """
        q_value = 0.0
        next_states = mdp.transition_model.get_next_states(state, action)

        for next_state, prob in next_states.items():
            reward = mdp.reward_function.get_reward(state, action, next_state)
            q_value += prob * (reward + mdp.gamma * V.V(next_state))

        return q_value

    def _policy_evaluation(self, mdp: MDP, policy: Policy,
                           theta: float = 0.0001,
                           max_iterations: int = 1000) -> ValueFunction:
        """
        Policy Evaluation: Berechnet V^π.

        V^π(s) = Σ_a π(a|s) Σ_s' P(s'|s,a) [R(s,a,s') + γ V^π(s')]
        """
        V = ValueFunction()
        states = mdp.get_state_ids()

        for s in states:
            V.set_V(s, 0.0)

        for _ in range(max_iterations):
            delta = 0.0

            for s in states:
                v_old = V.V(s)

                # V^π(s) = Σ_a π(a|s) Q^π(s,a)
                new_value = 0.0
                action = policy.get_action(s)
                if action:
                    new_value = self._compute_q_value(mdp, V, s, action)

                V.set_V(s, new_value)
                delta = max(delta, abs(v_old - V.V(s)))

            if delta < theta:
                break

        return V

    def _extract_policy(self, mdp: MDP, V: ValueFunction) -> Policy:
        """Extrahiert die greedy Policy aus der Wertfunktion"""
        policy = Policy()
        states = mdp.get_state_ids()
        actions = mdp.get_action_ids()

        for s in states:
            best_action = actions[0] if actions else ""
            best_value = float('-inf')

            for a in actions:
                q_value = self._compute_q_value(mdp, V, s, a)
                if q_value > best_value:
                    best_value = q_value
                    best_action = a

            policy.set_deterministic(s, best_action)

        return policy

    def bellman_backup(self, mdp: MDP, V: ValueFunction,
                       state: str) -> float:
        """
        Ein einzelnes Bellman Backup für Zustand s.
        Gibt max_a Q(s,a) zurück.
        """
        best_value = float('-inf')
        for a in mdp.get_action_ids():
            q_value = self._compute_q_value(mdp, V, state, a)
            best_value = max(best_value, q_value)
        return best_value if best_value > float('-inf') else 0.0


# =============================================================================
# TD LEARNING ENGINE
# =============================================================================

class TDLearningEngine:
    """
    Engine für Temporal Difference Learning.
    """

    def __init__(self):
        logger.info("TDLearningEngine initialisiert")

    def td_zero(self, mdp: MDP, policy: Policy,
                alpha: float = 0.1,
                episodes: int = 1000) -> ValueFunction:
        """
        TD(0) Algorithmus für Policy Evaluation.

        V(s) ← V(s) + α [r + γ V(s') - V(s)]

        Der TD-Error δ = r + γ V(s') - V(s) ist der Unterschied
        zwischen der beobachteten Belohnung plus geschätztem zukünftigem Wert
        und dem aktuellen geschätzten Wert.
        """
        V = ValueFunction()
        states = mdp.get_state_ids()

        for s in states:
            V.set_V(s, 0.0)

        for _ in range(episodes):
            # Starte in zufälligem Zustand
            state = random.choice(states)

            while True:
                state_obj = next((s for s in mdp.states if s.id == state), None)
                if state_obj and state_obj.is_terminal:
                    break

                action = policy.get_action(state)
                next_states = mdp.transition_model.get_next_states(state, action)

                if not next_states:
                    break

                # Sample nächsten Zustand
                next_state = random.choices(
                    list(next_states.keys()),
                    weights=list(next_states.values())
                )[0]

                reward = mdp.reward_function.get_reward(state, action, next_state)

                # TD Update
                td_error = reward + mdp.gamma * V.V(next_state) - V.V(state)
                V.set_V(state, V.V(state) + alpha * td_error)

                state = next_state

        return V


class SARSAAgent:
    """
    SARSA Agent - On-Policy TD Control.

    Q(s,a) ← Q(s,a) + α [r + γ Q(s',a') - Q(s,a)]

    SARSA lernt die Aktionswertfunktion für die Policy, die es tatsächlich ausführt.
    """

    def __init__(self, actions: List[str], alpha: float = 0.1,
                 gamma: float = 0.95, epsilon: float = 0.1):
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.Q = ValueFunction()

    def get_action(self, state: str) -> str:
        """ε-greedy Aktionswahl"""
        if random.random() < self.epsilon:
            return random.choice(self.actions)

        # Greedy
        best_action = self.actions[0]
        best_value = self.Q.Q(state, best_action)

        for a in self.actions[1:]:
            q = self.Q.Q(state, a)
            if q > best_value:
                best_value = q
                best_action = a

        return best_action

    def update(self, state: str, action: str, reward: float,
               next_state: str, next_action: str):
        """SARSA Update"""
        current_q = self.Q.Q(state, action)
        next_q = self.Q.Q(next_state, next_action)

        # TD Error
        td_error = reward + self.gamma * next_q - current_q

        # Update
        new_q = current_q + self.alpha * td_error
        self.Q.set_Q(state, action, new_q)


class QLearningAgent:
    """
    Q-Learning Agent - Off-Policy TD Control.

    Q(s,a) ← Q(s,a) + α [r + γ max_a' Q(s',a') - Q(s,a)]

    Q-Learning lernt die optimale Aktionswertfunktion unabhängig
    von der ausgeführten Policy.
    """

    def __init__(self, actions: List[str], alpha: float = 0.1,
                 gamma: float = 0.95, epsilon: float = 0.1):
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.Q = ValueFunction()

    def get_action(self, state: str) -> str:
        """ε-greedy Aktionswahl"""
        if random.random() < self.epsilon:
            return random.choice(self.actions)

        return self._greedy_action(state)

    def _greedy_action(self, state: str) -> str:
        """Beste Aktion nach Q-Werten"""
        best_action = self.actions[0]
        best_value = self.Q.Q(state, best_action)

        for a in self.actions[1:]:
            q = self.Q.Q(state, a)
            if q > best_value:
                best_value = q
                best_action = a

        return best_action

    def update(self, state: str, action: str, reward: float,
               next_state: str, is_terminal: bool = False):
        """
        Q-Learning Update.

        Bellman-Optimalitätsgleichung für Q:
        Q*(s,a) = E[r + γ max_a' Q*(s',a')]
        """
        current_q = self.Q.Q(state, action)

        if is_terminal:
            max_next_q = 0.0
        else:
            max_next_q = max(self.Q.Q(next_state, a) for a in self.actions)

        # TD Error
        td_error = reward + self.gamma * max_next_q - current_q

        # Update
        new_q = current_q + self.alpha * td_error
        self.Q.set_Q(state, action, new_q)


class TDLambdaAgent:
    """
    TD(λ) Agent mit Eligibility Traces.

    Kombiniert TD(0) mit Monte Carlo durch Eligibility Traces.
    λ = 0: TD(0)
    λ = 1: Monte Carlo
    """

    def __init__(self, states: List[str], actions: List[str],
                 alpha: float = 0.1, gamma: float = 0.95,
                 lambda_: float = 0.9, epsilon: float = 0.1):
        self.states = states
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.lambda_ = lambda_
        self.epsilon = epsilon
        self.Q = ValueFunction()
        self.eligibility: Dict[Tuple[str, str], float] = {}

    def reset_eligibility(self):
        """Setzt Eligibility Traces zurück"""
        self.eligibility = {}

    def get_action(self, state: str) -> str:
        """ε-greedy Aktionswahl"""
        if random.random() < self.epsilon:
            return random.choice(self.actions)

        best_action = self.actions[0]
        best_value = self.Q.Q(state, best_action)

        for a in self.actions[1:]:
            q = self.Q.Q(state, a)
            if q > best_value:
                best_value = q
                best_action = a

        return best_action

    def update(self, state: str, action: str, reward: float,
               next_state: str, next_action: str):
        """TD(λ) Update mit Eligibility Traces"""
        # TD Error
        current_q = self.Q.Q(state, action)
        next_q = self.Q.Q(next_state, next_action)
        td_error = reward + self.gamma * next_q - current_q

        # Increment eligibility für aktuelle (s,a)
        key = (state, action)
        self.eligibility[key] = self.eligibility.get(key, 0) + 1

        # Update alle (s,a) Paare mit Eligibility
        for (s, a), e in list(self.eligibility.items()):
            # Update Q
            old_q = self.Q.Q(s, a)
            new_q = old_q + self.alpha * td_error * e
            self.Q.set_Q(s, a, new_q)

            # Decay Eligibility
            self.eligibility[(s, a)] = self.gamma * self.lambda_ * e

            # Entferne kleine Eligibilities
            if self.eligibility[(s, a)] < 0.0001:
                del self.eligibility[(s, a)]


# =============================================================================
# POLICY GRADIENT ENGINE
# =============================================================================

class PolicyGradientEngine:
    """
    Engine für Policy Gradient Methoden.
    """

    def __init__(self):
        logger.info("PolicyGradientEngine initialisiert")


class REINFORCEAgent:
    """
    REINFORCE Agent - Monte Carlo Policy Gradient.

    ∇J(θ) = E[Σ_t ∇log π_θ(a_t|s_t) G_t]

    wobei G_t = Σ_{k=t}^T γ^{k-t} r_k der Return ab Zeitpunkt t ist.
    """

    def __init__(self, states: List[str], actions: List[str],
                 alpha: float = 0.01, gamma: float = 0.95):
        self.states = states
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma

        # Policy Parameter: θ[s][a] = Präferenz für Aktion a in Zustand s
        self.theta: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {a: 0.0 for a in actions}
        )

    def _softmax(self, state: str) -> Dict[str, float]:
        """Berechnet Softmax über Aktionspräferenzen"""
        preferences = self.theta[state]
        max_pref = max(preferences.values())

        exp_prefs = {a: math.exp(p - max_pref) for a, p in preferences.items()}
        total = sum(exp_prefs.values())

        return {a: e / total for a, e in exp_prefs.items()}

    def get_action(self, state: str) -> str:
        """Sampelt Aktion aus Policy"""
        probs = self._softmax(state)
        actions = list(probs.keys())
        weights = list(probs.values())
        return random.choices(actions, weights=weights)[0]

    def get_policy_probability(self, state: str, action: str) -> float:
        """π_θ(a|s)"""
        probs = self._softmax(state)
        return probs.get(action, 0.0)

    def update_from_episode(self, episode: List[Tuple[str, str, float]]):
        """
        Update nach einer kompletten Episode.

        episode: Liste von (state, action, reward) Tupeln
        """
        T = len(episode)

        # Berechne Returns für jeden Zeitpunkt
        returns = []
        G = 0.0
        for t in range(T - 1, -1, -1):
            _, _, r = episode[t]
            G = r + self.gamma * G
            returns.insert(0, G)

        # Policy Gradient Update
        for t, (state, action, _) in enumerate(episode):
            G_t = returns[t]

            # ∇log π_θ(a|s) = I(a) - π_θ(·|s)
            # für Softmax Policy
            probs = self._softmax(state)

            for a in self.actions:
                indicator = 1.0 if a == action else 0.0
                grad = indicator - probs[a]

                # θ ← θ + α G_t ∇log π_θ(a|s)
                self.theta[state][a] += self.alpha * G_t * grad


class ActorCriticAgent:
    """
    Actor-Critic Agent.

    Actor: Policy π_θ(a|s)
    Critic: Value Function V_w(s)

    Verwendet TD-Error als Advantage:
    δ = r + γ V_w(s') - V_w(s)

    Actor Update: θ ← θ + α_θ δ ∇log π_θ(a|s)
    Critic Update: w ← w + α_w δ ∇V_w(s)
    """

    def __init__(self, states: List[str], actions: List[str],
                 alpha_actor: float = 0.01, alpha_critic: float = 0.1,
                 gamma: float = 0.95):
        self.states = states
        self.actions = actions
        self.alpha_actor = alpha_actor
        self.alpha_critic = alpha_critic
        self.gamma = gamma

        # Actor: Policy Parameter
        self.theta: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {a: 0.0 for a in actions}
        )

        # Critic: Value Function
        self.V: Dict[str, float] = defaultdict(float)

    def _softmax(self, state: str) -> Dict[str, float]:
        """Softmax Policy"""
        preferences = self.theta[state]
        max_pref = max(preferences.values()) if preferences else 0

        exp_prefs = {a: math.exp(p - max_pref) for a, p in preferences.items()}
        total = sum(exp_prefs.values())

        return {a: e / total for a, e in exp_prefs.items()}

    def get_action(self, state: str) -> str:
        """Sampelt Aktion aus Actor Policy"""
        probs = self._softmax(state)
        return random.choices(list(probs.keys()), weights=list(probs.values()))[0]

    def update(self, state: str, action: str, reward: float,
               next_state: str, is_terminal: bool = False):
        """Online Actor-Critic Update"""
        # TD Error (Advantage Estimate)
        if is_terminal:
            td_error = reward - self.V[state]
        else:
            td_error = reward + self.gamma * self.V[next_state] - self.V[state]

        # Critic Update
        self.V[state] += self.alpha_critic * td_error

        # Actor Update
        probs = self._softmax(state)
        for a in self.actions:
            indicator = 1.0 if a == action else 0.0
            grad = indicator - probs[a]
            self.theta[state][a] += self.alpha_actor * td_error * grad


class AdvantageEstimator:
    """
    Generalized Advantage Estimation (GAE).

    A^GAE(γ,λ)_t = Σ_{l=0}^∞ (γλ)^l δ_{t+l}

    wobei δ_t = r_t + γ V(s_{t+1}) - V(s_t)
    """

    def __init__(self, gamma: float = 0.95, lambda_: float = 0.95):
        self.gamma = gamma
        self.lambda_ = lambda_

    def estimate(self, rewards: List[float], values: List[float],
                 next_value: float) -> List[float]:
        """
        Berechnet GAE für eine Trajektorie.

        rewards: [r_0, r_1, ..., r_{T-1}]
        values: [V(s_0), V(s_1), ..., V(s_{T-1})]
        next_value: V(s_T) (oder 0 wenn Terminal)
        """
        T = len(rewards)
        advantages = [0.0] * T

        # Erweitere values um next_value
        all_values = values + [next_value]

        # Rückwärts berechnen
        gae = 0.0
        for t in range(T - 1, -1, -1):
            delta = rewards[t] + self.gamma * all_values[t + 1] - all_values[t]
            gae = delta + self.gamma * self.lambda_ * gae
            advantages[t] = gae

        return advantages


# =============================================================================
# POMDP ENGINE
# =============================================================================

@dataclass
class Observation:
    """Eine Beobachtung im POMDP"""
    id: str
    features: Dict[str, float] = field(default_factory=dict)


@dataclass
class BeliefState:
    """
    Belief State b(s) - Wahrscheinlichkeitsverteilung über Zustände.
    """
    distribution: Dict[str, float] = field(default_factory=dict)

    def get_probability(self, state: str) -> float:
        return self.distribution.get(state, 0.0)

    def set_probability(self, state: str, prob: float):
        self.distribution[state] = prob

    def normalize(self):
        """Normalisiert die Verteilung"""
        total = sum(self.distribution.values())
        if total > 0:
            self.distribution = {s: p / total for s, p in self.distribution.items()}

    def most_likely_state(self) -> str:
        """Gibt den wahrscheinlichsten Zustand zurück"""
        if not self.distribution:
            return ""
        return max(self.distribution.keys(), key=lambda s: self.distribution[s])

    def entropy(self) -> float:
        """Berechnet die Entropie des Belief State"""
        h = 0.0
        for p in self.distribution.values():
            if p > 0:
                h -= p * math.log(p)
        return h


@dataclass
class POMDP:
    """
    Partially Observable Markov Decision Process.
    POMDP = (S, A, O, P, R, Ω, γ)

    O: Beobachtungen
    Ω: Beobachtungsfunktion P(o|s',a)
    """
    states: List[MDPState]
    actions: List[MDPAction]
    observations: List[Observation]
    transition_model: TransitionModel                    # P(s'|s,a)
    reward_function: RewardFunction                      # R(s,a,s')
    observation_model: Dict[Tuple[str, str], Dict[str, float]]  # P(o|s',a)
    gamma: float = 0.95
    initial_belief: Optional[BeliefState] = None


class POMDPEngine:
    """
    Engine für Partially Observable MDPs.
    """

    def __init__(self):
        logger.info("POMDPEngine initialisiert")

    def belief_update(self, pomdp: POMDP, belief: BeliefState,
                      action: str, observation: str) -> BeliefState:
        """
        Bayesian Belief Update.

        b'(s') = η P(o|s',a) Σ_s P(s'|s,a) b(s)

        wobei η ein Normalisierungsfaktor ist.
        """
        new_belief = BeliefState()

        for s_prime in [s.id for s in pomdp.states]:
            # P(o|s',a)
            obs_prob = pomdp.observation_model.get((s_prime, action), {}).get(observation, 0.0)

            if obs_prob == 0:
                new_belief.set_probability(s_prime, 0.0)
                continue

            # Σ_s P(s'|s,a) b(s)
            transition_sum = 0.0
            for s in [st.id for st in pomdp.states]:
                trans_prob = pomdp.transition_model.get_probability(s, action, s_prime)
                belief_prob = belief.get_probability(s)
                transition_sum += trans_prob * belief_prob

            new_belief.set_probability(s_prime, obs_prob * transition_sum)

        new_belief.normalize()
        return new_belief

    def qmdp_action(self, pomdp: POMDP, belief: BeliefState,
                    q_values: ValueFunction) -> str:
        """
        QMDP Heuristik: Wähle Aktion basierend auf erwarteten Q-Werten.

        a* = argmax_a Σ_s b(s) Q*(s,a)

        Dies ist eine optimistische Heuristik, die annimmt, dass
        der Zustand nach einer Aktion vollständig beobachtbar wird.
        """
        actions = [a.id for a in pomdp.actions]
        best_action = actions[0]
        best_value = float('-inf')

        for a in actions:
            expected_q = 0.0
            for s in [st.id for st in pomdp.states]:
                q = q_values.Q(s, a)
                b = belief.get_probability(s)
                expected_q += b * q

            if expected_q > best_value:
                best_value = expected_q
                best_action = a

        return best_action

    def information_gathering_value(self, pomdp: POMDP,
                                     belief: BeliefState,
                                     action: str) -> float:
        """
        Schätzt den Wert der Informationsgewinnung einer Aktion.
        Berechnet die erwartete Entropie-Reduktion.
        """
        current_entropy = belief.entropy()

        expected_new_entropy = 0.0
        observations = [o.id for o in pomdp.observations]

        for obs in observations:
            # Berechne P(o|a,b)
            obs_prob = self._observation_probability(pomdp, belief, action, obs)

            if obs_prob > 0:
                new_belief = self.belief_update(pomdp, belief, action, obs)
                new_entropy = new_belief.entropy()
                expected_new_entropy += obs_prob * new_entropy

        # Information Gain = Entropie-Reduktion
        return current_entropy - expected_new_entropy

    def _observation_probability(self, pomdp: POMDP, belief: BeliefState,
                                  action: str, observation: str) -> float:
        """P(o|a,b) = Σ_{s'} P(o|s',a) Σ_s P(s'|s,a) b(s)"""
        prob = 0.0

        for s_prime in [s.id for s in pomdp.states]:
            obs_prob = pomdp.observation_model.get((s_prime, action), {}).get(observation, 0.0)

            trans_sum = 0.0
            for s in [st.id for st in pomdp.states]:
                trans_prob = pomdp.transition_model.get_probability(s, action, s_prime)
                trans_sum += trans_prob * belief.get_probability(s)

            prob += obs_prob * trans_sum

        return prob


# =============================================================================
# MODEL-BASED RL ENGINE
# =============================================================================

@dataclass
class WorldModel:
    """
    Gelerntes Weltmodell für model-based RL.
    """
    transition_counts: Dict[Tuple[str, str, str], int] = field(default_factory=dict)
    reward_sum: Dict[Tuple[str, str, str], float] = field(default_factory=dict)
    visit_counts: Dict[Tuple[str, str], int] = field(default_factory=dict)

    def update(self, state: str, action: str, next_state: str, reward: float):
        """Aktualisiert das Modell mit einer Erfahrung"""
        key = (state, action, next_state)
        sa_key = (state, action)

        self.transition_counts[key] = self.transition_counts.get(key, 0) + 1
        self.reward_sum[key] = self.reward_sum.get(key, 0.0) + reward
        self.visit_counts[sa_key] = self.visit_counts.get(sa_key, 0) + 1

    def get_transition_probability(self, state: str, action: str, next_state: str) -> float:
        """Geschätzte P(s'|s,a)"""
        key = (state, action, next_state)
        sa_key = (state, action)

        count = self.transition_counts.get(key, 0)
        total = self.visit_counts.get(sa_key, 0)

        return count / total if total > 0 else 0.0

    def get_expected_reward(self, state: str, action: str, next_state: str) -> float:
        """Geschätzte R(s,a,s')"""
        key = (state, action, next_state)
        count = self.transition_counts.get(key, 0)
        total_reward = self.reward_sum.get(key, 0.0)

        return total_reward / count if count > 0 else 0.0

    def sample_next_state(self, state: str, action: str) -> Optional[Tuple[str, float]]:
        """Sampelt einen Nachfolgezustand aus dem Modell"""
        sa_key = (state, action)
        if self.visit_counts.get(sa_key, 0) == 0:
            return None

        # Sammle alle möglichen Nachfolgezustände
        next_states = []
        probs = []

        for (s, a, s_prime), count in self.transition_counts.items():
            if s == state and a == action:
                prob = count / self.visit_counts[sa_key]
                next_states.append(s_prime)
                probs.append(prob)

        if not next_states:
            return None

        # Sample
        s_prime = random.choices(next_states, weights=probs)[0]
        reward = self.get_expected_reward(state, action, s_prime)

        return s_prime, reward


class DynaQAgent:
    """
    Dyna-Q Agent: Kombiniert Q-Learning mit Planung.

    1. Führe echte Erfahrung aus
    2. Update Q-Werte (Direct RL)
    3. Update Modell (Model Learning)
    4. Führe k simulierte Erfahrungen aus (Planning)
    """

    def __init__(self, actions: List[str], alpha: float = 0.1,
                 gamma: float = 0.95, epsilon: float = 0.1,
                 planning_steps: int = 5):
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.planning_steps = planning_steps

        self.Q = ValueFunction()
        self.model = WorldModel()
        self.visited_states: Set[str] = set()

    def get_action(self, state: str) -> str:
        """ε-greedy Aktionswahl"""
        if random.random() < self.epsilon:
            return random.choice(self.actions)

        best_action = self.actions[0]
        best_value = self.Q.Q(state, best_action)

        for a in self.actions[1:]:
            q = self.Q.Q(state, a)
            if q > best_value:
                best_value = q
                best_action = a

        return best_action

    def update(self, state: str, action: str, reward: float,
               next_state: str, is_terminal: bool = False):
        """
        Dyna-Q Update:
        1. Direct RL (Q-Learning)
        2. Model Update
        3. Planning (simulierte Erfahrungen)
        """
        self.visited_states.add(state)

        # 1. Direct RL - Q-Learning Update
        current_q = self.Q.Q(state, action)
        if is_terminal:
            max_next_q = 0.0
        else:
            max_next_q = max(self.Q.Q(next_state, a) for a in self.actions)

        td_error = reward + self.gamma * max_next_q - current_q
        self.Q.set_Q(state, action, current_q + self.alpha * td_error)

        # 2. Model Update
        self.model.update(state, action, next_state, reward)

        # 3. Planning - Simulierte Erfahrungen
        for _ in range(self.planning_steps):
            self._planning_step()

    def _planning_step(self):
        """Ein Planungsschritt mit dem gelernten Modell"""
        if not self.visited_states:
            return

        # Wähle zufälligen besuchten Zustand
        state = random.choice(list(self.visited_states))
        action = random.choice(self.actions)

        # Sample aus Modell
        result = self.model.sample_next_state(state, action)
        if result is None:
            return

        next_state, reward = result

        # Q-Learning Update mit simulierter Erfahrung
        current_q = self.Q.Q(state, action)
        max_next_q = max(self.Q.Q(next_state, a) for a in self.actions)
        td_error = reward + self.gamma * max_next_q - current_q
        self.Q.set_Q(state, action, current_q + self.alpha * td_error)


class ModelBasedEngine:
    """Engine für Model-based RL"""

    def __init__(self):
        logger.info("ModelBasedEngine initialisiert")

    def prioritized_sweeping(self, model: WorldModel, Q: ValueFunction,
                              actions: List[str], gamma: float = 0.95,
                              theta: float = 0.0001, max_updates: int = 100):
        """
        Prioritized Sweeping: Fokussiert Updates auf Zustände,
        deren Wert sich am meisten ändern würde.
        """
        # Priority Queue (vereinfacht als Dict)
        priorities: Dict[Tuple[str, str], float] = {}

        for _ in range(max_updates):
            if not priorities:
                break

            # Pop höchste Priorität
            (state, action), priority = max(priorities.items(), key=lambda x: x[1])
            del priorities[(state, action)]

            if priority < theta:
                continue

            # Update Q(s,a)
            # ... (implementiert analog zu Dyna-Q)

            # Finde Vorgängerzustände und aktualisiere deren Prioritäten
            # ... (benötigt Rückwärtsmodell)


# =============================================================================
# KOMBINIERTE ENGINE
# =============================================================================

class AdvancedMDPEngine:
    """Kombiniert alle MDP-Engines"""

    def __init__(self):
        self.bellman = BellmanEngine()
        self.td = TDLearningEngine()
        self.policy_gradient = PolicyGradientEngine()
        self.pomdp = POMDPEngine()
        self.model_based = ModelBasedEngine()

        logger.info("AdvancedMDPEngine initialisiert (alle Sub-Engines)")

    def get_wolf_wisdom(self) -> str:
        """Holos MDP-Weisheit"""
        wisdoms = [
            "Die Bellman-Gleichung ist wie der Leitstern des Rudels - sie zeigt den optimalen Pfad.",
            "TD-Learning ist wie ein junger Wolf: Er lernt aus jedem Schritt, nicht erst am Ziel.",
            "Policy Gradient ist die Kunst, direkt zu lernen, wie man jagt - nicht nur, wo die Beute ist.",
            "In einer unsicheren Welt (POMDP) muss man seine Überzeugungen stetig aktualisieren.",
            "Ein gutes Modell der Welt spart echte Erfahrungen - Planung ist die Weisheit des Alters.",
            "Der Discount-Faktor γ lehrt uns: Das Heute zählt, aber die Zukunft ist nicht bedeutungslos.",
        ]
        return random.choice(wisdoms)

    def create_grid_world_mdp(self, size: int = 4,
                               goal_state: str = "3,3",
                               obstacle_states: List[str] = None) -> MDP:
        """Erstellt ein Grid World MDP zum Testen"""
        states = []
        for i in range(size):
            for j in range(size):
                state_id = f"{i},{j}"
                is_terminal = state_id == goal_state
                states.append(MDPState(state_id, is_terminal=is_terminal))

        actions = [
            MDPAction("up"), MDPAction("down"),
            MDPAction("left"), MDPAction("right")
        ]

        transition_model = TransitionModel()
        reward_function = RewardFunction()

        # Deterministische Übergänge
        for i in range(size):
            for j in range(size):
                s = f"{i},{j}"

                # Up
                next_i = max(0, i - 1)
                next_s = f"{next_i},{j}"
                transition_model.set_transition(s, "up", next_s, 1.0)

                # Down
                next_i = min(size - 1, i + 1)
                next_s = f"{next_i},{j}"
                transition_model.set_transition(s, "down", next_s, 1.0)

                # Left
                next_j = max(0, j - 1)
                next_s = f"{i},{next_j}"
                transition_model.set_transition(s, "left", next_s, 1.0)

                # Right
                next_j = min(size - 1, j + 1)
                next_s = f"{i},{next_j}"
                transition_model.set_transition(s, "right", next_s, 1.0)

        # Belohnungen
        reward_function.state_rewards[goal_state] = 1.0
        if obstacle_states:
            for obs in obstacle_states:
                reward_function.state_rewards[obs] = -1.0

        return MDP(
            states=states,
            actions=actions,
            transition_model=transition_model,
            reward_function=reward_function,
            gamma=0.95,
            initial_state=states[0]
        )


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

_bellman_engine: Optional[BellmanEngine] = None
_td_engine: Optional[TDLearningEngine] = None
_pg_engine: Optional[PolicyGradientEngine] = None
_pomdp_engine: Optional[POMDPEngine] = None
_advanced_mdp_engine: Optional[AdvancedMDPEngine] = None


def create_bellman_engine() -> BellmanEngine:
    global _bellman_engine
    if _bellman_engine is None:
        _bellman_engine = BellmanEngine()
    return _bellman_engine


def create_td_learning_engine() -> TDLearningEngine:
    global _td_engine
    if _td_engine is None:
        _td_engine = TDLearningEngine()
    return _td_engine


def create_policy_gradient_engine() -> PolicyGradientEngine:
    global _pg_engine
    if _pg_engine is None:
        _pg_engine = PolicyGradientEngine()
    return _pg_engine


def create_pomdp_engine() -> POMDPEngine:
    global _pomdp_engine
    if _pomdp_engine is None:
        _pomdp_engine = POMDPEngine()
    return _pomdp_engine


def get_advanced_mdp_engine() -> AdvancedMDPEngine:
    global _advanced_mdp_engine
    if _advanced_mdp_engine is None:
        _advanced_mdp_engine = AdvancedMDPEngine()
    return _advanced_mdp_engine


# =============================================================================
# MAIN (TEST)
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 70)
    print("HOLO ADVANCED MDP v1.0 - Demo")
    print("=" * 70)

    engine = get_advanced_mdp_engine()

    # Erstelle Grid World
    print("\n--- GRID WORLD MDP ---")
    mdp = engine.create_grid_world_mdp(size=4, goal_state="3,3")
    print(f"Zustände: {len(mdp.states)}")
    print(f"Aktionen: {[a.id for a in mdp.actions]}")
    print(f"Discount γ: {mdp.gamma}")

    # Value Iteration
    print("\n--- VALUE ITERATION ---")
    V, policy = engine.bellman.value_iteration(mdp)
    print("Optimale Werte (Auswahl):")
    for s in ["0,0", "1,1", "2,2", "3,3"]:
        print(f"  V({s}) = {V.V(s):.3f}, π({s}) = {policy.get_action(s)}")

    # Policy Iteration
    print("\n--- POLICY ITERATION ---")
    V2, policy2 = engine.bellman.policy_iteration(mdp)
    print("Optimale Policy gleich?", all(
        policy.get_action(s) == policy2.get_action(s)
        for s in mdp.get_state_ids()
    ))

    # Q-Learning Agent
    print("\n--- Q-LEARNING ---")
    q_agent = QLearningAgent(
        actions=mdp.get_action_ids(),
        alpha=0.1, gamma=0.95, epsilon=0.1
    )

    for episode in range(500):
        state = "0,0"
        for _ in range(50):
            action = q_agent.get_action(state)
            next_states = mdp.transition_model.get_next_states(state, action)
            if not next_states:
                break
            next_state = random.choices(
                list(next_states.keys()),
                weights=list(next_states.values())
            )[0]
            reward = mdp.reward_function.get_reward(state, action, next_state)
            is_terminal = next_state == "3,3"
            q_agent.update(state, action, reward, next_state, is_terminal)
            if is_terminal:
                break
            state = next_state

    print("Gelernte Q-Werte (Auswahl):")
    for s in ["0,0", "1,1"]:
        for a in mdp.get_action_ids():
            print(f"  Q({s}, {a}) = {q_agent.Q.Q(s, a):.3f}")

    # Dyna-Q
    print("\n--- DYNA-Q ---")
    dyna_agent = DynaQAgent(
        actions=mdp.get_action_ids(),
        planning_steps=5
    )
    print(f"Dyna-Q mit {dyna_agent.planning_steps} Planungsschritten pro Update")

    # Actor-Critic
    print("\n--- ACTOR-CRITIC ---")
    ac_agent = ActorCriticAgent(
        states=mdp.get_state_ids(),
        actions=mdp.get_action_ids()
    )
    print("Actor-Critic Agent erstellt (Online-Updates)")

    # REINFORCE
    print("\n--- REINFORCE ---")
    reinforce = REINFORCEAgent(
        states=mdp.get_state_ids(),
        actions=mdp.get_action_ids()
    )
    print("REINFORCE Agent erstellt (Episodische Updates)")

    # GAE
    print("\n--- GENERALIZED ADVANTAGE ESTIMATION ---")
    gae = AdvantageEstimator(gamma=0.95, lambda_=0.95)
    test_rewards = [0, 0, 0, 1]
    test_values = [0.5, 0.6, 0.8, 0.9]
    advantages = gae.estimate(test_rewards, test_values, 0.0)
    print(f"Rewards: {test_rewards}")
    print(f"Values: {test_values}")
    print(f"Advantages: {[f'{a:.3f}' for a in advantages]}")

    # POMDP
    print("\n--- POMDP (Belief Update) ---")
    belief = BeliefState(distribution={"A": 0.5, "B": 0.5})
    print(f"Initiales Belief: {belief.distribution}")
    print(f"Entropie: {belief.entropy():.3f}")
    print(f"Wahrscheinlichster Zustand: {belief.most_likely_state()}")

    # Weisheit
    print("\n--- MDP WEISHEIT ---")
    print(f"*richtet Ohren auf* {engine.get_wolf_wisdom()}")

    print("\n" + "=" * 70)
    print("Demo abgeschlossen!")
