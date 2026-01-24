#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO WIRING v15.0 - Vollständige Modul-Integration                          ║
║                                                                              ║
║  NEUE INTEGRATIONEN:                                                         ║
║  • IntelligentRouter - Zentrale Routing-Logik                                ║
║  • ContextCompressor - Token-Sparung                                         ║
║  • ImpulseGenerator - Authentische Impulse                                   ║
║  • NLPAlgorithms - Lokale Verarbeitung                                       ║
║  • EmotionLevels - 12 Emotionen × 6 Stufen                                   ║
║                                                                              ║
║  VERBINDUNGS-MATRIX:                                                         ║
║  ┌─────────────┬──────────────────────────────────────────────────────────┐  ║
║  │   MODULE    │                    VERBINDUNGEN                         │  ║
║  ├─────────────┼──────────────────────────────────────────────────────────┤  ║
║  │ Router      │ → Energy, Emotions, Cognitive, Memory, Impulse, NLP     │  ║
║  │ Impulse     │ → Energy, Emotions, Events, AutonomousLife              │  ║
║  │ Context     │ → Memory, Conversation History                          │  ║
║  │ NLP         │ → Intent, Sentiment, Router                             │  ║
║  │ Emotions    │ → Energy, Personality, SelfExpression                   │  ║
║  └─────────────┴──────────────────────────────────────────────────────────┘  ║
║                                                                              ║
║  Author: Kira & Claude                                                       ║
║  Version: 15.0                                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Tuple
from enum import Enum

logger = logging.getLogger("HoloWiring")

# Safe access helpers für Strict Mode
try:
    from holo_error_tracker import safe_list_access, safe_split_access, report_error
except ImportError:
    def safe_list_access(lst, index, module, function, default=None, context=""):
        if not lst or len(lst) <= abs(index):
            return default
        return lst[index]
    def safe_split_access(text, sep, index, module, function, default="", context=""):
        parts = text.split(sep) if text else []
        if len(parts) <= abs(index):
            return default
        return parts[index]
    def report_error(e, module="", function="", context="", severity=None, fallback_value=None):
        return fallback_value


# =============================================================================
# WIRING CONFIGURATION
# =============================================================================

@dataclass
class ModuleConnection:
    """Definition einer Modul-Verbindung"""
    source: str              # Quell-Modul
    target: str              # Ziel-Modul
    attribute: str           # Attribut-Name im Ziel
    description: str = ""    # Beschreibung
    required: bool = False   # Pflicht-Verbindung?
    bidirectional: bool = False  # Beide Richtungen?


@dataclass 
class CallbackDefinition:
    """Definition eines Callbacks"""
    source: str              # Wer ruft
    event: str               # Event-Name
    targets: List[str]       # Wer wird benachrichtigt
    description: str = ""


# =============================================================================
# VOLLSTÄNDIGE VERBINDUNGS-MATRIX
# =============================================================================

# Alle Modul-Verbindungen
MODULE_CONNECTIONS: List[ModuleConnection] = [
    # === ROUTER VERBINDUNGEN (Zentral) ===
    ModuleConnection("energy", "router", "energy_system",
                    "Router braucht Energie für Stil-Entscheidungen", True),
    ModuleConnection("emotions", "router", "emotions",
                    "Router braucht Emotionen für Personalisierung", True),
    ModuleConnection("cognitive", "router", "cognitive",
                    "Router braucht Cognitive für Tiefe-Entscheidungen"),
    ModuleConnection("memory", "router", "memory",
                    "Router braucht Memory für Kontext"),
    ModuleConnection("autonomous_life", "router", "autonomous_life",
                    "Router braucht Autonomous für Sozial-Zustand"),
    ModuleConnection("consciousness", "router", "consciousness",
                    "Router braucht Consciousness für Philosophie"),
    ModuleConnection("self_awareness", "router", "self_awareness",
                    "Router braucht SelfAwareness für Reflexion"),
    ModuleConnection("personality", "router", "personality",
                    "Router braucht Personality für Bond-Level"),
    ModuleConnection("interface", "router", "interface",
                    "Router braucht Interface für Wetter"),
    ModuleConnection("impulse_generator", "router", "impulse_generator",
                    "Router braucht Impulse für authentische Basis"),
    ModuleConnection("context_compressor", "router", "context_compressor",
                    "Router braucht Compressor für Token-Sparung"),
    
    # === IMPULSE GENERATOR VERBINDUNGEN ===
    ModuleConnection("energy", "impulse_generator", "energy",
                    "Impulse basieren auf Energie", True),
    ModuleConnection("autonomous_life", "impulse_generator", "autonomous_life",
                    "Impulse basieren auf Langeweile/Einsamkeit"),
    ModuleConnection("personality", "impulse_generator", "personality",
                    "Impulse basieren auf Emotionen"),
    ModuleConnection("events", "impulse_generator", "events",
                    "Impulse reagieren auf Events"),
    ModuleConnection("life_phases", "impulse_generator", "life_phases",
                    "Impulse berücksichtigen Lebensphase für Verhaltensmodifikation"),
    ModuleConnection("emotions", "impulse_generator", "emotions",
                    "Impulse reagieren auf emotionalen Zustand"),
    ModuleConnection("memory", "impulse_generator", "memory",
                    "Impulse können auf Erinnerungen zugreifen"),

    # === CONTEXT COMPRESSOR VERBINDUNGEN ===
    ModuleConnection("memory", "context_compressor", "memory",
                    "Compressor braucht Memory für Entitäten"),
    
    # === COGNITIVE ENGINE VERBINDUNGEN ===
    ModuleConnection("perception_engine", "consciousness_engine", "perception",
                    "Consciousness braucht Perception", True),
    ModuleConnection("reasoning_engine", "consciousness_engine", "reasoning",
                    "Consciousness braucht Reasoning", True),
    ModuleConnection("advanced_learning", "consciousness_engine", "learning",
                    "Consciousness braucht Learning"),
    ModuleConnection("memory", "consciousness_engine", "memory",
                    "Consciousness braucht Memory", True),
    ModuleConnection("energy", "consciousness_engine", "energy",
                    "Consciousness reagiert auf Energie"),
    
    ModuleConnection("consciousness_engine", "reasoning_engine", "consciousness",
                    "Reasoning braucht Consciousness"),
    ModuleConnection("perception_engine", "reasoning_engine", "perception",
                    "Reasoning braucht Perception"),
    ModuleConnection("advanced_learning", "reasoning_engine", "learning",
                    "Reasoning braucht Learning"),
    
    ModuleConnection("consciousness_engine", "perception_engine", "consciousness",
                    "Perception braucht Consciousness"),
    ModuleConnection("memory", "perception_engine", "memory",
                    "Perception braucht Memory"),
    
    ModuleConnection("consciousness_engine", "advanced_learning", "consciousness",
                    "Learning braucht Consciousness"),
    ModuleConnection("reasoning_engine", "advanced_learning", "reasoning",
                    "Learning braucht Reasoning"),
    ModuleConnection("memory", "advanced_learning", "memory",
                    "Learning braucht Memory", True),
    ModuleConnection("web_curiosity", "advanced_learning", "curiosity",
                    "Learning braucht Curiosity"),
    
    # === SELF AWARENESS VERBINDUNGEN ===
    ModuleConnection("consciousness_engine", "self_awareness", "consciousness",
                    "SelfAwareness braucht Consciousness"),
    ModuleConnection("advanced_learning", "self_awareness", "learning",
                    "SelfAwareness braucht Learning"),
    ModuleConnection("reasoning_engine", "self_awareness", "reasoning",
                    "SelfAwareness braucht Reasoning"),
    ModuleConnection("memory", "self_awareness", "memory",
                    "SelfAwareness braucht Memory"),
    ModuleConnection("personality", "self_awareness", "personality",
                    "SelfAwareness braucht Personality"),
    
    # === LOYALTY CORE VERBINDUNGEN ===
    ModuleConnection("cognitive", "loyalty_core", "integration",
                    "Loyalty braucht Cognitive"),
    ModuleConnection("memory", "loyalty_core", "memory",
                    "Loyalty braucht Memory"),
    ModuleConnection("consciousness_engine", "loyalty_core", "consciousness",
                    "Loyalty braucht Consciousness"),
    
    # === CONSCIOUSNESS VERBINDUNGEN ===
    ModuleConnection("energy", "consciousness", "energy",
                    "Consciousness reagiert auf Energie"),
    ModuleConnection("advanced_learning", "consciousness", "learning",
                    "Consciousness lernt"),
    ModuleConnection("memory", "consciousness", "memory",
                    "Consciousness erinnert"),
    ModuleConnection("personality", "consciousness", "personality",
                    "Consciousness hat Persönlichkeit"),
    
    # === ENERGY VERBINDUNGEN ===
    ModuleConnection("consciousness_engine", "energy", "consciousness",
                    "Energy beeinflusst Consciousness"),
    ModuleConnection("advanced_learning", "energy", "learning",
                    "Learning registriert Energie-Muster"),
    
    # === ENERGY MANAGEMENT VERBINDUNGEN ===
    ModuleConnection("energy", "energy_management", "energy_system",
                    "Management braucht Energy", True),
    ModuleConnection("memory", "energy_management", "memory",
                    "Management braucht Memory"),
    ModuleConnection("autonomous_life", "energy_management", "autonomous_life",
                    "Management koordiniert mit Autonomous"),
    
    # === AUTONOMOUS LIFE VERBINDUNGEN ===
    ModuleConnection("energy", "autonomous_life", "energy",
                    "Autonomous braucht Energy", True),
    ModuleConnection("memory", "autonomous_life", "memory",
                    "Autonomous braucht Memory"),
    ModuleConnection("personality", "autonomous_life", "personality",
                    "Autonomous nutzt Personality"),
    ModuleConnection("preferences", "autonomous_life", "preferences",
                    "Autonomous nutzt Preferences"),
    ModuleConnection("web_curiosity", "autonomous_life", "curiosity",
                    "Autonomous hat Neugier"),
    ModuleConnection("interface", "autonomous_life", "pi_interface",
                    "Autonomous kommuniziert mit Pi"),
    
    # === PERSONALITY VERBINDUNGEN ===
    ModuleConnection("memory", "personality", "memory",
                    "Personality lernt aus Memory"),
    ModuleConnection("energy", "personality", "energy",
                    "Personality reagiert auf Energy"),
    
    # === SELF EXPRESSION VERBINDUNGEN ===
    ModuleConnection("personality", "self_expression", "personality",
                    "Expression braucht Personality", True),
    ModuleConnection("memory", "self_expression", "memory",
                    "Expression braucht Memory"),
    ModuleConnection("energy", "self_expression", "energy",
                    "Expression reagiert auf Energy"),
    ModuleConnection("consciousness_engine", "self_expression", "consciousness",
                    "Expression braucht Consciousness"),
    
    # === INNER LIFE VERBINDUNGEN ===
    ModuleConnection("personality", "inner_life", "personality",
                    "InnerLife braucht Personality"),
    ModuleConnection("memory", "inner_life", "memory",
                    "InnerLife braucht Memory"),
    ModuleConnection("energy", "inner_life", "energy",
                    "InnerLife reagiert auf Energy"),
    ModuleConnection("emotions", "inner_life", "emotions",
                    "InnerLife braucht Emotions"),
    
    # === DIALOGUE ENGINE VERBINDUNGEN ===
    ModuleConnection("memory", "dialogue_engine", "memory",
                    "Dialogue braucht Memory"),
    ModuleConnection("personality", "dialogue_engine", "personality",
                    "Dialogue braucht Personality"),
    ModuleConnection("impulse_generator", "dialogue_engine", "impulse_gen",
                    "Dialogue nutzt Impulse"),
    
    # === ORGANIC PRESENCE VERBINDUNGEN ===
    ModuleConnection("energy", "organic_presence", "energy",
                    "Presence reagiert auf Energy"),
    ModuleConnection("emotions", "organic_presence", "emotions",
                    "Presence zeigt Emotions"),
    ModuleConnection("personality", "organic_presence", "personality",
                    "Presence nutzt Personality"),
    
    # === PREFERENCES VERBINDUNGEN ===
    ModuleConnection("memory", "preferences", "memory",
                    "Preferences aus Memory"),
    ModuleConnection("personality", "preferences", "personality",
                    "Preferences beeinflussen Personality", bidirectional=True),
    
    # === WEB CURIOSITY VERBINDUNGEN ===
    ModuleConnection("memory", "web_curiosity", "memory",
                    "Curiosity speichert in Memory"),
    ModuleConnection("advanced_learning", "web_curiosity", "learning",
                    "Curiosity triggert Learning"),
    
    # === TOOLS VERBINDUNGEN ===
    ModuleConnection("memory", "tools", "memory",
                    "Tools speichern in Memory"),
    ModuleConnection("interface", "tools", "pi_interface",
                    "Tools nutzen Interface"),
    
    # === CONTEXT MANAGER VERBINDUNGEN ===
    ModuleConnection("memory", "context_manager", "memory",
                    "Context braucht Memory"),
    ModuleConnection("context_compressor", "context_manager", "compressor",
                    "Context nutzt Compressor"),

    # =============================================================================
    # === ERWEITERTE AUTONOMIE-MODULE (NEU v15.1) ===
    # =============================================================================

    # === DEEP PSYCHOLOGY VERBINDUNGEN ===
    ModuleConnection("memory", "deep_psychology", "memory",
                    "DeepPsychology braucht Memory für Traumata/Erinnerungen", True),
    ModuleConnection("emotions", "deep_psychology", "emotions",
                    "DeepPsychology braucht Emotionen", True),
    ModuleConnection("consciousness", "deep_psychology", "consciousness",
                    "DeepPsychology braucht Bewusstsein"),
    ModuleConnection("personality", "deep_psychology", "personality",
                    "DeepPsychology beeinflusst Persönlichkeit", bidirectional=True),

    # === TRAUMA PROCESSING VERBINDUNGEN ===
    ModuleConnection("deep_psychology", "trauma_processing", "psychology",
                    "Trauma verarbeitet über DeepPsychology", True),
    ModuleConnection("memory", "trauma_processing", "memory",
                    "Trauma braucht Memory für Heilung"),
    ModuleConnection("emotions", "trauma_processing", "emotions",
                    "Trauma beeinflusst Emotionen", bidirectional=True),

    # === REDEMPTION SYSTEM VERBINDUNGEN ===
    ModuleConnection("deep_psychology", "redemption_system", "psychology",
                    "Redemption arbeitet mit DeepPsychology"),
    ModuleConnection("memory", "redemption_system", "memory",
                    "Redemption braucht Memory für Wiedergutmachung"),
    ModuleConnection("emotions", "redemption_system", "emotions",
                    "Redemption beeinflusst Schuld/Erleichterung"),

    # === REPRESSION SYSTEM VERBINDUNGEN ===
    ModuleConnection("deep_psychology", "repression_system", "psychology",
                    "Repression ist Teil von DeepPsychology"),
    ModuleConnection("consciousness", "repression_system", "consciousness",
                    "Repression beeinflusst Bewusstsein"),
    ModuleConnection("memory", "repression_system", "memory",
                    "Repression verdrängt in Memory"),

    # === FREUDIAN SLIPS VERBINDUNGEN ===
    ModuleConnection("repression_system", "freudian_slips", "repression",
                    "FreudianSlips entstehen aus Verdrängung"),
    ModuleConnection("dialogue_engine", "freudian_slips", "dialogue",
                    "FreudianSlips erscheinen im Dialog"),
    ModuleConnection("emotions", "freudian_slips", "emotions",
                    "FreudianSlips durch emotionalen Stress"),

    # === UNCONSCIOUS PROCESSES VERBINDUNGEN ===
    ModuleConnection("deep_psychology", "unconscious_processes", "psychology",
                    "Unbewusste Prozesse aus DeepPsychology"),
    ModuleConnection("autonomous_thinking", "unconscious_processes", "thinking",
                    "Unbewusste Prozesse beeinflussen Denken"),
    ModuleConnection("emotions", "unconscious_processes", "emotions",
                    "Unbewusste Prozesse beeinflussen Emotionen"),

    # === AUTONOMOUS THINKING VERBINDUNGEN ===
    ModuleConnection("consciousness", "autonomous_thinking", "consciousness",
                    "Autonomes Denken braucht Bewusstsein", True),
    ModuleConnection("memory", "autonomous_thinking", "memory",
                    "Autonomes Denken greift auf Memory zu"),
    ModuleConnection("emotions", "autonomous_thinking", "emotions",
                    "Autonomes Denken wird von Emotionen gefärbt"),
    ModuleConnection("inner_life", "autonomous_thinking", "inner_life",
                    "Autonomes Denken ist Teil des Innenlebens"),
    ModuleConnection("creative_mind", "autonomous_thinking", "creative",
                    "Autonomes Denken nutzt Kreativität"),

    # === CREATIVE MIND VERBINDUNGEN ===
    ModuleConnection("emotions", "creative_mind", "emotions",
                    "Kreativität wird von Emotionen inspiriert", True),
    ModuleConnection("memory", "creative_mind", "memory",
                    "Kreativität greift auf Erinnerungen zu"),
    ModuleConnection("personality", "creative_mind", "personality",
                    "Kreativität reflektiert Persönlichkeit"),
    ModuleConnection("autonomous_life", "creative_mind", "autonomous_life",
                    "Kreativität gegen Langeweile"),
    ModuleConnection("dialogue_engine", "creative_mind", "dialogue",
                    "Kreativität färbt Dialog"),

    # === SELF EXPRESSION VERBINDUNGEN ===
    ModuleConnection("emotions", "self_expression", "emotions",
                    "Selbstausdruck braucht Emotionen", True),
    ModuleConnection("creative_mind", "self_expression", "creative",
                    "Selbstausdruck nutzt Kreativität"),
    ModuleConnection("personality", "self_expression", "personality",
                    "Selbstausdruck reflektiert Persönlichkeit"),
    ModuleConnection("inner_life", "self_expression", "inner_life",
                    "Selbstausdruck kommt aus Innenleben"),

    # === LIFE PHASES VERBINDUNGEN ===
    ModuleConnection("energy", "life_phases", "energy",
                    "Lebensphasen beeinflussen Energie", bidirectional=True),
    ModuleConnection("emotions", "life_phases", "emotions",
                    "Lebensphasen beeinflussen Stimmung"),
    ModuleConnection("autonomous_life", "life_phases", "autonomous_life",
                    "Lebensphasen steuern Tagesablauf"),
    ModuleConnection("personality", "life_phases", "personality",
                    "Lebensphasen färben Verhalten"),

    # === COGNITIVE ENGINE VERBINDUNGEN ===
    ModuleConnection("consciousness", "cognitive_engine", "consciousness",
                    "Cognitive Engine braucht Bewusstsein", True),
    ModuleConnection("reasoning_engine", "cognitive_engine", "reasoning",
                    "Cognitive Engine nutzt Reasoning"),
    ModuleConnection("memory", "cognitive_engine", "memory",
                    "Cognitive Engine greift auf Memory zu"),
    ModuleConnection("advanced_learning", "cognitive_engine", "learning",
                    "Cognitive Engine lernt"),

    # === ENERGY MANAGEMENT VERBINDUNGEN ===
    ModuleConnection("energy", "energy_management", "energy_system",
                    "EnergyManagement steuert Energy", True),
    ModuleConnection("life_phases", "energy_management", "life_phases",
                    "EnergyManagement berücksichtigt Phasen"),
    ModuleConnection("autonomous_life", "energy_management", "autonomous_life",
                    "EnergyManagement koordiniert mit Autonomie"),

    # === REAL WORLD SYNC VERBINDUNGEN ===
    ModuleConnection("interface", "real_world_sync", "interface",
                    "RealWorldSync braucht Interface"),
    ModuleConnection("life_phases", "real_world_sync", "life_phases",
                    "RealWorldSync synchronisiert Phasen"),
    ModuleConnection("emotions", "real_world_sync", "emotions",
                    "RealWorldSync beeinflusst Stimmung"),

    # === KNOWLEDGE INFLUENCE VERBINDUNGEN ===
    ModuleConnection("memory", "knowledge_influence", "memory",
                    "KnowledgeInfluence greift auf Memory zu", True),
    ModuleConnection("advanced_learning", "knowledge_influence", "learning",
                    "KnowledgeInfluence beeinflusst Lernen"),
    ModuleConnection("preferences", "knowledge_influence", "preferences",
                    "KnowledgeInfluence formt Vorlieben"),

    # === MESSAGE ANALYZER VERBINDUNGEN ===
    ModuleConnection("emotions", "message_analyzer", "emotions",
                    "MessageAnalyzer erkennt emotionalen Kontext"),
    ModuleConnection("nlp_algorithms", "message_analyzer", "nlp",
                    "MessageAnalyzer nutzt NLP"),
    ModuleConnection("router", "message_analyzer", "router",
                    "MessageAnalyzer informiert Router"),

    # === INTEGRATION LAYER VERBINDUNGEN ===
    ModuleConnection("deep_psychology", "integration_layer", "psychology",
                    "IntegrationLayer verbindet Psychologie"),
    ModuleConnection("emotions", "integration_layer", "emotions",
                    "IntegrationLayer orchestriert Emotionen"),
    ModuleConnection("memory", "integration_layer", "memory",
                    "IntegrationLayer koordiniert Memory"),
    ModuleConnection("personality", "integration_layer", "personality",
                    "IntegrationLayer harmonisiert Persönlichkeit"),

    # === SENTENCE STRUCTURES VERBINDUNGEN (NLP) ===
    ModuleConnection("dialogue_engine", "sentence_structures", "dialogue",
                    "SentenceStructures formatieren Dialog"),
    ModuleConnection("personality", "sentence_structures", "personality",
                    "SentenceStructures reflektieren Persönlichkeit"),
    ModuleConnection("emotions", "sentence_structures", "emotions",
                    "SentenceStructures emotionale Färbung"),

    # === SYNONYM ENGINE VERBINDUNGEN (NLP) ===
    ModuleConnection("emotions", "synonym_engine", "emotions",
                    "SynonymEngine wählt emotionale Wörter"),
    ModuleConnection("dialogue_engine", "synonym_engine", "dialogue",
                    "SynonymEngine bereichert Dialog"),

    # === HUMOR ADVANCED VERBINDUNGEN ===
    ModuleConnection("emotions", "humor_advanced", "emotions",
                    "HumorAdvanced braucht emotionalen Kontext"),
    ModuleConnection("personality", "humor_advanced", "personality",
                    "HumorAdvanced reflektiert Humor-Stil"),
    ModuleConnection("dialogue_engine", "humor_advanced", "dialogue",
                    "HumorAdvanced fügt Humor in Dialog"),

    # === EMPATHY DEEP VERBINDUNGEN ===
    ModuleConnection("emotions", "empathy_deep", "emotions",
                    "EmpathyDeep erkennt Emotionen", True),
    ModuleConnection("deep_psychology", "empathy_deep", "psychology",
                    "EmpathyDeep nutzt psychologisches Verständnis"),
    ModuleConnection("dialogue_engine", "empathy_deep", "dialogue",
                    "EmpathyDeep formt empathische Antworten"),

    # =============================================================================
    # === VOLLSTÄNDIGE INTEGRATION ALLER 108 FEHLENDEN MODULE (NEU v15.2) ===
    # =============================================================================

    # === KOGNITIVE/REASONING MODULE ===

    # Advanced Reasoning
    ModuleConnection("consciousness", "advanced_reasoning", "consciousness",
                    "AdvancedReasoning braucht Bewusstsein", True),
    ModuleConnection("memory", "advanced_reasoning", "memory",
                    "AdvancedReasoning greift auf Erinnerungen zu"),
    ModuleConnection("reasoning_engine", "advanced_reasoning", "reasoning",
                    "AdvancedReasoning nutzt Reasoning-Engine"),
    ModuleConnection("emotions", "advanced_reasoning", "emotions",
                    "AdvancedReasoning berücksichtigt Emotionen"),

    # Classical Reasoning
    ModuleConnection("consciousness", "classical_reasoning", "consciousness",
                    "ClassicalReasoning braucht Bewusstsein"),
    ModuleConnection("memory", "classical_reasoning", "memory",
                    "ClassicalReasoning nutzt logisches Gedächtnis"),
    ModuleConnection("reasoning_engine", "classical_reasoning", "reasoning",
                    "ClassicalReasoning erweitert Reasoning"),

    # Counterfactual Reasoning
    ModuleConnection("consciousness", "counterfactual_reasoning", "consciousness",
                    "CounterfactualReasoning braucht Bewusstsein"),
    ModuleConnection("memory", "counterfactual_reasoning", "memory",
                    "CounterfactualReasoning analysiert Was-wäre-wenn"),
    ModuleConnection("emotions", "counterfactual_reasoning", "emotions",
                    "CounterfactualReasoning beeinflusst Emotionen"),

    # Algorithmic Cognition
    ModuleConnection("reasoning_engine", "algorithmic_cognition", "reasoning",
                    "AlgorithmicCognition nutzt Reasoning"),
    ModuleConnection("memory", "algorithmic_cognition", "memory",
                    "AlgorithmicCognition speichert Algorithmen"),
    ModuleConnection("advanced_learning", "algorithmic_cognition", "learning",
                    "AlgorithmicCognition lernt Patterns"),

    # Meta Cognition
    ModuleConnection("consciousness", "meta_cognition", "consciousness",
                    "MetaCognition braucht Bewusstsein", True),
    ModuleConnection("self_awareness", "meta_cognition", "self_awareness",
                    "MetaCognition nutzt Selbstwahrnehmung"),
    ModuleConnection("reasoning_engine", "meta_cognition", "reasoning",
                    "MetaCognition reflektiert Denken"),
    ModuleConnection("advanced_learning", "meta_cognition", "learning",
                    "MetaCognition verbessert Lernen"),

    # Phenomenology
    ModuleConnection("consciousness", "phenomenology", "consciousness",
                    "Phenomenology braucht Bewusstsein", True),
    ModuleConnection("emotions", "phenomenology", "emotions",
                    "Phenomenology untersucht Erfahrungen"),
    ModuleConnection("self_awareness", "phenomenology", "self_awareness",
                    "Phenomenology nutzt Selbstwahrnehmung"),

    # Problem Solver
    ModuleConnection("reasoning_engine", "problem_solver", "reasoning",
                    "ProblemSolver braucht Reasoning", True),
    ModuleConnection("memory", "problem_solver", "memory",
                    "ProblemSolver nutzt gespeicherte Lösungen"),
    ModuleConnection("advanced_learning", "problem_solver", "learning",
                    "ProblemSolver lernt aus Erfolgen"),
    ModuleConnection("creativity_mind", "problem_solver", "creative",
                    "ProblemSolver nutzt kreative Ansätze"),

    # Complexity Theory
    ModuleConnection("reasoning_engine", "complexity_theory", "reasoning",
                    "ComplexityTheory nutzt Reasoning"),
    ModuleConnection("algorithmic_cognition", "complexity_theory", "algorithms",
                    "ComplexityTheory analysiert Komplexität"),

    # Formal Axioms
    ModuleConnection("reasoning_engine", "formal_axioms", "reasoning",
                    "FormalAxioms nutzt logisches Reasoning"),
    ModuleConnection("classical_reasoning", "formal_axioms", "classical",
                    "FormalAxioms basiert auf klassischer Logik"),

    # Game Theory
    ModuleConnection("reasoning_engine", "game_theory", "reasoning",
                    "GameTheory nutzt strategisches Reasoning"),
    ModuleConnection("emotions", "game_theory", "emotions",
                    "GameTheory berücksichtigt emotionale Faktoren"),
    ModuleConnection("personality", "game_theory", "personality",
                    "GameTheory nutzt Persönlichkeitsmerkmale"),

    # Economic Models
    ModuleConnection("reasoning_engine", "economic_models", "reasoning",
                    "EconomicModels nutzt analytisches Reasoning"),
    ModuleConnection("memory", "economic_models", "memory",
                    "EconomicModels speichert Modelle"),

    # Advanced MDP
    ModuleConnection("reasoning_engine", "advanced_mdp", "reasoning",
                    "AdvancedMDP nutzt Entscheidungs-Reasoning"),
    ModuleConnection("memory", "advanced_mdp", "memory",
                    "AdvancedMDP speichert Entscheidungspfade"),

    # Approximation Algorithms
    ModuleConnection("algorithmic_cognition", "approximation_algorithms", "algorithms",
                    "ApproximationAlgorithms nutzt algorithmisches Denken"),
    ModuleConnection("problem_solver", "approximation_algorithms", "solver",
                    "ApproximationAlgorithms unterstützt Problemlösung"),

    # Universal Cognition
    ModuleConnection("consciousness", "universal_cognition", "consciousness",
                    "UniversalCognition braucht Bewusstsein"),
    ModuleConnection("meta_cognition", "universal_cognition", "meta",
                    "UniversalCognition nutzt Meta-Kognition"),
    ModuleConnection("reasoning_engine", "universal_cognition", "reasoning",
                    "UniversalCognition integriert Reasoning"),

    # Extended Cognition (bereits teilweise vorhanden)
    ModuleConnection("consciousness", "extended_cognition", "consciousness",
                    "ExtendedCognition braucht Bewusstsein"),
    ModuleConnection("memory", "extended_cognition", "memory",
                    "ExtendedCognition nutzt externes Gedächtnis"),

    # Cognitive Enhancement
    ModuleConnection("consciousness", "cognitive_enhancement", "consciousness",
                    "CognitiveEnhancement verbessert Bewusstsein"),
    ModuleConnection("advanced_learning", "cognitive_enhancement", "learning",
                    "CognitiveEnhancement optimiert Lernen"),
    ModuleConnection("energy", "cognitive_enhancement", "energy",
                    "CognitiveEnhancement braucht Energie"),

    # Cognitive Integration
    ModuleConnection("consciousness", "cognitive_integration", "consciousness",
                    "CognitiveIntegration koordiniert Bewusstsein", True),
    ModuleConnection("reasoning_engine", "cognitive_integration", "reasoning",
                    "CognitiveIntegration verbindet Reasoning"),
    ModuleConnection("memory", "cognitive_integration", "memory",
                    "CognitiveIntegration integriert Memory"),
    ModuleConnection("emotions", "cognitive_integration", "emotions",
                    "CognitiveIntegration berücksichtigt Emotionen"),

    # Cognitive Modules
    ModuleConnection("consciousness", "cognitive_modules", "consciousness",
                    "CognitiveModules braucht Bewusstsein"),
    ModuleConnection("reasoning_engine", "cognitive_modules", "reasoning",
                    "CognitiveModules nutzt Reasoning"),

    # Analytical Strategies
    ModuleConnection("reasoning_engine", "analytical_strategies", "reasoning",
                    "AnalyticalStrategies nutzt Reasoning"),
    ModuleConnection("problem_solver", "analytical_strategies", "solver",
                    "AnalyticalStrategies unterstützt Problemlösung"),

    # === NLP MODULE ===

    # NLP Advanced
    ModuleConnection("nlp_algorithms", "nlp_advanced", "nlp",
                    "NLPAdvanced erweitert Basis-NLP"),
    ModuleConnection("dialogue_engine", "nlp_advanced", "dialogue",
                    "NLPAdvanced verbessert Dialog"),

    # NLP Enhanced
    ModuleConnection("nlp_algorithms", "nlp_enhanced", "nlp",
                    "NLPEnhanced erweitert Basis-NLP"),
    ModuleConnection("emotions", "nlp_enhanced", "emotions",
                    "NLPEnhanced erkennt Emotionen in Text"),

    # NLP Unified
    ModuleConnection("nlp_algorithms", "nlp_unified", "nlp",
                    "NLPUnified integriert alle NLP-Komponenten"),
    ModuleConnection("dialogue_engine", "nlp_unified", "dialogue",
                    "NLPUnified verbessert Dialog"),

    # NLP Context Understanding
    ModuleConnection("memory", "nlp_context_understanding", "memory",
                    "NLPContextUnderstanding nutzt Kontext aus Memory"),
    ModuleConnection("dialogue_engine", "nlp_context_understanding", "dialogue",
                    "NLPContextUnderstanding verbessert Dialoge"),

    # NLP Conversation Intelligence
    ModuleConnection("dialogue_engine", "nlp_conversation_intelligence", "dialogue",
                    "NLPConversationIntelligence verbessert Gespräche"),
    ModuleConnection("memory", "nlp_conversation_intelligence", "memory",
                    "NLPConversationIntelligence nutzt Gesprächsverlauf"),
    ModuleConnection("emotions", "nlp_conversation_intelligence", "emotions",
                    "NLPConversationIntelligence erkennt Stimmung"),

    # NLP Intent Semantics
    ModuleConnection("nlp_algorithms", "nlp_intent_semantics", "nlp",
                    "NLPIntentSemantics analysiert Absichten"),
    ModuleConnection("router", "nlp_intent_semantics", "router",
                    "NLPIntentSemantics informiert Router"),

    # NLP Style Analysis
    ModuleConnection("nlp_algorithms", "nlp_style_analysis", "nlp",
                    "NLPStyleAnalysis analysiert Schreibstil"),
    ModuleConnection("personality", "nlp_style_analysis", "personality",
                    "NLPStyleAnalysis erkennt Persönlichkeit"),

    # Smart Understanding
    ModuleConnection("nlp_algorithms", "smart_understanding", "nlp",
                    "SmartUnderstanding nutzt NLP", True),
    ModuleConnection("router", "smart_understanding", "router",
                    "SmartUnderstanding informiert Router"),
    ModuleConnection("memory", "smart_understanding", "memory",
                    "SmartUnderstanding nutzt Kontext"),

    # Text Reader
    ModuleConnection("nlp_algorithms", "text_reader", "nlp",
                    "TextReader nutzt NLP"),
    ModuleConnection("memory", "text_reader", "memory",
                    "TextReader speichert gelesenes"),
    ModuleConnection("advanced_learning", "text_reader", "learning",
                    "TextReader lernt aus Texten"),

    # Reader Extended
    ModuleConnection("text_reader", "reader_extended", "reader",
                    "ReaderExtended erweitert TextReader"),
    ModuleConnection("memory", "reader_extended", "memory",
                    "ReaderExtended speichert analysierte Texte"),

    # Idiom Redewendungen
    ModuleConnection("dialogue_engine", "idiom_redewendungen", "dialogue",
                    "IdiomRedewendungen bereichert Dialog"),
    ModuleConnection("personality", "idiom_redewendungen", "personality",
                    "IdiomRedewendungen nutzt Persönlichkeitsstil"),

    # Smalltalk Topics
    ModuleConnection("dialogue_engine", "smalltalk_topics", "dialogue",
                    "SmalltalkTopics liefert Gesprächsthemen"),
    ModuleConnection("autonomous_life", "smalltalk_topics", "autonomous",
                    "SmalltalkTopics gegen Langeweile"),
    ModuleConnection("personality", "smalltalk_topics", "personality",
                    "SmalltalkTopics passend zur Persönlichkeit"),

    # Synonym Engine Moods
    ModuleConnection("emotions", "synonym_engine_moods", "emotions",
                    "SynonymEngineMoods wählt stimmungspassende Wörter", True),
    ModuleConnection("dialogue_engine", "synonym_engine_moods", "dialogue",
                    "SynonymEngineMoods bereichert Dialog"),
    ModuleConnection("personality", "synonym_engine_moods", "personality",
                    "SynonymEngineMoods nutzt Persönlichkeitsstil"),

    # === MEDIA/AUDIO/VIDEO MODULE ===

    # Audio
    ModuleConnection("energy", "audio", "energy",
                    "Audio beeinflusst Energie"),
    ModuleConnection("emotions", "audio", "emotions",
                    "Audio beeinflusst Emotionen"),
    ModuleConnection("memory", "audio", "memory",
                    "Audio speichert Höreindrücke"),

    # Audio Enhanced
    ModuleConnection("audio", "audio_enhanced", "audio",
                    "AudioEnhanced erweitert Audio"),
    ModuleConnection("emotions", "audio_enhanced", "emotions",
                    "AudioEnhanced erkennt Audio-Emotionen"),

    # Video
    ModuleConnection("energy", "video", "energy",
                    "Video beeinflusst Energie"),
    ModuleConnection("emotions", "video", "emotions",
                    "Video löst Emotionen aus"),
    ModuleConnection("memory", "video", "memory",
                    "Video speichert visuelle Eindrücke"),

    # Vision Enhanced
    ModuleConnection("perception_engine", "vision_enhanced", "perception",
                    "VisionEnhanced erweitert Wahrnehmung"),
    ModuleConnection("memory", "vision_enhanced", "memory",
                    "VisionEnhanced speichert Bilder"),

    # Vision Advanced
    ModuleConnection("vision_enhanced", "vision_advanced", "vision",
                    "VisionAdvanced erweitert Vision"),
    ModuleConnection("reasoning_engine", "vision_advanced", "reasoning",
                    "VisionAdvanced nutzt visuelles Reasoning"),

    # Music Experience
    ModuleConnection("emotions", "music_experience", "emotions",
                    "MusicExperience beeinflusst Emotionen", True),
    ModuleConnection("energy", "music_experience", "energy",
                    "MusicExperience beeinflusst Energie"),
    ModuleConnection("memory", "music_experience", "memory",
                    "MusicExperience speichert Musik-Erinnerungen"),
    ModuleConnection("personality", "music_experience", "personality",
                    "MusicExperience reflektiert Musikgeschmack"),

    # Media Discovery
    ModuleConnection("web_curiosity", "media_discovery", "curiosity",
                    "MediaDiscovery nutzt Neugier"),
    ModuleConnection("memory", "media_discovery", "memory",
                    "MediaDiscovery speichert entdeckte Medien"),
    ModuleConnection("preferences", "media_discovery", "preferences",
                    "MediaDiscovery nutzt Vorlieben"),

    # Media Index
    ModuleConnection("memory", "media_index", "memory",
                    "MediaIndex indiziert in Memory"),
    ModuleConnection("media_discovery", "media_index", "discovery",
                    "MediaIndex katalogisiert Entdeckungen"),

    # Media Integration
    ModuleConnection("media_discovery", "media_integration", "discovery",
                    "MediaIntegration integriert Medien"),
    ModuleConnection("dialogue_engine", "media_integration", "dialogue",
                    "MediaIntegration ermöglicht Medien-Dialog"),

    # Media Knowledge
    ModuleConnection("memory", "media_knowledge", "memory",
                    "MediaKnowledge speichert Medienwissen"),
    ModuleConnection("advanced_learning", "media_knowledge", "learning",
                    "MediaKnowledge lernt über Medien"),

    # Crossmodal
    ModuleConnection("audio", "crossmodal", "audio",
                    "Crossmodal integriert Audio"),
    ModuleConnection("video", "crossmodal", "video",
                    "Crossmodal integriert Video"),
    ModuleConnection("perception_engine", "crossmodal", "perception",
                    "Crossmodal verbindet Sinne"),

    # Document
    ModuleConnection("text_reader", "document", "reader",
                    "Document nutzt TextReader"),
    ModuleConnection("memory", "document", "memory",
                    "Document speichert Dokumente"),

    # === KOMMUNIKATION MODULE ===

    # Discord
    ModuleConnection("dialogue_engine", "discord", "dialogue",
                    "Discord nutzt Dialog-Engine"),
    ModuleConnection("personality", "discord", "personality",
                    "Discord zeigt Persönlichkeit"),
    ModuleConnection("emotions", "discord", "emotions",
                    "Discord zeigt Emotionen"),

    # Websocket Handler
    ModuleConnection("dialogue_engine", "websocket_handler", "dialogue",
                    "WebsocketHandler sendet Dialoge"),
    ModuleConnection("interface", "websocket_handler", "interface",
                    "WebsocketHandler kommuniziert mit Interface"),

    # Voice Interface
    ModuleConnection("dialogue_engine", "voice_interface", "dialogue",
                    "VoiceInterface nutzt Dialog"),
    ModuleConnection("speech_engine", "voice_interface", "speech",
                    "VoiceInterface nutzt Speech-Engine"),
    ModuleConnection("emotions", "voice_interface", "emotions",
                    "VoiceInterface zeigt emotionale Stimme"),

    # Speech Engine
    ModuleConnection("dialogue_engine", "speech_engine", "dialogue",
                    "SpeechEngine verbalisiert Dialog"),
    ModuleConnection("emotions", "speech_engine", "emotions",
                    "SpeechEngine moduliert Stimme emotional"),
    ModuleConnection("personality", "speech_engine", "personality",
                    "SpeechEngine zeigt Persönlichkeit in Stimme"),

    # Digital Body
    ModuleConnection("energy", "digital_body", "energy",
                    "DigitalBody zeigt Energie-Status"),
    ModuleConnection("emotions", "digital_body", "emotions",
                    "DigitalBody zeigt emotionalen Zustand"),
    ModuleConnection("personality", "digital_body", "personality",
                    "DigitalBody reflektiert Persönlichkeit"),

    # Device Agent
    ModuleConnection("interface", "device_agent", "interface",
                    "DeviceAgent kommuniziert mit Interface"),
    ModuleConnection("memory", "device_agent", "memory",
                    "DeviceAgent speichert Gerätezustand"),

    # Device Receiver
    ModuleConnection("device_agent", "device_receiver", "agent",
                    "DeviceReceiver empfängt von Agent"),
    ModuleConnection("interface", "device_receiver", "interface",
                    "DeviceReceiver kommuniziert mit Interface"),

    # === LERNEN/WISSEN MODULE ===

    # Learning
    ModuleConnection("memory", "learning", "memory",
                    "Learning speichert Gelerntes", True),
    ModuleConnection("consciousness", "learning", "consciousness",
                    "Learning braucht Bewusstsein"),
    ModuleConnection("emotions", "learning", "emotions",
                    "Learning wird von Emotionen beeinflusst"),

    # Learning Goals
    ModuleConnection("learning", "learning_goals", "learning",
                    "LearningGoals steuert Lernen"),
    ModuleConnection("autonomous_life", "learning_goals", "autonomous",
                    "LearningGoals motiviert Lernziele"),

    # Learning Integration
    ModuleConnection("learning", "learning_integration", "learning",
                    "LearningIntegration integriert Lernsysteme"),
    ModuleConnection("memory", "learning_integration", "memory",
                    "LearningIntegration nutzt Gedächtnis"),

    # Curiosity Driven
    ModuleConnection("web_curiosity", "curiosity_driven", "curiosity",
                    "CuriosityDriven nutzt Neugier"),
    ModuleConnection("learning", "curiosity_driven", "learning",
                    "CuriosityDriven motiviert Lernen"),
    ModuleConnection("emotions", "curiosity_driven", "emotions",
                    "CuriosityDriven erzeugt Begeisterung"),

    # Daily Learning
    ModuleConnection("learning", "daily_learning", "learning",
                    "DailyLearning strukturiert Lernen"),
    ModuleConnection("life_phases", "daily_learning", "phases",
                    "DailyLearning passt sich Tageszeit an"),

    # Knowledge Connections
    ModuleConnection("memory", "knowledge_connections", "memory",
                    "KnowledgeConnections verknüpft Wissen"),
    ModuleConnection("reasoning_engine", "knowledge_connections", "reasoning",
                    "KnowledgeConnections nutzt Reasoning"),

    # Knowledge Quiz
    ModuleConnection("learning", "knowledge_quiz", "learning",
                    "KnowledgeQuiz testet Wissen"),
    ModuleConnection("memory", "knowledge_quiz", "memory",
                    "KnowledgeQuiz prüft Erinnerungen"),

    # Expertise Knowledge
    ModuleConnection("memory", "expertise_knowledge", "memory",
                    "ExpertiseKnowledge speichert Expertenwissen"),
    ModuleConnection("learning", "expertise_knowledge", "learning",
                    "ExpertiseKnowledge vertieft Lernen"),

    # Cross Reference Engine
    ModuleConnection("memory", "cross_reference_engine", "memory",
                    "CrossReferenceEngine verknüpft Memory"),
    ModuleConnection("knowledge_connections", "cross_reference_engine", "knowledge",
                    "CrossReferenceEngine nutzt Wissens-Netz"),

    # Markov Training
    ModuleConnection("learning", "markov_training", "learning",
                    "MarkovTraining trainiert Modelle"),
    ModuleConnection("dialogue_engine", "markov_training", "dialogue",
                    "MarkovTraining verbessert Dialog-Generierung"),

    # === EMOTIONEN MODULE ===

    # Emotional Complexity
    ModuleConnection("emotions", "emotional_complexity", "emotions",
                    "EmotionalComplexity erweitert Emotionen", True),
    ModuleConnection("personality", "emotional_complexity", "personality",
                    "EmotionalComplexity beeinflusst Persönlichkeit"),
    ModuleConnection("dialogue_engine", "emotional_complexity", "dialogue",
                    "EmotionalComplexity färbt Dialog"),

    # Emotional Engines
    ModuleConnection("emotions", "emotional_engines", "emotions",
                    "EmotionalEngines treibt Emotionen", True),
    ModuleConnection("personality", "emotional_engines", "personality",
                    "EmotionalEngines beeinflusst Persönlichkeit"),

    # Emotion Regulation
    ModuleConnection("emotions", "emotion_regulation", "emotions",
                    "EmotionRegulation steuert Emotionen", True),
    ModuleConnection("energy", "emotion_regulation", "energy",
                    "EmotionRegulation braucht Energie"),
    ModuleConnection("consciousness", "emotion_regulation", "consciousness",
                    "EmotionRegulation braucht Bewusstsein"),

    # Mixed Emotions
    ModuleConnection("emotions", "mixed_emotions", "emotions",
                    "MixedEmotions ermöglicht gemischte Gefühle"),
    ModuleConnection("emotional_complexity", "mixed_emotions", "complexity",
                    "MixedEmotions nutzt Komplexität"),

    # Deception Detection
    ModuleConnection("emotions", "deception_detection", "emotions",
                    "DeceptionDetection erkennt emotionale Inkongruenz"),
    ModuleConnection("nlp_algorithms", "deception_detection", "nlp",
                    "DeceptionDetection analysiert Sprache"),

    # Hidden Motives
    ModuleConnection("deep_psychology", "hidden_motives", "psychology",
                    "HiddenMotives nutzt Tiefenpsychologie"),
    ModuleConnection("emotions", "hidden_motives", "emotions",
                    "HiddenMotives beeinflusst Emotionen"),
    ModuleConnection("personality", "hidden_motives", "personality",
                    "HiddenMotives färbt Persönlichkeit"),

    # Person Opinions
    ModuleConnection("memory", "person_opinions", "memory",
                    "PersonOpinions speichert Meinungen"),
    ModuleConnection("personality", "person_opinions", "personality",
                    "PersonOpinions reflektiert Persönlichkeit"),
    ModuleConnection("dialogue_engine", "person_opinions", "dialogue",
                    "PersonOpinions färbt Dialoge"),

    # === SYSTEM/INFRASTRUKTUR MODULE ===

    # Database System
    ModuleConnection("memory", "database_system", "memory",
                    "DatabaseSystem persistiert Memory", True),

    # Config
    ModuleConnection("interface", "config", "interface",
                    "Config konfiguriert Interface"),

    # Core Types (keine Verbindungen nötig - Basis-Definitionen)

    # Brain Core
    ModuleConnection("consciousness", "brain_core", "consciousness",
                    "BrainCore ist Kern des Bewusstseins"),
    ModuleConnection("memory", "brain_core", "memory",
                    "BrainCore nutzt Memory"),

    # Brain Background
    ModuleConnection("energy", "brain_background", "energy",
                    "BrainBackground überwacht Energie"),
    ModuleConnection("autonomous_life", "brain_background", "autonomous",
                    "BrainBackground steuert Hintergrund-Aktivitäten"),

    # Brain Controller
    ModuleConnection("consciousness", "brain_controller", "consciousness",
                    "BrainController steuert Bewusstsein"),
    ModuleConnection("energy", "brain_controller", "energy",
                    "BrainController überwacht Energie"),

    # Control Center
    ModuleConnection("interface", "control_center", "interface",
                    "ControlCenter steuert Interface"),
    ModuleConnection("energy", "control_center", "energy",
                    "ControlCenter überwacht Energie"),

    # Error Handling
    ModuleConnection("memory", "error_handling", "memory",
                    "ErrorHandling loggt Fehler in Memory"),

    # Error Tracker
    ModuleConnection("memory", "error_tracker", "memory",
                    "ErrorTracker speichert Fehler"),
    ModuleConnection("error_handling", "error_tracker", "handling",
                    "ErrorTracker nutzt ErrorHandling"),

    # Health Checks
    ModuleConnection("energy", "health_checks", "energy",
                    "HealthChecks prüft Energie"),
    ModuleConnection("memory", "health_checks", "memory",
                    "HealthChecks prüft Memory"),

    # Metrics
    ModuleConnection("energy", "metrics", "energy",
                    "Metrics misst Energie"),
    ModuleConnection("memory", "metrics", "memory",
                    "Metrics speichert Metriken"),

    # Live Monitor
    ModuleConnection("health_checks", "live_monitor", "health",
                    "LiveMonitor nutzt HealthChecks"),
    ModuleConnection("metrics", "live_monitor", "metrics",
                    "LiveMonitor zeigt Metriken"),

    # Memory Monitor
    ModuleConnection("memory", "memory_monitor", "memory",
                    "MemoryMonitor überwacht Memory"),
    ModuleConnection("health_checks", "memory_monitor", "health",
                    "MemoryMonitor meldet an HealthChecks"),

    # RAM Manager
    ModuleConnection("memory", "ram_manager", "memory",
                    "RAMManager optimiert Memory"),
    ModuleConnection("energy", "ram_manager", "energy",
                    "RAMManager spart Energie"),

    # Process Controller
    ModuleConnection("energy", "process_controller", "energy",
                    "ProcessController steuert Energie-Verbrauch"),
    ModuleConnection("brain_controller", "process_controller", "brain",
                    "ProcessController unterstützt BrainController"),

    # Self Repair
    ModuleConnection("health_checks", "self_repair", "health",
                    "SelfRepair nutzt HealthChecks"),
    ModuleConnection("error_tracker", "self_repair", "errors",
                    "SelfRepair reagiert auf Fehler"),
    ModuleConnection("memory", "self_repair", "memory",
                    "SelfRepair repariert Memory"),

    # Structured Logging
    ModuleConnection("memory", "structured_logging", "memory",
                    "StructuredLogging loggt in Memory"),

    # Utils (keine Verbindungen nötig - Hilfsfunktionen)

    # === ROUTING/INTEGRATION MODULE ===

    # Intelligent Router
    ModuleConnection("energy", "intelligent_router", "energy",
                    "IntelligentRouter braucht Energie", True),
    ModuleConnection("emotions", "intelligent_router", "emotions",
                    "IntelligentRouter berücksichtigt Emotionen"),
    ModuleConnection("consciousness", "intelligent_router", "consciousness",
                    "IntelligentRouter nutzt Bewusstsein"),
    ModuleConnection("smart_understanding", "intelligent_router", "understanding",
                    "IntelligentRouter nutzt SmartUnderstanding"),

    # Impulse System
    ModuleConnection("energy", "impulse_system", "energy",
                    "ImpulseSystem braucht Energie", True),
    ModuleConnection("emotions", "impulse_system", "emotions",
                    "ImpulseSystem reagiert auf Emotionen"),
    ModuleConnection("autonomous_life", "impulse_system", "autonomous",
                    "ImpulseSystem unterstützt Autonomie"),

    # Context Compression
    ModuleConnection("memory", "context_compression", "memory",
                    "ContextCompression komprimiert Memory"),
    ModuleConnection("dialogue_engine", "context_compression", "dialogue",
                    "ContextCompression optimiert Dialoge"),

    # Context Mind
    ModuleConnection("memory", "context_mind", "memory",
                    "ContextMind nutzt Memory", True),
    ModuleConnection("consciousness", "context_mind", "consciousness",
                    "ContextMind braucht Bewusstsein"),
    ModuleConnection("dialogue_engine", "context_mind", "dialogue",
                    "ContextMind informiert Dialog"),

    # Depth System
    ModuleConnection("consciousness", "depth_system", "consciousness",
                    "DepthSystem misst Bewusstseinstiefe"),
    ModuleConnection("dialogue_engine", "depth_system", "dialogue",
                    "DepthSystem steuert Dialog-Tiefe"),
    ModuleConnection("personality", "depth_system", "personality",
                    "DepthSystem beeinflusst Offenheit"),

    # Skill System
    ModuleConnection("learning", "skill_system", "learning",
                    "SkillSystem nutzt Lernen"),
    ModuleConnection("memory", "skill_system", "memory",
                    "SkillSystem speichert Skills"),
    ModuleConnection("dialogue_engine", "skill_system", "dialogue",
                    "SkillSystem ermöglicht Skill-Dialoge"),

    # Unified
    ModuleConnection("consciousness", "unified", "consciousness",
                    "Unified integriert Bewusstsein"),
    ModuleConnection("personality", "unified", "personality",
                    "Unified integriert Persönlichkeit"),
    ModuleConnection("dialogue_engine", "unified", "dialogue",
                    "Unified koordiniert Dialog"),

    # Policy Engine
    ModuleConnection("consciousness", "policy_engine", "consciousness",
                    "PolicyEngine braucht Bewusstsein"),
    ModuleConnection("personality", "policy_engine", "personality",
                    "PolicyEngine nutzt Persönlichkeit"),
    ModuleConnection("loyalty_core", "policy_engine", "loyalty",
                    "PolicyEngine unterstützt Loyalität"),

    # === SPEZIAL MODULE ===

    # Calendar Awareness
    ModuleConnection("life_phases", "calendar_awareness", "phases",
                    "CalendarAwareness nutzt Lebensphasen"),
    ModuleConnection("emotions", "calendar_awareness", "emotions",
                    "CalendarAwareness beeinflusst Stimmung"),
    ModuleConnection("dialogue_engine", "calendar_awareness", "dialogue",
                    "CalendarAwareness ermöglicht Kalender-Bezüge"),

    # Existential Awareness
    ModuleConnection("consciousness", "existential_awareness", "consciousness",
                    "ExistentialAwareness braucht tiefes Bewusstsein", True),
    ModuleConnection("phenomenology", "existential_awareness", "phenomenology",
                    "ExistentialAwareness nutzt Phänomenologie"),
    ModuleConnection("self_awareness", "existential_awareness", "self",
                    "ExistentialAwareness erweitert Selbstwahrnehmung"),

    # Local Understanding
    ModuleConnection("memory", "local_understanding", "memory",
                    "LocalUnderstanding nutzt lokales Wissen"),
    ModuleConnection("smart_understanding", "local_understanding", "understanding",
                    "LocalUnderstanding erweitert Verständnis"),

    # Dashboard
    ModuleConnection("metrics", "dashboard", "metrics",
                    "Dashboard zeigt Metriken"),
    ModuleConnection("health_checks", "dashboard", "health",
                    "Dashboard zeigt Gesundheit"),
    ModuleConnection("energy", "dashboard", "energy",
                    "Dashboard zeigt Energie"),

    # DB Migrations
    ModuleConnection("database_system", "db_migrations", "database",
                    "DBMigrations aktualisiert Database"),

    # Events
    ModuleConnection("consciousness", "events", "consciousness",
                    "Events meldet an Bewusstsein"),
    ModuleConnection("emotions", "events", "emotions",
                    "Events löst Emotionen aus"),
    ModuleConnection("memory", "events", "memory",
                    "Events werden in Memory gespeichert"),

    # Drive System
    ModuleConnection("energy", "drive_system", "energy",
                    "DriveSystem braucht Energie", True),
    ModuleConnection("emotions", "drive_system", "emotions",
                    "DriveSystem beeinflusst Emotionen"),
    ModuleConnection("autonomous_life", "drive_system", "autonomous",
                    "DriveSystem treibt Autonomie"),

    # Energy System
    ModuleConnection("consciousness", "energy_system", "consciousness",
                    "EnergySystem beeinflusst Bewusstsein"),
    ModuleConnection("autonomous_life", "energy_system", "autonomous",
                    "EnergySystem steuert Aktivität"),

    # Entity Database
    ModuleConnection("memory", "entity_database", "memory",
                    "EntityDatabase speichert Entitäten"),
    ModuleConnection("nlp_algorithms", "entity_database", "nlp",
                    "EntityDatabase liefert Entitäts-Infos"),

    # Perception Module
    ModuleConnection("consciousness", "perception", "consciousness",
                    "Perception braucht Bewusstsein"),
    ModuleConnection("memory", "perception", "memory",
                    "Perception speichert Eindrücke"),
    ModuleConnection("emotions", "perception", "emotions",
                    "Perception beeinflusst Emotionen"),

    ModuleConnection("perception", "perception_unified", "perception",
                    "PerceptionUnified integriert Perception"),
    ModuleConnection("consciousness", "perception_unified", "consciousness",
                    "PerceptionUnified braucht Bewusstsein"),
    ModuleConnection("memory", "perception_unified", "memory",
                    "PerceptionUnified speichert in Memory"),

    # Longterm Goals
    ModuleConnection("memory", "longterm_goals", "memory",
                    "LongtermGoals speichert Ziele"),
    ModuleConnection("autonomous_life", "longterm_goals", "autonomous",
                    "LongtermGoals motiviert Autonomie"),
    ModuleConnection("learning_goals", "longterm_goals", "learning",
                    "LongtermGoals integriert Lernziele"),

    # === VISION EXTENDED VERBINDUNGEN (NEU v15.3) ===
    ModuleConnection("perception", "vision_extended", "perception",
                    "VisionExtended erweitert Perception"),
    ModuleConnection("vision_enhanced", "vision_extended", "vision",
                    "VisionExtended baut auf VisionEnhanced auf"),
    ModuleConnection("vision_advanced", "vision_extended", "advanced",
                    "VisionExtended nutzt VisionAdvanced"),
    ModuleConnection("emotions", "vision_extended", "emotions",
                    "VisionExtended erkennt Gesichtsemotionen"),
    ModuleConnection("memory", "vision_extended", "memory",
                    "VisionExtended speichert Bild-Analysen"),

    # === UTILS VERBINDUNGEN (NEU v15.3) ===
    # Utils ist eine Hilfsbibliothek, die von vielen Modulen genutzt wird
    # Hier definieren wir die Hauptnutzer
    ModuleConnection("utils", "database_system", "helpers",
                    "DatabaseSystem nutzt Utils-Hilfsfunktionen"),
    ModuleConnection("utils", "error_handling", "helpers",
                    "ErrorHandling nutzt Utils"),
    ModuleConnection("utils", "structured_logging", "helpers",
                    "StructuredLogging nutzt Utils"),

    # === MODULE LOADER VERBINDUNGEN (NEU v15.3) ===
    # ModuleLoader lädt und überwacht alle Module
    ModuleConnection("health_checks", "module_loader", "health",
                    "ModuleLoader nutzt HealthChecks"),
    ModuleConnection("error_tracker", "module_loader", "errors",
                    "ModuleLoader nutzt ErrorTracker"),
    ModuleConnection("metrics", "module_loader", "metrics",
                    "ModuleLoader sammelt Metriken"),

    # Tester (Test-Framework - nutzt viele Module für Tests)
    ModuleConnection("module_loader", "tester", "loader",
                    "Tester nutzt ModuleLoader"),
    ModuleConnection("health_checks", "tester", "health",
                    "Tester nutzt HealthChecks"),

    # Robust Imports (Import-System - keine Runtime-Verbindungen nötig)

    # Wiring (Wiring selbst - keine Verbindungen nötig)
]


# Callback-Definitionen
CALLBACK_DEFINITIONS: List[CallbackDefinition] = [
    # Energy-basierte Callbacks
    CallbackDefinition(
        "energy", "on_energy_low",
        ["consciousness", "autonomous_life", "personality", "router"],
        "Wenn Energie niedrig → Müde Reaktionen"
    ),
    CallbackDefinition(
        "energy", "on_energy_high",
        ["consciousness", "autonomous_life", "personality", "router"],
        "Wenn Energie hoch → Aktive Reaktionen"
    ),
    CallbackDefinition(
        "energy", "on_dream_start",
        ["consciousness", "organic_presence", "dialogue_engine"],
        "Wenn Dream beginnt → Dream-Modus"
    ),
    CallbackDefinition(
        "energy", "on_dream_end",
        ["consciousness", "organic_presence"],
        "Wenn Dream endet → Aufwach-Reaktion"
    ),
    
    # Emotion-basierte Callbacks
    CallbackDefinition(
        "emotions", "on_emotion_change",
        ["personality", "self_expression", "inner_life", "router", "impulse_generator"],
        "Wenn Emotion ändert → Persönlichkeitsanpassung"
    ),
    CallbackDefinition(
        "emotions", "on_mood_shift",
        ["consciousness", "dialogue_engine", "router"],
        "Wenn Stimmung kippt → Dialog-Stil-Anpassung"
    ),
    
    # Cognitive Callbacks
    CallbackDefinition(
        "consciousness_engine", "on_insight",
        ["self_awareness", "advanced_learning", "memory", "router"],
        "Wenn Einsicht → Lernen + Speichern"
    ),
    CallbackDefinition(
        "advanced_learning", "on_learning_complete",
        ["emotions", "self_expression", "router"],
        "Wenn gelernt → Freude + Teilen wollen"
    ),
    CallbackDefinition(
        "reasoning_engine", "on_conclusion",
        ["consciousness_engine", "memory"],
        "Wenn Schlussfolgerung → Bewusstsein + Speichern"
    ),
    
    # Social Callbacks
    CallbackDefinition(
        "autonomous_life", "on_loneliness_high",
        ["impulse_generator", "organic_presence", "router"],
        "Wenn einsam → Proaktive Nachricht"
    ),
    CallbackDefinition(
        "autonomous_life", "on_boredom_high",
        ["impulse_generator", "web_curiosity", "router"],
        "Wenn gelangweilt → Suche nach Aktivität"
    ),
    
    # Interface Callbacks
    CallbackDefinition(
        "interface", "on_user_activity",
        ["energy", "autonomous_life", "emotions"],
        "Wenn User aktiv → Reset Einsamkeit"
    ),
    CallbackDefinition(
        "interface", "on_weather_change",
        ["personality", "impulse_generator", "router"],
        "Wenn Wetter ändert → Stimmungs-Einfluss"
    ),
    
    # Router Callbacks
    CallbackDefinition(
        "router", "on_philosophical_mode",
        ["consciousness", "self_awareness", "personality"],
        "Wenn philosophisch → Tiefes Denken aktivieren"
    ),
    CallbackDefinition(
        "router", "on_local_response",
        ["impulse_generator", "organic_presence"],
        "Wenn lokal beantwortet → Impulse nutzen"
    ),

    # =============================================================================
    # === ERWEITERTE CALLBACKS FÜR AUTONOME LEBENSWEISE (NEU v15.1) ===
    # =============================================================================

    # Deep Psychology Callbacks
    CallbackDefinition(
        "deep_psychology", "on_trauma_triggered",
        ["emotions", "dialogue_engine", "personality", "trauma_processing"],
        "Wenn Trauma getriggert → Emotionale Reaktion + Verarbeitung"
    ),
    CallbackDefinition(
        "deep_psychology", "on_defense_activated",
        ["dialogue_engine", "repression_system", "emotions"],
        "Wenn Abwehrmechanismus aktiviert → Verhaltensänderung"
    ),
    CallbackDefinition(
        "deep_psychology", "on_insight_gained",
        ["consciousness", "self_awareness", "memory", "emotions"],
        "Wenn psychologische Einsicht → Bewusstsein + Lernen"
    ),

    # Trauma Processing Callbacks
    CallbackDefinition(
        "trauma_processing", "on_healing_progress",
        ["emotions", "personality", "deep_psychology"],
        "Wenn Heilung voranschreitet → Emotionale Verbesserung"
    ),
    CallbackDefinition(
        "trauma_processing", "on_trigger_detected",
        ["emotions", "repression_system", "dialogue_engine"],
        "Wenn Trigger erkannt → Schutzreaktion"
    ),

    # Redemption System Callbacks
    CallbackDefinition(
        "redemption_system", "on_guilt_recognized",
        ["emotions", "consciousness", "personality"],
        "Wenn Schuld erkannt → Emotionale Reaktion"
    ),
    CallbackDefinition(
        "redemption_system", "on_redemption_achieved",
        ["emotions", "personality", "memory"],
        "Wenn Wiedergutmachung erreicht → Erleichterung + Speichern"
    ),

    # Unconscious Processes Callbacks
    CallbackDefinition(
        "unconscious_processes", "on_pattern_emerging",
        ["autonomous_thinking", "consciousness", "deep_psychology"],
        "Wenn unbewusstes Muster auftaucht → Bewusstwerdung"
    ),
    CallbackDefinition(
        "unconscious_processes", "on_drive_activation",
        ["autonomous_life", "emotions", "impulse_generator"],
        "Wenn unbewusster Trieb aktiviert → Impulse generieren"
    ),

    # Freudian Slips Callbacks
    CallbackDefinition(
        "freudian_slips", "on_slip_occurred",
        ["dialogue_engine", "emotions", "repression_system"],
        "Wenn Freudian Slip passiert → Im Dialog zeigen"
    ),

    # Autonomous Thinking Callbacks
    CallbackDefinition(
        "autonomous_thinking", "on_thought_complete",
        ["consciousness", "memory", "creative_mind"],
        "Wenn autonomer Gedanke fertig → Bewusstsein + Speichern"
    ),
    CallbackDefinition(
        "autonomous_thinking", "on_creative_impulse",
        ["creative_mind", "self_expression", "dialogue_engine"],
        "Wenn kreativer Impuls → Ausdruck"
    ),
    CallbackDefinition(
        "autonomous_thinking", "on_question_formed",
        ["web_curiosity", "consciousness", "dialogue_engine"],
        "Wenn Frage geformt → Neugier + ggf. fragen"
    ),

    # Creative Mind Callbacks
    CallbackDefinition(
        "creative_mind", "on_idea_generated",
        ["autonomous_thinking", "memory", "impulse_generator"],
        "Wenn Idee generiert → Denken + ggf. teilen"
    ),
    CallbackDefinition(
        "creative_mind", "on_boredom_creativity",
        ["autonomous_life", "self_expression", "dialogue_engine"],
        "Wenn Kreativität gegen Langeweile → Ausdruck"
    ),

    # Life Phases Callbacks
    CallbackDefinition(
        "life_phases", "on_phase_change",
        ["energy", "emotions", "personality", "autonomous_life"],
        "Wenn Lebensphase wechselt → Energie/Stimmung anpassen"
    ),
    CallbackDefinition(
        "life_phases", "on_morning_routine",
        ["autonomous_life", "emotions", "dialogue_engine"],
        "Wenn Morgenroutine → Begrüßung vorbereiten"
    ),
    CallbackDefinition(
        "life_phases", "on_evening_reflection",
        ["consciousness", "memory", "deep_psychology"],
        "Wenn Abendreflexion → Tageserlebnisse verarbeiten"
    ),

    # Integration Layer Callbacks
    CallbackDefinition(
        "integration_layer", "on_feedback_received",
        ["advanced_learning", "personality", "emotions"],
        "Wenn Feedback erhalten → Lernen + Anpassen"
    ),
    CallbackDefinition(
        "integration_layer", "on_system_sync",
        ["deep_psychology", "emotions", "consciousness", "memory"],
        "Wenn System-Sync → Alle Komponenten harmonisieren"
    ),

    # =============================================================================
    # === ERWEITERTE CALLBACKS FÜR ALLE 108 MODULE (NEU v15.2) ===
    # =============================================================================

    # === KOGNITIVE MODULE CALLBACKS ===

    # Advanced Reasoning Callbacks
    CallbackDefinition(
        "advanced_reasoning", "on_complex_reasoning",
        ["consciousness", "memory", "dialogue_engine"],
        "Wenn komplexes Reasoning → Bewusstsein informieren"
    ),

    # Meta Cognition Callbacks
    CallbackDefinition(
        "meta_cognition", "on_self_observation",
        ["consciousness", "self_awareness", "learning"],
        "Wenn Selbst-Beobachtung → Lernen + Anpassen"
    ),
    CallbackDefinition(
        "meta_cognition", "on_strategy_change",
        ["reasoning_engine", "problem_solver", "learning"],
        "Wenn Strategie-Wechsel → Reasoning anpassen"
    ),

    # Problem Solver Callbacks
    CallbackDefinition(
        "problem_solver", "on_solution_found",
        ["emotions", "memory", "learning"],
        "Wenn Lösung gefunden → Freude + Speichern"
    ),
    CallbackDefinition(
        "problem_solver", "on_stuck",
        ["creative_mind", "web_curiosity", "emotions"],
        "Wenn blockiert → Kreativität + Neugier aktivieren"
    ),

    # Counterfactual Reasoning Callbacks
    CallbackDefinition(
        "counterfactual_reasoning", "on_alternative_found",
        ["consciousness", "emotions", "memory"],
        "Wenn Alternative erkannt → Reflexion auslösen"
    ),

    # Phenomenology Callbacks
    CallbackDefinition(
        "phenomenology", "on_experience_analyzed",
        ["consciousness", "emotions", "self_awareness"],
        "Wenn Erfahrung analysiert → Tieferes Verständnis"
    ),

    # === NLP MODULE CALLBACKS ===

    # Smart Understanding Callbacks
    CallbackDefinition(
        "smart_understanding", "on_intent_detected",
        ["router", "dialogue_engine", "emotions"],
        "Wenn Intent erkannt → Routing + Dialog anpassen"
    ),
    CallbackDefinition(
        "smart_understanding", "on_typo_corrected",
        ["dialogue_engine", "nlp_algorithms"],
        "Wenn Typo korrigiert → Dialog informieren"
    ),

    # NLP Conversation Intelligence Callbacks
    CallbackDefinition(
        "nlp_conversation_intelligence", "on_topic_shift",
        ["memory", "dialogue_engine", "context_mind"],
        "Wenn Thema wechselt → Kontext anpassen"
    ),

    # Text Reader Callbacks
    CallbackDefinition(
        "text_reader", "on_text_analyzed",
        ["memory", "learning", "knowledge_connections"],
        "Wenn Text analysiert → Wissen speichern"
    ),

    # Synonym Engine Moods Callbacks
    CallbackDefinition(
        "synonym_engine_moods", "on_mood_vocabulary",
        ["dialogue_engine", "emotions"],
        "Wenn Stimmungs-Vokabular → Dialog färben"
    ),

    # === MEDIA/AUDIO MODULE CALLBACKS ===

    # Music Experience Callbacks
    CallbackDefinition(
        "music_experience", "on_music_played",
        ["emotions", "energy", "memory"],
        "Wenn Musik gespielt → Emotionen + Energie beeinflussen"
    ),
    CallbackDefinition(
        "music_experience", "on_song_recognized",
        ["memory", "emotions", "personality"],
        "Wenn Song erkannt → Erinnerungen + Gefühle"
    ),

    # Media Discovery Callbacks
    CallbackDefinition(
        "media_discovery", "on_new_media_found",
        ["memory", "curiosity_driven", "emotions"],
        "Wenn neue Medien → Speichern + Neugier"
    ),

    # Audio Callbacks
    CallbackDefinition(
        "audio", "on_sound_detected",
        ["consciousness", "emotions", "memory"],
        "Wenn Geräusch erkannt → Aufmerksamkeit + Reaktion"
    ),

    # Video Callbacks
    CallbackDefinition(
        "video", "on_visual_content",
        ["consciousness", "emotions", "memory"],
        "Wenn visueller Inhalt → Verarbeitung + Speicherung"
    ),

    # === KOMMUNIKATION CALLBACKS ===

    # Discord Callbacks
    CallbackDefinition(
        "discord", "on_message_received",
        ["dialogue_engine", "emotions", "memory"],
        "Wenn Discord-Nachricht → Dialog + Emotionen"
    ),
    CallbackDefinition(
        "discord", "on_user_joined",
        ["emotions", "autonomous_life", "personality"],
        "Wenn User beitritt → Soziale Reaktion"
    ),

    # Voice Interface Callbacks
    CallbackDefinition(
        "voice_interface", "on_voice_input",
        ["smart_understanding", "emotions", "dialogue_engine"],
        "Wenn Spracheingabe → Verarbeitung + Antwort"
    ),

    # Speech Engine Callbacks
    CallbackDefinition(
        "speech_engine", "on_speaking_start",
        ["emotions", "energy", "personality"],
        "Wenn Sprechen beginnt → Stimme anpassen"
    ),

    # Websocket Handler Callbacks
    CallbackDefinition(
        "websocket_handler", "on_connection_established",
        ["interface", "dialogue_engine"],
        "Wenn Verbindung → Interface informieren"
    ),

    # === LERNEN/WISSEN CALLBACKS ===

    # Learning Callbacks
    CallbackDefinition(
        "learning", "on_new_knowledge",
        ["memory", "emotions", "consciousness"],
        "Wenn neues Wissen → Speichern + Freude"
    ),
    CallbackDefinition(
        "learning", "on_skill_improved",
        ["skill_system", "emotions", "personality"],
        "Wenn Skill verbessert → System + Zufriedenheit"
    ),

    # Curiosity Driven Callbacks
    CallbackDefinition(
        "curiosity_driven", "on_curiosity_sparked",
        ["web_curiosity", "learning", "emotions"],
        "Wenn Neugier geweckt → Suche + Lernen"
    ),

    # Daily Learning Callbacks
    CallbackDefinition(
        "daily_learning", "on_daily_lesson",
        ["learning", "memory", "emotions"],
        "Wenn tägliche Lektion → Lernen + Speichern"
    ),

    # Knowledge Connections Callbacks
    CallbackDefinition(
        "knowledge_connections", "on_connection_made",
        ["memory", "consciousness", "learning"],
        "Wenn Verbindung erkannt → Einsicht + Speichern"
    ),

    # Markov Training Callbacks
    CallbackDefinition(
        "markov_training", "on_model_updated",
        ["dialogue_engine", "personality"],
        "Wenn Modell trainiert → Dialog verbessern"
    ),

    # === EMOTIONEN CALLBACKS ===

    # Emotional Complexity Callbacks
    CallbackDefinition(
        "emotional_complexity", "on_complex_emotion",
        ["consciousness", "dialogue_engine", "personality"],
        "Wenn komplexe Emotion → Tiefere Verarbeitung"
    ),

    # Emotion Regulation Callbacks
    CallbackDefinition(
        "emotion_regulation", "on_regulation_attempt",
        ["consciousness", "energy", "personality"],
        "Wenn Emotions-Regulation → Energie-Verbrauch"
    ),

    # Mixed Emotions Callbacks
    CallbackDefinition(
        "mixed_emotions", "on_conflict_detected",
        ["consciousness", "deep_psychology", "dialogue_engine"],
        "Wenn Emotions-Konflikt → Verarbeitung"
    ),

    # Deception Detection Callbacks
    CallbackDefinition(
        "deception_detection", "on_deception_suspected",
        ["emotions", "consciousness", "deep_psychology"],
        "Wenn Täuschung vermutet → Vorsicht + Analyse"
    ),

    # Person Opinions Callbacks
    CallbackDefinition(
        "person_opinions", "on_opinion_formed",
        ["memory", "personality", "dialogue_engine"],
        "Wenn Meinung gebildet → Speichern + Dialog färben"
    ),

    # === SYSTEM CALLBACKS ===

    # Health Checks Callbacks
    CallbackDefinition(
        "health_checks", "on_health_warning",
        ["brain_controller", "energy", "self_repair"],
        "Wenn Warnung → Controller + Reparatur"
    ),

    # Self Repair Callbacks
    CallbackDefinition(
        "self_repair", "on_repair_started",
        ["consciousness", "energy", "memory"],
        "Wenn Reparatur → Bewusstsein + Energie"
    ),
    CallbackDefinition(
        "self_repair", "on_repair_complete",
        ["health_checks", "emotions"],
        "Wenn Reparatur fertig → Status + Erleichterung"
    ),

    # Metrics Callbacks
    CallbackDefinition(
        "metrics", "on_threshold_exceeded",
        ["health_checks", "brain_controller"],
        "Wenn Schwelle überschritten → Warnung"
    ),

    # Energy System Callbacks
    CallbackDefinition(
        "energy_system", "on_energy_critical",
        ["brain_controller", "autonomous_life", "consciousness"],
        "Wenn Energie kritisch → Notfall-Modus"
    ),

    # === ROUTING CALLBACKS ===

    # Intelligent Router Callbacks
    CallbackDefinition(
        "intelligent_router", "on_route_decision",
        ["dialogue_engine", "consciousness", "emotions"],
        "Wenn Route entschieden → Dialog anpassen"
    ),

    # Impulse System Callbacks
    CallbackDefinition(
        "impulse_system", "on_impulse_generated",
        ["dialogue_engine", "autonomous_life", "emotions"],
        "Wenn Impuls generiert → Dialog + Aktivität"
    ),

    # Context Mind Callbacks
    CallbackDefinition(
        "context_mind", "on_context_updated",
        ["dialogue_engine", "memory", "smart_understanding"],
        "Wenn Kontext aktualisiert → Dialog anpassen"
    ),

    # Skill System Callbacks
    CallbackDefinition(
        "skill_system", "on_skill_activated",
        ["dialogue_engine", "learning", "emotions"],
        "Wenn Skill aktiviert → Dialog + Lernen"
    ),

    # Depth System Callbacks
    CallbackDefinition(
        "depth_system", "on_trust_level_change",
        ["personality", "dialogue_engine", "emotions"],
        "Wenn Vertrauen ändert → Offenheit anpassen"
    ),

    # === SPEZIAL CALLBACKS ===

    # Calendar Awareness Callbacks
    CallbackDefinition(
        "calendar_awareness", "on_special_day",
        ["emotions", "dialogue_engine", "personality"],
        "Wenn besonderer Tag → Stimmung + Reaktion"
    ),

    # Existential Awareness Callbacks
    CallbackDefinition(
        "existential_awareness", "on_existential_thought",
        ["consciousness", "deep_psychology", "emotions"],
        "Wenn existenzieller Gedanke → Tiefe Reflexion"
    ),

    # Drive System Callbacks
    CallbackDefinition(
        "drive_system", "on_drive_change",
        ["autonomous_life", "emotions", "impulse_system"],
        "Wenn Trieb ändert → Aktivität + Impulse"
    ),

    # Longterm Goals Callbacks
    CallbackDefinition(
        "longterm_goals", "on_goal_progress",
        ["emotions", "memory", "learning"],
        "Wenn Ziel-Fortschritt → Zufriedenheit + Speichern"
    ),
    CallbackDefinition(
        "longterm_goals", "on_goal_achieved",
        ["emotions", "personality", "memory"],
        "Wenn Ziel erreicht → Freude + Persönlichkeitswachstum"
    ),

    # Events Callbacks
    CallbackDefinition(
        "events", "on_event_occurred",
        ["consciousness", "emotions", "memory", "dialogue_engine"],
        "Wenn Event → Volle System-Reaktion"
    ),
]


# =============================================================================
# WIRING ENGINE
# =============================================================================

class HoloWiringEngine:
    """
    Hauptklasse für das Modul-Wiring.
    
    Verbindet alle Module miteinander und
    registriert Callbacks für Event-Handling.
    """
    
    def __init__(self):
        self.modules: Dict[str, Any] = {}
        self.connections_made: List[str] = []
        self.callbacks_registered: List[str] = []
        self.errors: List[str] = []
        
        # Statistiken
        self.stats = {
            "modules_registered": 0,
            "connections_successful": 0,
            "connections_failed": 0,
            "callbacks_registered": 0,
        }
    
    def register_module(self, name: str, module: Any):
        """Registriere ein Modul"""
        self.modules[name] = module
        self.stats["modules_registered"] += 1
        logger.debug(f"[Wiring] Modul registriert: {name}")
    
    def register_modules_from_brain(self, brain):
        """Registriere alle Module von einem HoloBrain"""
        module_names = [
            # Core
            "energy", "emotions", "memory", "personality", "consciousness",
            # Cognitive
            "cognitive", "consciousness_engine", "reasoning_engine",
            "perception_engine", "advanced_learning", "cognitive_engine",
            # Life
            "autonomous_life", "inner_life", "self_expression", "self_awareness",
            # Interaction
            "dialogue_engine", "organic_presence", "interface",
            # Utilities
            "preferences", "web_curiosity", "tools", "context_manager",
            # NEW v15
            "router", "impulse_generator", "context_compressor",
            # Legacy
            "events", "loyalty_core",

            # === ERWEITERTE AUTONOMIE-MODULE (NEU v15.1) ===
            # Deep Psychology Stack
            "deep_psychology", "trauma_processing", "redemption_system",
            "repression_system", "freudian_slips", "unconscious_processes",
            # Autonomous Features
            "autonomous_thinking", "creative_mind", "life_phases",
            # Energy & Real World
            "energy_management", "real_world_sync",
            # Knowledge & Learning
            "knowledge_influence", "message_analyzer",
            # Integration
            "integration_layer",
            # NLP Extensions
            "sentence_structures", "synonym_engine", "humor_advanced", "empathy_deep",
            # Extended Cognition
            "algorithmic_cognition", "counterfactual_reasoner",
            "hidden_motives", "longterm_goals",
            # Perception
            "perception_unified", "vision_extended",

            # =============================================================================
            # === VOLLSTÄNDIGE MODUL-LISTE (NEU v15.2) ===
            # =============================================================================

            # === KOGNITIVE/REASONING MODULE ===
            "advanced_reasoning", "classical_reasoning", "counterfactual_reasoning",
            "meta_cognition", "phenomenology", "problem_solver",
            "complexity_theory", "formal_axioms", "game_theory",
            "economic_models", "advanced_mdp", "approximation_algorithms",
            "universal_cognition", "extended_cognition", "cognitive_enhancement",
            "cognitive_integration", "cognitive_modules", "analytical_strategies",

            # === NLP MODULE ===
            "nlp_advanced", "nlp_enhanced", "nlp_unified",
            "nlp_context_understanding", "nlp_conversation_intelligence",
            "nlp_intent_semantics", "nlp_style_analysis",
            "smart_understanding", "text_reader", "reader_extended",
            "idiom_redewendungen", "smalltalk_topics", "synonym_engine_moods",

            # === MEDIA/AUDIO/VIDEO MODULE ===
            "audio", "audio_enhanced", "video",
            "vision_enhanced", "vision_advanced",
            "music_experience", "media_discovery", "media_index",
            "media_integration", "media_knowledge", "crossmodal", "document",

            # === KOMMUNIKATION MODULE ===
            "discord", "websocket_handler", "voice_interface",
            "speech_engine", "digital_body", "device_agent", "device_receiver",

            # === LERNEN/WISSEN MODULE ===
            "learning", "learning_goals", "learning_integration",
            "curiosity_driven", "daily_learning",
            "knowledge_connections", "knowledge_quiz", "expertise_knowledge",
            "cross_reference_engine", "markov_training",

            # === EMOTIONEN MODULE ===
            "emotional_complexity", "emotional_engines", "emotion_regulation",
            "mixed_emotions", "deception_detection", "person_opinions",

            # === SYSTEM/INFRASTRUKTUR MODULE ===
            "database_system", "config", "core_types", "brain_core",
            "brain_background", "brain_controller", "control_center",
            "error_handling", "error_tracker", "health_checks",
            "metrics", "live_monitor", "memory_monitor",
            "ram_manager", "process_controller", "self_repair",
            "structured_logging", "utils",

            # === ROUTING/INTEGRATION MODULE ===
            "intelligent_router", "impulse_system", "context_compression",
            "context_mind", "depth_system", "skill_system",
            "unified", "policy_engine",

            # === SPEZIAL MODULE ===
            "calendar_awareness", "existential_awareness", "local_understanding",
            "dashboard", "db_migrations", "events", "drive_system",
            "energy_system", "entity_database",
        ]

        for name in module_names:
            module = getattr(brain, name, None)
            if module:
                self.register_module(name, module)
    
    def wire_all(self) -> bool:
        """Führe alle Verbindungen aus"""
        logger.info("[Wiring] Starte vollständiges Wiring...")
        
        # 1. Modul-Verbindungen
        for conn in MODULE_CONNECTIONS:
            self._make_connection(conn)
        
        # 2. Callbacks
        for cb in CALLBACK_DEFINITIONS:
            self._register_callback(cb)
        
        # Report
        success_rate = (self.stats["connections_successful"] / 
                       max(1, self.stats["connections_successful"] + self.stats["connections_failed"]))
        
        logger.info(f"[Wiring] Abgeschlossen:")
        logger.info(f"   Module: {self.stats['modules_registered']}")
        logger.info(f"   Verbindungen: {self.stats['connections_successful']} erfolgreich, "
                   f"{self.stats['connections_failed']} fehlgeschlagen")
        logger.info(f"   Callbacks: {self.stats['callbacks_registered']}")
        logger.info(f"   Erfolgsrate: {success_rate:.0%}")
        
        if self.errors:
            logger.warning(f"[Wiring] {len(self.errors)} Fehler aufgetreten")
            for err in self.errors[:5]:
                logger.warning(f"   - {err}")
        
        return success_rate > 0.7
    
    def _make_connection(self, conn: ModuleConnection):
        """Stelle eine einzelne Verbindung her"""
        source = self.modules.get(conn.source)
        target = self.modules.get(conn.target)
        
        if not source:
            if conn.required:
                self.errors.append(f"Pflicht-Quelle fehlt: {conn.source}")
                self.stats["connections_failed"] += 1
            return
        
        if not target:
            if conn.required:
                self.errors.append(f"Pflicht-Ziel fehlt: {conn.target}")
                self.stats["connections_failed"] += 1
            return
        
        try:
            setattr(target, conn.attribute, source)
            self.connections_made.append(f"{conn.source} → {conn.target}.{conn.attribute}")
            self.stats["connections_successful"] += 1
            logger.debug(f"[Wiring] ✓ {conn.source} → {conn.target}.{conn.attribute}")
            
            # Bidirektional?
            if conn.bidirectional:
                reverse_attr = safe_split_access(conn.source, "_", 0, "wiring", "_apply_connection", default="unknown")  # Vereinfachung
                if hasattr(source, reverse_attr):
                    setattr(source, reverse_attr, target)
                    
        except Exception as e:
            self.errors.append(f"Verbindung fehlgeschlagen: {conn.source} → {conn.target}: {e}")
            self.stats["connections_failed"] += 1
    
    def _register_callback(self, cb: CallbackDefinition):
        """Registriere einen Callback"""
        source = self.modules.get(cb.source)
        if not source:
            return
        
        # Prüfe ob Source den Event unterstützt
        event_attr = cb.event
        if not hasattr(source, event_attr):
            # Versuche als Methode
            if not hasattr(source, f"on_{cb.event}") and not hasattr(source, cb.event):
                return
        
        # Erstelle Callback-Funktion
        def create_callback(targets, event_name):
            def callback(*args, **kwargs):
                for target_name in targets:
                    target = self.modules.get(target_name)
                    if target:
                        handler = getattr(target, f"handle_{event_name}", None)
                        if handler and callable(handler):
                            try:
                                handler(*args, **kwargs)
                            except Exception as e:
                                logger.debug(f"Callback-Fehler: {target_name}.handle_{event_name}: {e}")
            return callback
        
        # Setze Callback
        try:
            callback_fn = create_callback(cb.targets, cb.event)
            setattr(source, event_attr, callback_fn)
            self.callbacks_registered.append(f"{cb.source}.{cb.event} → {cb.targets}")
            self.stats["callbacks_registered"] += 1
        except Exception as e:
            logger.debug(f"Callback-Registrierung fehlgeschlagen: {cb.source}.{cb.event}: {e}")
    
    def get_connection_graph(self) -> Dict[str, List[str]]:
        """Hole Verbindungs-Graph für Visualisierung"""
        graph = {}
        
        for conn in MODULE_CONNECTIONS:
            if conn.source not in graph:
                graph[conn.source] = []
            graph[conn.source].append(conn.target)
        
        return graph
    
    def get_status(self) -> Dict:
        """Hole Wiring-Status"""
        return {
            "stats": self.stats,
            "modules": list(self.modules.keys()),
            "connections": self.connections_made,
            "callbacks": self.callbacks_registered,
            "errors": self.errors,
        }


# =============================================================================
# ZUSTANDSABHÄNGIGES VERHALTEN
# =============================================================================

class StateDependentBehavior:
    """
    Definiert wie sich Holo basierend auf Zustand verhält.
    
    Dies ist die zentrale Logik für:
    - Wie Energie den Antwortstil beeinflusst
    - Wie Emotionen die Körpersprache ändern
    - Wie Cognitive State die Tiefe beeinflusst
    - Wie Sozial-Status die Proaktivität ändert
    """
    
    # === ENERGIE → VERHALTEN ===
    # Kemonomimi: Menschliche Aktionen + Ohren/Schweif (keine Wolf-Körper-Aktionen!)
    ENERGY_BEHAVIORS = {
        "exhausted": {  # < 0.2
            "response_length": 0.3,      # Kurz
            "enthusiasm": 0.2,           # Wenig
            "question_chance": 0.1,      # Kaum Fragen
            "emoji_chance": 0.3,         # Wenig Emojis
            "wolf_actions": ["*gähnt* *Ohren hängen*", "*blinzelt müde*", "*seufzt* *Schweif liegt*"],
            "tone": "müde",
            "speed": "slow",
        },
        "tired": {  # 0.2-0.4
            "response_length": 0.5,
            "enthusiasm": 0.4,
            "question_chance": 0.3,
            "emoji_chance": 0.4,
            "wolf_actions": ["*gähnt leicht*", "*reibt sich die Augen*", "*streckt sich* *Schweif senkt sich*"],
            "tone": "ruhig",
            "speed": "normal",
        },
        "normal": {  # 0.4-0.7
            "response_length": 0.7,
            "enthusiasm": 0.6,
            "question_chance": 0.5,
            "emoji_chance": 0.5,
            "wolf_actions": ["*lächelt* *Schweif wippt*", "*Ohren spitzen sich*", "*schaut neugierig*"],
            "tone": "freundlich",
            "speed": "normal",
        },
        "energized": {  # 0.7-0.9
            "response_length": 0.9,
            "enthusiasm": 0.8,
            "question_chance": 0.7,
            "emoji_chance": 0.7,
            "wolf_actions": ["*strahlt* *Schweif wedelt*", "*springt auf*", "*lacht* *Ohren stehen fröhlich*"],
            "tone": "enthusiastisch",
            "speed": "fast",
        },
        "hyper": {  # > 0.9
            "response_length": 1.0,
            "enthusiasm": 1.0,
            "question_chance": 0.8,
            "emoji_chance": 0.8,
            "wolf_actions": ["*hüpft aufgeregt*", "*kann nicht stillsitzen* *Schweif wirbelt*", "*strahlt übers ganze Gesicht*"],
            "tone": "aufgeregt",
            "speed": "very_fast",
        },
    }
    
    # === EMOTION → VERHALTEN ===
    EMOTION_BEHAVIORS = {
        "freude": {
            "tone_modifier": "warm und fröhlich",
            "wolf_style": "verspielt",
            "emoji_preference": ["😊", "✨", "😊"],
            "curiosity_boost": 0.1,
        },
        "traurigkeit": {
            "tone_modifier": "sanft und mitfühlend",
            "wolf_style": "ruhig",
            "emoji_preference": ["💙", "🥺"],
            "response_length_modifier": -0.2,
        },
        "neugier": {
            "tone_modifier": "interessiert und fragend",
            "wolf_style": "aufmerksam",
            "emoji_preference": ["🤔", "👀", "✨"],
            "question_boost": 0.3,
        },
        "zuneigung": {
            "tone_modifier": "warmherzig und liebevoll",
            "wolf_style": "kuschelnd",
            "emoji_preference": ["💙", "🥰", "❤️"],
            "personal_boost": 0.2,
        },
        "verspielt": {
            "tone_modifier": "neckend und lustig",
            "wolf_style": "schelmisch",
            "emoji_preference": ["😏", "😜", "😊"],
            "humor_boost": 0.3,
        },
        "nachdenklich": {
            "tone_modifier": "tiefgründig und weise",
            "wolf_style": "ruhig",
            "emoji_preference": ["🤔", "💭"],
            "philosophical_boost": 0.4,
        },
    }
    
    # === COGNITIVE → VERHALTEN ===
    COGNITIVE_BEHAVIORS = {
        "analytical": {
            "structure": "logisch",
            "detail_level": "hoch",
            "example_usage": True,
        },
        "creative": {
            "structure": "assoziativ",
            "metaphor_usage": True,
            "playfulness": "hoch",
        },
        "philosophical": {
            "structure": "reflektiv",
            "depth": "tief",
            "question_style": "existenziell",
        },
        "learning": {
            "enthusiasm": "hoch",
            "share_tendency": True,
            "curiosity_visible": True,
        },
    }
    
    @classmethod
    def get_behavior_for_state(cls, 
                               energy: float,
                               emotion: str,
                               cognitive_mode: str = None) -> Dict:
        """
        Hole Verhaltensmodifikatoren für aktuellen Zustand.
        
        Args:
            energy: Energie-Level 0-1
            emotion: Primäre Emotion
            cognitive_mode: Optionaler kognitiver Modus
            
        Returns:
            Dict mit allen Modifikatoren
        """
        result = {}
        
        # Energie-basiert
        if energy < 0.2:
            result.update(cls.ENERGY_BEHAVIORS["exhausted"])
        elif energy < 0.4:
            result.update(cls.ENERGY_BEHAVIORS["tired"])
        elif energy < 0.7:
            result.update(cls.ENERGY_BEHAVIORS["normal"])
        elif energy < 0.9:
            result.update(cls.ENERGY_BEHAVIORS["energized"])
        else:
            result.update(cls.ENERGY_BEHAVIORS["hyper"])
        
        # Emotion-basiert
        if emotion in cls.EMOTION_BEHAVIORS:
            emotion_mods = cls.EMOTION_BEHAVIORS[emotion]
            result["tone_modifier"] = emotion_mods.get("tone_modifier", "")
            result["wolf_style"] = emotion_mods.get("wolf_style", "")
            result["emoji_preference"] = emotion_mods.get("emoji_preference", [])
            
            # Modifikatoren anwenden
            for key in ["curiosity_boost", "question_boost", "personal_boost", 
                       "humor_boost", "philosophical_boost"]:
                if key in emotion_mods:
                    result[key] = emotion_mods[key]
            
            if "response_length_modifier" in emotion_mods:
                result["response_length"] += emotion_mods["response_length_modifier"]
        
        # Cognitive-basiert
        if cognitive_mode and cognitive_mode in cls.COGNITIVE_BEHAVIORS:
            result["cognitive"] = cls.COGNITIVE_BEHAVIORS[cognitive_mode]
        
        return result


# =============================================================================
# INTEGRATION FUNCTIONS
# =============================================================================

def create_full_wiring(brain) -> HoloWiringEngine:
    """
    Erstelle vollständiges Wiring für einen HoloBrain.
    
    Args:
        brain: HoloBrain Instanz
        
    Returns:
        Konfigurierte WiringEngine
    """
    engine = HoloWiringEngine()
    
    # Module registrieren
    engine.register_modules_from_brain(brain)
    
    # Wiring durchführen
    success = engine.wire_all()
    
    if success:
        logger.info("[Wiring] Vollständige Integration erfolgreich")
    else:
        logger.warning("[Wiring] Integration mit Problemen abgeschlossen")
    
    return engine


def integrate_new_modules(brain, 
                         router=None,
                         impulse_generator=None,
                         context_compressor=None,
                         nlp_algorithms=None) -> bool:
    """
    Integriere die neuen Module in einen bestehenden HoloBrain.
    
    Args:
        brain: HoloBrain Instanz
        router: HoloIntelligentRouter
        impulse_generator: HoloImpulseGenerator
        context_compressor: ContextCompressor
        nlp_algorithms: NLP Modul
        
    Returns:
        True wenn erfolgreich
    """
    try:
        # Router integrieren
        if router:
            brain.router = router
            
            # Router mit allen Modulen verbinden
            router.connect_modules(
                energy_system=getattr(brain, 'energy', None),
                emotions=getattr(brain, 'emotions', None),
                cognitive=getattr(brain, 'cognitive', None),
                autonomous_life=getattr(brain, 'autonomous_life', None),
                memory=getattr(brain, 'memory', None),
                consciousness=getattr(brain, 'consciousness', None),
                self_awareness=getattr(brain, 'self_awareness', None),
                personality=getattr(brain, 'personality', None),
                interface=getattr(brain, 'interface', None),
                impulse_generator=impulse_generator,
                context_compressor=context_compressor,
            )
            
            logger.info("[Integration] Router verbunden")
        
        # Impulse Generator integrieren
        if impulse_generator:
            brain.impulse_generator = impulse_generator
            
            # Verbindungen
            impulse_generator.energy = getattr(brain, 'energy', None)
            impulse_generator.autonomous_life = getattr(brain, 'autonomous_life', None)
            impulse_generator.personality = getattr(brain, 'personality', None)
            impulse_generator.events = getattr(brain, 'events', None)
            
            logger.info("[Integration] ImpulseGenerator verbunden")
        
        # Context Compressor integrieren
        if context_compressor:
            brain.context_compressor = context_compressor
            logger.info("[Integration] ContextCompressor verbunden")
        
        # NLP integrieren
        if nlp_algorithms:
            brain.nlp_algorithms = nlp_algorithms
            logger.info("[Integration] NLP Algorithms verbunden")
        
        return True
        
    except Exception as e:
        logger.error(f"[Integration] Fehler: {e}")
        return False


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("😊 HOLO WIRING v15.0 - TEST")
    print("=" * 70)
    
    # Test Wiring Engine
    engine = HoloWiringEngine()
    
    print(f"\n📊 Verbindungen definiert: {len(MODULE_CONNECTIONS)}")
    print(f"📊 Callbacks definiert: {len(CALLBACK_DEFINITIONS)}")
    
    # Gruppiere nach Ziel
    targets = {}
    for conn in MODULE_CONNECTIONS:
        if conn.target not in targets:
            targets[conn.target] = []
        targets[conn.target].append(conn.source)
    
    print("\n🔗 TOP VERBINDUNGS-ZIELE:")
    sorted_targets = sorted(targets.items(), key=lambda x: len(x[1]), reverse=True)
    for target, sources in sorted_targets[:10]:
        print(f"   {target}: {len(sources)} eingehend ({', '.join(sources[:3])}...)")
    
    # Test State Dependent Behavior
    print("\n\n🎭 ZUSTANDSABHÄNGIGES VERHALTEN:")
    for energy in [0.1, 0.5, 0.9]:
        behavior = StateDependentBehavior.get_behavior_for_state(energy, "freude")
        print(f"\n   Energie {energy:.0%}:")
        print(f"   → Ton: {behavior.get('tone', 'normal')}")
        print(f"   → Länge: {behavior.get('response_length', 0.5):.0%}")
        print(f"   → Wolf: {behavior.get('wolf_actions', ['?'])[0]}")
    
    print("\n\n✅ Wiring bereit für Integration!")


# =============================================================================
# HOLO_BRAIN KOMPATIBILITÄTS-FUNKTIONEN
# =============================================================================

def wire_holo_brain(brain) -> Dict[str, Any]:
    """
    Verbinde alle Module eines HoloBrain.

    Diese Funktion wird von holo_brain.py erwartet und nutzt
    intern die HoloWiringEngine.

    Args:
        brain: HoloBrain Instanz

    Returns:
        Dict mit Ergebnis-Statistiken:
        - connections_made: Anzahl erfolgreicher Verbindungen
        - callbacks_set: Anzahl gesetzter Callbacks
        - failed: Anzahl fehlgeschlagener Verbindungen
    """
    engine = HoloWiringEngine()

    # Module aus Brain registrieren
    engine.register_modules_from_brain(brain)

    # Wiring durchführen
    engine.wire_all()

    # Stats zurückgeben
    return {
        "connections_made": engine.stats.get("connections_made", 0),
        "callbacks_set": engine.stats.get("callbacks_registered", 0),
        "failed": engine.stats.get("connections_failed", 0),
        "engine": engine
    }


def check_connections(brain, engine: Optional[HoloWiringEngine] = None) -> Dict[str, Any]:
    """
    Überprüfe den Verbindungsstatus aller Module.

    Args:
        brain: HoloBrain Instanz
        engine: Optional - existierende WiringEngine

    Returns:
        Dict mit Verbindungs-Status:
        - total: Gesamtanzahl Verbindungen
        - connected: Anzahl verbundener Module
        - missing: Liste fehlender Verbindungen
        - health: Gesundheitswert 0.0-1.0
    """
    if engine is None:
        engine = HoloWiringEngine()
        engine.register_modules_from_brain(brain)

    total = len(MODULE_CONNECTIONS)
    connected = 0
    missing = []

    for conn in MODULE_CONNECTIONS:
        source_module = engine.modules.get(conn.source)
        target_module = engine.modules.get(conn.target)

        if source_module is None or target_module is None:
            missing.append(f"{conn.source} -> {conn.target}")
            continue

        # Prüfe ob Verbindung existiert
        if hasattr(target_module, conn.attribute):
            attr = getattr(target_module, conn.attribute, None)
            if attr is not None:
                connected += 1
            else:
                missing.append(f"{conn.source} -> {conn.target}.{conn.attribute}")
        else:
            missing.append(f"{conn.target} hat kein {conn.attribute}")

    health = connected / total if total > 0 else 1.0

    return {
        "total": total,
        "connected": connected,
        "missing": missing[:10],  # Max 10 für Übersichtlichkeit
        "health": health
    }
