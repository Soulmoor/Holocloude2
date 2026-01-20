"""
Holo Universal Cognition Hub - Zentrales Denk-System
=====================================================

Verbindet ALLE kognitiven Systeme zu einem einheitlichen Denk-Framework.
Jedes System kann auf jedes andere zugreifen.

Verbundene Systeme:
1. Problem Solver (Out-of-Box Thinking, Zerlegung, Simulation)
2. Autonomous Thinking (Intuition, Hypothesen, Analogien)
3. Algorithmic Cognition (Analytische Strategien)
4. Cognitive Enhancement (Wissens-Injektion, Reasoning)
5. Meta-Cognition (Denken über Denken)
6. Creative Mind (Kreatives Denken)
7. Learning System (Lernen aus Erfahrungen)
8. Self-Awareness (Selbstwahrnehmung)

Autor: Claude (Anthropic) für Holo
Version: 1.0.0
"""

import logging
import time
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class CognitiveThought:
    """Ein Gedanke der durch das kognitive System fließt"""
    id: str
    content: str
    source_system: str  # Welches System hat ihn erzeugt?
    thought_type: str   # question, hypothesis, insight, intuition, etc.
    confidence: float = 0.5
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)


@dataclass
class CognitiveResult:
    """Ergebnis eines Denk-Prozesses"""
    success: bool
    thoughts: List[CognitiveThought]
    insights: List[str]
    recommendations: List[str]
    thinking_time_ms: int
    systems_used: List[str]
    metadata: Dict = field(default_factory=dict)


class UniversalCognitionHub:
    """
    Zentraler Hub der ALLE kognitiven Systeme verbindet.

    Ermöglicht:
    - Jedes System kann jedes andere nutzen
    - Einheitliche Schnittstelle für alle Denk-Prozesse
    - Automatische Koordination zwischen Systemen
    - Gedanken fließen zwischen Systemen
    """

    def __init__(self, holo_brain=None):
        self.brain = holo_brain

        # Alle verbundenen Systeme
        self._systems: Dict[str, Any] = {}

        # Gedanken-Stream (fließt durch alle Systeme)
        self._thought_stream: List[CognitiveThought] = []

        # Statistiken
        self.stats = {
            "total_thoughts": 0,
            "systems_invoked": 0,
            "cross_system_connections": 0,
        }

        # Initialisiere Verbindungen
        self._connect_all_systems()

        logger.info(f"Universal Cognition Hub initialisiert mit {len(self._systems)} Systemen")

    def _connect_all_systems(self):
        """Verbindet alle verfügbaren kognitiven Systeme"""

        if not self.brain:
            logger.warning("Kein HoloBrain verfügbar - Systeme werden später verbunden")
            return

        # =====================================================================
        # 1. PROBLEM SOLVER - Analytisches Denken
        # =====================================================================
        if hasattr(self.brain, 'problem_solver') and self.brain.problem_solver:
            self._systems['problem_solver'] = self.brain.problem_solver
            logger.debug("✓ Problem Solver verbunden")

        # =====================================================================
        # 2. AUTONOMOUS THINKING - Selbstständiges Denken
        # =====================================================================
        # Intuition
        if hasattr(self.brain, 'intuitive_system') and self.brain.intuitive_system:
            self._systems['intuition'] = self.brain.intuitive_system
            logger.debug("✓ Intuitive System verbunden")

        # Self-Challenger
        if hasattr(self.brain, 'self_challenger') and self.brain.self_challenger:
            self._systems['self_challenger'] = self.brain.self_challenger
            logger.debug("✓ Self-Challenger verbunden")

        # Hypothesis Engine
        if hasattr(self.brain, 'hypothesis_engine') and self.brain.hypothesis_engine:
            self._systems['hypothesis_engine'] = self.brain.hypothesis_engine
            logger.debug("✓ Hypothesis Engine verbunden")

        # Prediction System
        if hasattr(self.brain, 'prediction_system') and self.brain.prediction_system:
            self._systems['prediction'] = self.brain.prediction_system
            logger.debug("✓ Prediction System verbunden")

        # Analogy Engine
        if hasattr(self.brain, 'analogy_engine') and self.brain.analogy_engine:
            self._systems['analogy'] = self.brain.analogy_engine
            logger.debug("✓ Analogy Engine verbunden")

        # Regret Learning
        if hasattr(self.brain, 'regret_learning') and self.brain.regret_learning:
            self._systems['regret_learning'] = self.brain.regret_learning
            logger.debug("✓ Regret Learning verbunden")

        # =====================================================================
        # 3. ALGORITHMIC COGNITION - Theoretische Informatik
        # =====================================================================
        if hasattr(self.brain, 'algorithmic_cognition') and self.brain.algorithmic_cognition:
            self._systems['algorithmic'] = self.brain.algorithmic_cognition
            logger.debug("✓ Algorithmic Cognition verbunden")

        # =====================================================================
        # 4. COGNITIVE ENHANCEMENT - Erweitertes Denken
        # =====================================================================
        if hasattr(self.brain, 'cognitive_enhancement') and self.brain.cognitive_enhancement:
            self._systems['enhancement'] = self.brain.cognitive_enhancement
            logger.debug("✓ Cognitive Enhancement verbunden")

        # =====================================================================
        # 5. META-COGNITION - Denken über Denken
        # =====================================================================
        if hasattr(self.brain, 'meta_observer') and self.brain.meta_observer:
            self._systems['meta_cognition'] = self.brain.meta_observer
            logger.debug("✓ Meta-Cognition verbunden")

        if hasattr(self.brain, 'sandbox') and self.brain.sandbox:
            self._systems['sandbox'] = self.brain.sandbox
            logger.debug("✓ Sandbox verbunden")

        # =====================================================================
        # 6. CREATIVE MIND - Kreatives Denken
        # =====================================================================
        if hasattr(self.brain, 'creative_mind') and self.brain.creative_mind:
            self._systems['creative'] = self.brain.creative_mind
            logger.debug("✓ Creative Mind verbunden")

        # =====================================================================
        # 7. LEARNING SYSTEM - Lernen
        # =====================================================================
        if hasattr(self.brain, 'learning_system') and self.brain.learning_system:
            self._systems['learning'] = self.brain.learning_system
            logger.debug("✓ Learning System verbunden")
        elif hasattr(self.brain, 'learning_engine') and self.brain.learning_engine:
            self._systems['learning'] = self.brain.learning_engine
            logger.debug("✓ Learning Engine verbunden")

        # =====================================================================
        # 8. SELF-AWARENESS - Selbstwahrnehmung
        # =====================================================================
        if hasattr(self.brain, 'self_awareness') and self.brain.self_awareness:
            self._systems['self_awareness'] = self.brain.self_awareness
            logger.debug("✓ Self-Awareness verbunden")

        # =====================================================================
        # 9. CONTEXT MIND - Kontext-Verständnis
        # =====================================================================
        if hasattr(self.brain, 'context_mind') and self.brain.context_mind:
            self._systems['context'] = self.brain.context_mind
            logger.debug("✓ Context Mind verbunden")

        # =====================================================================
        # 10. COGNITIVE ENGINE - Haupt-Kognition
        # =====================================================================
        if hasattr(self.brain, 'cognitive_engine') and self.brain.cognitive_engine:
            self._systems['cognitive_engine'] = self.brain.cognitive_engine
            logger.debug("✓ Cognitive Engine verbunden")

        logger.info(f"Universal Cognition Hub: {len(self._systems)} Systeme verbunden")

    def reconnect(self):
        """Verbindet alle Systeme neu"""
        self._systems.clear()
        self._connect_all_systems()
        return self.get_status()

    # =========================================================================
    # UNIVERSELLES DENKEN - Nutzt ALLE Systeme
    # =========================================================================

    def think(self, input_text: str,
              thinking_mode: str = "comprehensive",
              max_time_ms: int = 500) -> CognitiveResult:
        """
        Universelles Denken - nutzt ALLE verfügbaren kognitiven Systeme.

        Args:
            input_text: Der Input über den nachgedacht werden soll
            thinking_mode: "quick", "normal", "comprehensive", "deep"
            max_time_ms: Maximale Denkzeit

        Returns:
            CognitiveResult mit allen Gedanken und Einsichten
        """
        start_time = time.time()

        thoughts: List[CognitiveThought] = []
        insights: List[str] = []
        recommendations: List[str] = []
        systems_used: List[str] = []

        # Konfiguration basierend auf Modus
        config = self._get_thinking_config(thinking_mode)

        try:
            # 1. INTUITION - Erste Reaktion (immer)
            if 'intuition' in self._systems and config.get('use_intuition', True):
                intuition_result = self._consult_intuition(input_text)
                if intuition_result:
                    thoughts.append(intuition_result)
                    systems_used.append('intuition')

            # 2. PROBLEM SOLVER - Analytisches Denken
            if 'problem_solver' in self._systems and config.get('use_analysis', True):
                analysis_thoughts = self._consult_problem_solver(input_text)
                thoughts.extend(analysis_thoughts)
                if analysis_thoughts:
                    systems_used.append('problem_solver')

            # 3. HYPOTHESEN - "Was wenn?" (bei normalem+ Modus)
            if 'hypothesis_engine' in self._systems and config.get('use_hypotheses', False):
                hypothesis_thought = self._generate_hypothesis(input_text)
                if hypothesis_thought:
                    thoughts.append(hypothesis_thought)
                    systems_used.append('hypothesis_engine')

            # 4. ANALOGIEN - "Das erinnert mich an..." (bei comprehensive+)
            if 'analogy' in self._systems and config.get('use_analogies', False):
                analogy_thought = self._find_analogies(input_text)
                if analogy_thought:
                    thoughts.append(analogy_thought)
                    systems_used.append('analogy')

            # 5. KREATIVES DENKEN (bei comprehensive+)
            if 'creative' in self._systems and config.get('use_creative', False):
                creative_thought = self._think_creatively(input_text)
                if creative_thought:
                    thoughts.append(creative_thought)
                    systems_used.append('creative')

            # 6. VORHERSAGEN (bei deep)
            if 'prediction' in self._systems and config.get('use_prediction', False):
                prediction_thought = self._make_prediction(input_text)
                if prediction_thought:
                    thoughts.append(prediction_thought)
                    systems_used.append('prediction')

            # 7. SELBST-HINTERFRAGUNG (bei deep)
            if 'self_challenger' in self._systems and config.get('use_self_challenge', False):
                challenge_thought = self._challenge_thoughts(thoughts)
                if challenge_thought:
                    thoughts.append(challenge_thought)
                    systems_used.append('self_challenger')

            # 8. META-KOGNITION - Reflexion über das Denken
            if 'meta_cognition' in self._systems and config.get('use_meta', False):
                meta_thought = self._reflect_on_thinking(thoughts)
                if meta_thought:
                    thoughts.append(meta_thought)
                    systems_used.append('meta_cognition')

            # Extrahiere Insights aus allen Gedanken
            insights = self._extract_insights(thoughts)

            # Generiere Empfehlungen
            recommendations = self._generate_recommendations(thoughts, insights)

        except Exception as e:
            logger.error(f"Universal thinking error: {e}")
            insights.append(f"Fehler beim Denken: {e}")

        # Statistiken aktualisieren
        self.stats["total_thoughts"] += len(thoughts)
        self.stats["systems_invoked"] += len(systems_used)
        self.stats["cross_system_connections"] += len(systems_used) * (len(systems_used) - 1) // 2

        # Speichere Gedanken im Stream
        self._thought_stream.extend(thoughts)
        if len(self._thought_stream) > 100:
            self._thought_stream = self._thought_stream[-50:]

        return CognitiveResult(
            success=len(thoughts) > 0,
            thoughts=thoughts,
            insights=insights,
            recommendations=recommendations,
            thinking_time_ms=int((time.time() - start_time) * 1000),
            systems_used=systems_used,
            metadata={"mode": thinking_mode}
        )

    def _get_thinking_config(self, mode: str) -> Dict:
        """Gibt Konfiguration für Denkmodus zurück"""
        configs = {
            "quick": {
                "use_intuition": True,
                "use_analysis": False,
                "use_hypotheses": False,
                "use_analogies": False,
                "use_creative": False,
                "use_prediction": False,
                "use_self_challenge": False,
                "use_meta": False,
            },
            "normal": {
                "use_intuition": True,
                "use_analysis": True,
                "use_hypotheses": True,
                "use_analogies": False,
                "use_creative": False,
                "use_prediction": False,
                "use_self_challenge": False,
                "use_meta": False,
            },
            "comprehensive": {
                "use_intuition": True,
                "use_analysis": True,
                "use_hypotheses": True,
                "use_analogies": True,
                "use_creative": True,
                "use_prediction": False,
                "use_self_challenge": False,
                "use_meta": False,
            },
            "deep": {
                "use_intuition": True,
                "use_analysis": True,
                "use_hypotheses": True,
                "use_analogies": True,
                "use_creative": True,
                "use_prediction": True,
                "use_self_challenge": True,
                "use_meta": True,
            },
        }
        return configs.get(mode, configs["normal"])

    # =========================================================================
    # SYSTEM-SPEZIFISCHE KONSULTATIONEN
    # =========================================================================

    def _consult_intuition(self, input_text: str) -> Optional[CognitiveThought]:
        """Fragt das Intuitions-System"""
        intuition = self._systems.get('intuition')
        if not intuition:
            return None

        try:
            if hasattr(intuition, 'get_gut_feeling'):
                feeling = intuition.get_gut_feeling(input_text)
                return CognitiveThought(
                    id=f"intuition_{int(time.time()*1000)}",
                    content=feeling.express() if hasattr(feeling, 'express') else str(feeling),
                    source_system="intuition",
                    thought_type="intuition",
                    confidence=feeling.intensity if hasattr(feeling, 'intensity') else 0.5,
                )
            elif hasattr(intuition, 'feel'):
                feeling = intuition.feel(input_text)
                return CognitiveThought(
                    id=f"intuition_{int(time.time()*1000)}",
                    content=str(feeling),
                    source_system="intuition",
                    thought_type="intuition",
                    confidence=0.5,
                )
        except Exception as e:
            logger.debug(f"Intuition error: {e}")

        return None

    def _consult_problem_solver(self, input_text: str) -> List[CognitiveThought]:
        """Fragt den Problem Solver"""
        ps = self._systems.get('problem_solver')
        if not ps:
            return []

        thoughts = []

        try:
            # Erstelle Problem-Objekt
            if hasattr(ps, '_create_problem'):
                problem = ps._create_problem(input_text, {}, [], [])

                # Hypothesen
                if hasattr(ps, 'hypothesis_generator'):
                    hypotheses = ps.hypothesis_generator.generate_hypotheses(problem, {}, count=2)
                    for h in hypotheses[:1]:
                        thoughts.append(CognitiveThought(
                            id=f"hypothesis_{int(time.time()*1000)}",
                            content=h.description,
                            source_system="problem_solver",
                            thought_type="hypothesis",
                            confidence=h.confidence,
                        ))

                # Laterales Denken
                if hasattr(ps, 'lateral_thinking'):
                    ideas = ps.lateral_thinking.think_laterally(problem, techniques=["analogy"])
                    for idea in ideas[:1]:
                        thoughts.append(CognitiveThought(
                            id=f"creative_{int(time.time()*1000)}",
                            content=idea.get('idea', ''),
                            source_system="problem_solver",
                            thought_type="creative_idea",
                            confidence=idea.get('confidence', 0.5),
                        ))

                # Zerlegung bei Komplexität
                if hasattr(ps, 'recursive_decomposer'):
                    decomp = ps.decompose_problem(input_text, max_depth=2)
                    if decomp.get('total_subproblems', 0) > 1:
                        thoughts.append(CognitiveThought(
                            id=f"decomp_{int(time.time()*1000)}",
                            content=f"Problem in {decomp['total_subproblems']} Teile zerlegt",
                            source_system="problem_solver",
                            thought_type="decomposition",
                            confidence=0.8,
                            metadata={"parts": decomp.get('atomic_problems', [])}
                        ))

        except Exception as e:
            logger.debug(f"Problem solver error: {e}")

        return thoughts

    def _generate_hypothesis(self, input_text: str) -> Optional[CognitiveThought]:
        """Generiert eine Hypothese"""
        engine = self._systems.get('hypothesis_engine')
        if not engine:
            return None

        try:
            if hasattr(engine, 'generate_hypothesis'):
                hypothesis = engine.generate_hypothesis(input_text)
                if hypothesis:
                    return CognitiveThought(
                        id=f"hypo_{int(time.time()*1000)}",
                        content=hypothesis.statement if hasattr(hypothesis, 'statement') else str(hypothesis),
                        source_system="hypothesis_engine",
                        thought_type="hypothesis",
                        confidence=hypothesis.confidence if hasattr(hypothesis, 'confidence') else 0.5,
                    )
        except Exception as e:
            logger.debug(f"Hypothesis engine error: {e}")

        return None

    def _find_analogies(self, input_text: str) -> Optional[CognitiveThought]:
        """Findet Analogien"""
        analogy = self._systems.get('analogy')
        if not analogy:
            return None

        try:
            if hasattr(analogy, 'find_analogies'):
                analogies = analogy.find_analogies(input_text)
                if analogies:
                    first = analogies[0] if isinstance(analogies, list) else analogies
                    return CognitiveThought(
                        id=f"analogy_{int(time.time()*1000)}",
                        content=f"Das erinnert mich an: {first}",
                        source_system="analogy",
                        thought_type="analogy",
                        confidence=0.6,
                    )
            elif hasattr(analogy, 'remember_similar'):
                similar = analogy.remember_similar(input_text)
                if similar:
                    return CognitiveThought(
                        id=f"analogy_{int(time.time()*1000)}",
                        content=f"Ähnlich zu: {similar}",
                        source_system="analogy",
                        thought_type="analogy",
                        confidence=0.6,
                    )
        except Exception as e:
            logger.debug(f"Analogy error: {e}")

        return None

    def _think_creatively(self, input_text: str) -> Optional[CognitiveThought]:
        """Kreatives Denken"""
        creative = self._systems.get('creative')
        if not creative:
            return None

        try:
            if hasattr(creative, 'generate_idea'):
                idea = creative.generate_idea(input_text)
                if idea:
                    return CognitiveThought(
                        id=f"creative_{int(time.time()*1000)}",
                        content=str(idea),
                        source_system="creative",
                        thought_type="creative_idea",
                        confidence=0.5,
                    )
            elif hasattr(creative, 'brainstorm'):
                ideas = creative.brainstorm(input_text, count=1)
                if ideas:
                    return CognitiveThought(
                        id=f"creative_{int(time.time()*1000)}",
                        content=ideas[0] if isinstance(ideas, list) else str(ideas),
                        source_system="creative",
                        thought_type="creative_idea",
                        confidence=0.5,
                    )
        except Exception as e:
            logger.debug(f"Creative thinking error: {e}")

        return None

    def _make_prediction(self, input_text: str) -> Optional[CognitiveThought]:
        """Macht eine Vorhersage"""
        prediction = self._systems.get('prediction')
        if not prediction:
            return None

        try:
            if hasattr(prediction, 'predict'):
                pred = prediction.predict(input_text)
                if pred:
                    return CognitiveThought(
                        id=f"pred_{int(time.time()*1000)}",
                        content=str(pred),
                        source_system="prediction",
                        thought_type="prediction",
                        confidence=pred.confidence if hasattr(pred, 'confidence') else 0.5,
                    )
        except Exception as e:
            logger.debug(f"Prediction error: {e}")

        return None

    def _challenge_thoughts(self, thoughts: List[CognitiveThought]) -> Optional[CognitiveThought]:
        """Hinterfragt bisherige Gedanken"""
        challenger = self._systems.get('self_challenger')
        if not challenger or not thoughts:
            return None

        try:
            # Nimm den wichtigsten Gedanken
            main_thought = max(thoughts, key=lambda t: t.confidence)

            if hasattr(challenger, 'challenge'):
                challenge = challenger.challenge(main_thought.content)
                if challenge:
                    return CognitiveThought(
                        id=f"challenge_{int(time.time()*1000)}",
                        content=f"Aber... {challenge}",
                        source_system="self_challenger",
                        thought_type="self_challenge",
                        confidence=0.5,
                    )
        except Exception as e:
            logger.debug(f"Self-challenge error: {e}")

        return None

    def _reflect_on_thinking(self, thoughts: List[CognitiveThought]) -> Optional[CognitiveThought]:
        """Meta-Reflexion über das Denken"""
        meta = self._systems.get('meta_cognition')
        if not meta:
            return None

        try:
            # Analysiere den Denkprozess
            sources = set(t.source_system for t in thoughts)
            avg_confidence = sum(t.confidence for t in thoughts) / max(len(thoughts), 1)

            reflection = f"Ich habe {len(thoughts)} Gedanken aus {len(sources)} Systemen. "
            reflection += f"Durchschnittliche Sicherheit: {avg_confidence:.0%}. "

            if avg_confidence < 0.4:
                reflection += "Ich bin mir unsicher - sollte mehr nachdenken."
            elif avg_confidence > 0.7:
                reflection += "Ich bin ziemlich sicher."

            return CognitiveThought(
                id=f"meta_{int(time.time()*1000)}",
                content=reflection,
                source_system="meta_cognition",
                thought_type="meta_reflection",
                confidence=0.7,
            )
        except Exception as e:
            logger.debug(f"Meta-cognition error: {e}")

        return None

    def _extract_insights(self, thoughts: List[CognitiveThought]) -> List[str]:
        """Extrahiert Einsichten aus Gedanken"""
        insights = []

        for thought in thoughts:
            if thought.confidence > 0.6:
                insights.append(f"[{thought.source_system}] {thought.content[:100]}")

        return insights

    def _generate_recommendations(self, thoughts: List[CognitiveThought],
                                  insights: List[str]) -> List[str]:
        """Generiert Empfehlungen basierend auf Gedanken"""
        recommendations = []

        # Basierend auf Gedanken-Typen
        has_hypothesis = any(t.thought_type == "hypothesis" for t in thoughts)
        has_decomposition = any(t.thought_type == "decomposition" for t in thoughts)
        has_uncertainty = any(t.confidence < 0.4 for t in thoughts)

        if has_decomposition:
            recommendations.append("Problem in Teile zerlegen und einzeln angehen")

        if has_hypothesis:
            recommendations.append("Hypothese testen bevor Schlüsse gezogen werden")

        if has_uncertainty:
            recommendations.append("Mehr Informationen sammeln - hohe Unsicherheit")

        return recommendations

    # =========================================================================
    # ZUGRIFF AUF EINZELNE SYSTEME
    # =========================================================================

    def get_system(self, name: str) -> Optional[Any]:
        """Gibt ein spezifisches System zurück"""
        return self._systems.get(name)

    def has_system(self, name: str) -> bool:
        """Prüft ob ein System verfügbar ist"""
        return name in self._systems

    def get_available_systems(self) -> List[str]:
        """Gibt Liste verfügbarer Systeme zurück"""
        return list(self._systems.keys())

    def get_status(self) -> Dict:
        """Gibt Status des Hubs zurück"""
        return {
            "connected_systems": len(self._systems),
            "available_systems": list(self._systems.keys()),
            "thought_stream_size": len(self._thought_stream),
            "stats": self.stats,
        }

    def get_recent_thoughts(self, count: int = 10) -> List[CognitiveThought]:
        """Gibt die letzten Gedanken zurück"""
        return self._thought_stream[-count:]

    # =========================================================================
    # CROSS-SYSTEM METHODEN - Ein System nutzt ein anderes
    # =========================================================================

    def intuition_about_hypothesis(self, hypothesis: str) -> Optional[Dict]:
        """Fragt die Intuition über eine Hypothese"""
        intuition = self._systems.get('intuition')
        if not intuition:
            return None

        try:
            if hasattr(intuition, 'evaluate'):
                return intuition.evaluate(hypothesis)
            elif hasattr(intuition, 'get_gut_feeling'):
                feeling = intuition.get_gut_feeling(hypothesis)
                return {
                    "feeling": feeling.feeling_type.value if hasattr(feeling, 'feeling_type') else str(feeling),
                    "intensity": feeling.intensity if hasattr(feeling, 'intensity') else 0.5,
                }
        except Exception as e:
            logger.debug(f"Cross-system error: {e}")

        return None

    def analyze_with_all_systems(self, topic: str) -> Dict:
        """Analysiert ein Thema mit ALLEN Systemen"""
        result = {
            "topic": topic,
            "analyses": {},
            "consensus": None,
            "confidence": 0.0,
        }

        for name, system in self._systems.items():
            try:
                if hasattr(system, 'analyze'):
                    result["analyses"][name] = system.analyze(topic)
                elif hasattr(system, 'process'):
                    result["analyses"][name] = system.process(topic)
                elif hasattr(system, 'think'):
                    result["analyses"][name] = system.think(topic)
            except Exception as e:
                result["analyses"][name] = {"error": str(e)}

        # Berechne Konsens
        if result["analyses"]:
            result["confidence"] = len([a for a in result["analyses"].values()
                                       if not isinstance(a, dict) or "error" not in a]) / len(result["analyses"])

        return result

    def learn_from_all_systems(self, experience: str, outcome: bool):
        """Lässt alle lernfähigen Systeme aus einer Erfahrung lernen"""
        learning_systems = ['learning', 'regret_learning', 'intuition', 'analogy']

        for name in learning_systems:
            system = self._systems.get(name)
            if system:
                try:
                    if hasattr(system, 'learn'):
                        system.learn(experience, outcome)
                    elif hasattr(system, 'record_outcome'):
                        system.record_outcome(experience, outcome)
                    elif hasattr(system, 'update_from_experience'):
                        system.update_from_experience(experience, outcome)
                except Exception as e:
                    logger.debug(f"Learning error in {name}: {e}")


# ==================== FACTORY ====================

def create_universal_cognition_hub(holo_brain=None) -> UniversalCognitionHub:
    """Erstellt einen Universal Cognition Hub"""
    return UniversalCognitionHub(holo_brain)


# ==================== TEST ====================

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # Ohne Brain testen
    hub = UniversalCognitionHub()
    print(f"Hub Status: {hub.get_status()}")

    # Denken testen (ohne verbundene Systeme)
    result = hub.think("Wie löse ich ein komplexes Problem?", thinking_mode="quick")
    print(f"Thinking Result: {result}")
