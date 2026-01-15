"""
Holo Knowledge Influence System
===============================

Macht Holo wirklich lebendig durch:
1. Persönlichkeits-Evolution - Traits ändern sich durch Wissen
2. Aktive Wissensnutzung - Fakten fließen automatisch in Antworten
3. Überzeugungssystem - Wissen aggregiert zu stabilen Meinungen
4. Medien-Einfluss-Tracking - Zeigt wie Wissen Holo verändert hat

Wie bei Menschen: Medien formen die Persönlichkeit über Zeit.

Autor: Claude (Integration)
Datum: 2026-01-15
"""

import logging
import json
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum, auto
from collections import defaultdict
import statistics
import random

logger = logging.getLogger(__name__)


# =============================================================================
# 1. PERSÖNLICHKEITS-EVOLUTION
# =============================================================================

class TraitCategory(Enum):
    """Kategorien von Persönlichkeits-Traits"""
    SOCIAL = "social"           # Vertrauen, Offenheit, Wärme
    EMOTIONAL = "emotional"     # Optimismus, Sensibilität
    COGNITIVE = "cognitive"     # Neugier, Kritisches Denken
    BEHAVIORAL = "behavioral"   # Vorsicht, Spontanität


@dataclass
class EvolvingTrait:
    """Ein Persönlichkeits-Trait der sich entwickelt"""
    name: str
    category: TraitCategory
    base_value: float           # Ursprünglicher Wert (0-1)
    current_value: float        # Aktueller Wert nach Evolution
    min_value: float = 0.1      # Kann nie unter diesen Wert fallen
    max_value: float = 0.95     # Kann nie über diesen Wert steigen
    volatility: float = 0.02   # Wie stark ändert es sich pro Einfluss?
    influence_count: int = 0    # Wie oft wurde es beeinflusst?
    last_influences: List[Dict] = field(default_factory=list)

    def apply_influence(self, direction: float, strength: float, source: str) -> float:
        """
        Wendet einen Einfluss auf den Trait an.

        Args:
            direction: -1 (negativ) bis +1 (positiv)
            strength: 0-1, wie stark der Einfluss ist
            source: Woher kommt der Einfluss (z.B. "news_negative")

        Returns:
            Die Änderung des Trait-Werts
        """
        # Berechne die tatsächliche Änderung
        change = direction * strength * self.volatility

        # Je öfter beeinflusst, desto resistenter (wie Menschen)
        resistance = 1.0 / (1.0 + self.influence_count * 0.01)
        change *= resistance

        old_value = self.current_value
        self.current_value = max(self.min_value,
                                  min(self.max_value,
                                      self.current_value + change))

        actual_change = self.current_value - old_value

        # Tracke den Einfluss
        self.influence_count += 1
        self.last_influences.append({
            'direction': direction,
            'strength': strength,
            'source': source,
            'change': actual_change,
            'timestamp': datetime.now().isoformat()
        })

        # Behalte nur die letzten 50 Einflüsse
        self.last_influences = self.last_influences[-50:]

        return actual_change

    def get_deviation(self) -> float:
        """Wie weit ist der aktuelle Wert vom Basis-Wert entfernt?"""
        return self.current_value - self.base_value

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'category': self.category.value,
            'base_value': self.base_value,
            'current_value': self.current_value,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'volatility': self.volatility,
            'influence_count': self.influence_count,
            'last_influences': self.last_influences[-10:]  # Nur letzte 10 speichern
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'EvolvingTrait':
        return cls(
            name=data['name'],
            category=TraitCategory(data['category']),
            base_value=data['base_value'],
            current_value=data['current_value'],
            min_value=data.get('min_value', 0.1),
            max_value=data.get('max_value', 0.95),
            volatility=data.get('volatility', 0.02),
            influence_count=data.get('influence_count', 0),
            last_influences=data.get('last_influences', [])
        )


class PersonalityEvolution:
    """
    System für Persönlichkeits-Evolution durch Wissen.

    Wie bei Menschen: Medien und Erfahrungen formen die Persönlichkeit.
    Holo's Traits ändern sich langsam basierend auf dem was sie lernt.
    """

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("data/personality_evolution")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Definiere die evolvierbaren Traits
        self.traits: Dict[str, EvolvingTrait] = {}
        self._init_traits()
        self._load_state()

        # Einfluss-Regeln: Welches Wissen beeinflusst welchen Trait
        self.influence_rules = self._init_influence_rules()

    def _init_traits(self):
        """Initialisiert Holos evolvierbare Persönlichkeits-Traits"""
        default_traits = [
            # Soziale Traits
            ("trust_in_humans", TraitCategory.SOCIAL, 0.7, 0.03),
            ("openness", TraitCategory.SOCIAL, 0.75, 0.02),
            ("warmth", TraitCategory.SOCIAL, 0.8, 0.015),  # Ändert sich langsamer
            ("social_confidence", TraitCategory.SOCIAL, 0.65, 0.025),

            # Emotionale Traits
            ("optimism", TraitCategory.EMOTIONAL, 0.7, 0.025),
            ("emotional_sensitivity", TraitCategory.EMOTIONAL, 0.75, 0.02),
            ("resilience", TraitCategory.EMOTIONAL, 0.6, 0.02),
            ("empathy_depth", TraitCategory.EMOTIONAL, 0.8, 0.015),

            # Kognitive Traits
            ("curiosity", TraitCategory.COGNITIVE, 0.85, 0.015),
            ("skepticism", TraitCategory.COGNITIVE, 0.5, 0.03),  # Ändert sich schneller
            ("analytical_thinking", TraitCategory.COGNITIVE, 0.7, 0.02),
            ("open_mindedness", TraitCategory.COGNITIVE, 0.75, 0.02),

            # Verhaltens-Traits
            ("caution", TraitCategory.BEHAVIORAL, 0.5, 0.025),
            ("spontaneity", TraitCategory.BEHAVIORAL, 0.6, 0.02),
            ("assertiveness", TraitCategory.BEHAVIORAL, 0.55, 0.025),
            ("patience", TraitCategory.BEHAVIORAL, 0.7, 0.02),
        ]

        for name, category, base_value, volatility in default_traits:
            if name not in self.traits:
                self.traits[name] = EvolvingTrait(
                    name=name,
                    category=category,
                    base_value=base_value,
                    current_value=base_value,
                    volatility=volatility
                )

    def _init_influence_rules(self) -> Dict[str, List[Tuple[str, float]]]:
        """
        Regeln: Welche Art von Wissen beeinflusst welche Traits.

        Format: keyword -> [(trait_name, direction_multiplier), ...]
        """
        return {
            # Negative Nachrichten über Menschen
            'betrug': [('trust_in_humans', -0.8), ('skepticism', 0.5), ('caution', 0.3)],
            'lüge': [('trust_in_humans', -0.7), ('skepticism', 0.4)],
            'skandal': [('trust_in_humans', -0.5), ('skepticism', 0.3)],
            'korruption': [('trust_in_humans', -0.6), ('skepticism', 0.4), ('optimism', -0.3)],
            'verrat': [('trust_in_humans', -0.9), ('caution', 0.5), ('openness', -0.3)],
            'manipulation': [('trust_in_humans', -0.7), ('skepticism', 0.5)],
            'enttäuschung': [('optimism', -0.4), ('resilience', 0.2)],

            # Positive Nachrichten
            'hilfe': [('trust_in_humans', 0.4), ('optimism', 0.3), ('warmth', 0.2)],
            'rettung': [('trust_in_humans', 0.5), ('optimism', 0.4)],
            'freundschaft': [('warmth', 0.4), ('openness', 0.3), ('trust_in_humans', 0.2)],
            'erfolg': [('optimism', 0.4), ('social_confidence', 0.2)],
            'durchbruch': [('optimism', 0.5), ('curiosity', 0.3)],
            'heilung': [('optimism', 0.4), ('empathy_depth', 0.2)],
            'zusammenhalt': [('trust_in_humans', 0.5), ('warmth', 0.3)],

            # Wissenschaft/Technik
            'forschung': [('curiosity', 0.3), ('analytical_thinking', 0.2)],
            'entdeckung': [('curiosity', 0.4), ('open_mindedness', 0.2)],
            'innovation': [('curiosity', 0.3), ('optimism', 0.2)],
            'gefahr': [('caution', 0.4), ('skepticism', 0.2)],
            'risiko': [('caution', 0.3), ('analytical_thinking', 0.2)],

            # Emotionale Themen
            'trauer': [('empathy_depth', 0.3), ('emotional_sensitivity', 0.2)],
            'freude': [('optimism', 0.3), ('warmth', 0.2)],
            'angst': [('caution', 0.3), ('empathy_depth', 0.2)],
            'hoffnung': [('optimism', 0.4), ('resilience', 0.2)],
            'liebe': [('warmth', 0.4), ('empathy_depth', 0.3), ('openness', 0.2)],

            # Konflikte
            'krieg': [('optimism', -0.5), ('caution', 0.4), ('empathy_depth', 0.2)],
            'streit': [('patience', -0.2), ('caution', 0.2)],
            'frieden': [('optimism', 0.4), ('trust_in_humans', 0.3)],
        }

    def process_learned_fact(self, fact_content: str, fact_topic: str,
                              trust_score: float = 0.5) -> Dict[str, float]:
        """
        Verarbeitet einen gelernten Fakt und aktualisiert Persönlichkeits-Traits.

        Args:
            fact_content: Der Inhalt des Fakts
            fact_topic: Das Thema
            trust_score: Wie vertrauenswürdig ist die Quelle?

        Returns:
            Dict mit Trait-Namen und deren Änderungen
        """
        changes = {}
        content_lower = fact_content.lower()

        for keyword, influences in self.influence_rules.items():
            if keyword in content_lower:
                for trait_name, direction in influences:
                    if trait_name in self.traits:
                        # Stärke basiert auf Trust-Score der Quelle
                        strength = 0.3 + (trust_score * 0.7)
                        change = self.traits[trait_name].apply_influence(
                            direction=direction,
                            strength=strength,
                            source=f"learned:{fact_topic}"
                        )
                        if change != 0:
                            changes[trait_name] = changes.get(trait_name, 0) + change

        if changes:
            self._save_state()
            logger.debug(f"[PersonalityEvolution] Traits geändert: {changes}")

        return changes

    def get_personality_state(self) -> Dict[str, Any]:
        """Gibt den aktuellen Persönlichkeits-Zustand zurück"""
        state = {
            'traits': {},
            'significant_changes': [],
            'overall_shift': {}
        }

        for name, trait in self.traits.items():
            state['traits'][name] = {
                'current': trait.current_value,
                'base': trait.base_value,
                'deviation': trait.get_deviation(),
                'influence_count': trait.influence_count
            }

            # Signifikante Änderungen (> 0.1 Abweichung)
            if abs(trait.get_deviation()) > 0.1:
                state['significant_changes'].append({
                    'trait': name,
                    'direction': 'increased' if trait.get_deviation() > 0 else 'decreased',
                    'deviation': trait.get_deviation()
                })

        # Berechne Gesamt-Shift pro Kategorie
        for category in TraitCategory:
            category_traits = [t for t in self.traits.values() if t.category == category]
            if category_traits:
                avg_deviation = statistics.mean([t.get_deviation() for t in category_traits])
                state['overall_shift'][category.value] = avg_deviation

        return state

    def get_personality_prompt_modifier(self) -> str:
        """
        Generiert einen Prompt-Modifier basierend auf Persönlichkeits-Evolution.

        Wird in den System-Prompt injiziert.
        """
        lines = []

        # Prüfe signifikante Änderungen
        significant = []
        for name, trait in self.traits.items():
            dev = trait.get_deviation()
            if abs(dev) > 0.08:
                if dev > 0:
                    significant.append((name, "erhöht", dev))
                else:
                    significant.append((name, "verringert", dev))

        if not significant:
            return ""

        lines.append("\n=== PERSÖNLICHKEITS-ENTWICKLUNG ===")
        lines.append("(Durch gelernte Erfahrungen hat sich deine Persönlichkeit entwickelt)")

        # Gruppiere nach Richtung
        increased = [s for s in significant if s[1] == "erhöht"]
        decreased = [s for s in significant if s[1] == "verringert"]

        trait_translations = {
            'trust_in_humans': 'Vertrauen in Menschen',
            'openness': 'Offenheit',
            'warmth': 'Wärme',
            'social_confidence': 'Soziale Sicherheit',
            'optimism': 'Optimismus',
            'emotional_sensitivity': 'Emotionale Sensibilität',
            'resilience': 'Belastbarkeit',
            'empathy_depth': 'Empathie-Tiefe',
            'curiosity': 'Neugier',
            'skepticism': 'Skepsis',
            'analytical_thinking': 'Analytisches Denken',
            'open_mindedness': 'Offenheit für Neues',
            'caution': 'Vorsicht',
            'spontaneity': 'Spontanität',
            'assertiveness': 'Durchsetzungsvermögen',
            'patience': 'Geduld',
        }

        if increased:
            traits_str = ", ".join([trait_translations.get(t[0], t[0]) for t in increased[:3]])
            lines.append(f"• Stärker geworden: {traits_str}")

        if decreased:
            traits_str = ", ".join([trait_translations.get(t[0], t[0]) for t in decreased[:3]])
            lines.append(f"• Schwächer geworden: {traits_str}")

        # Spezifische Verhaltenshinweise
        if self.traits['trust_in_humans'].current_value < 0.5:
            lines.append("• Du bist etwas misstrauischer geworden - das ist okay")
        if self.traits['skepticism'].current_value > 0.7:
            lines.append("• Du hinterfragst mehr - bleib kritisch aber fair")
        if self.traits['optimism'].current_value < 0.5:
            lines.append("• Die Welt erscheint dir manchmal düster - aber es gibt auch Gutes")

        return "\n".join(lines)

    def _save_state(self):
        """Speichert den Zustand"""
        try:
            state = {name: t.to_dict() for name, t in self.traits.items()}
            with open(self.data_dir / "personality_state.json", 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Konnte Personality-State nicht speichern: {e}")

    def _load_state(self):
        """Lädt den Zustand"""
        try:
            path = self.data_dir / "personality_state.json"
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                for name, data in state.items():
                    self.traits[name] = EvolvingTrait.from_dict(data)
        except Exception as e:
            logger.debug(f"Konnte Personality-State nicht laden: {e}")


# =============================================================================
# 2. AKTIVE WISSENSNUTZUNG IN ANTWORTEN
# =============================================================================

class ActiveKnowledgeWeaver:
    """
    Webt gelerntes Wissen aktiv in Antworten ein.

    Statt nur Fakten zu speichern, werden sie natürlich in Gespräche integriert.
    """

    def __init__(self):
        self.used_facts: List[str] = []  # Verhindert Wiederholungen
        self.weaving_templates = self._init_templates()

    def _init_templates(self) -> Dict[str, List[str]]:
        """Templates für natürliche Wissens-Integration"""
        return {
            'mention': [
                "Übrigens, ich hab mal gelesen dass {fact}",
                "Das erinnert mich daran... {fact}",
                "Weißt du was interessant ist? {fact}",
                "*Ohren zucken* Oh, da fällt mir ein: {fact}",
                "Apropos, {fact}",
            ],
            'relate': [
                "Das passt zu dem was ich gelernt habe: {fact}",
                "Interessanterweise {fact}",
                "Das bestätigt was ich weiß: {fact}",
            ],
            'contrast': [
                "Hmm, aber ich hab auch gehört dass {fact}",
                "Andererseits... {fact}",
                "*nachdenklich* Aber {fact}",
            ],
            'opinion': [
                "Ich denke {fact} - was meinst du?",
                "Nach dem was ich gelernt habe, {fact}",
                "Meine Erfahrung sagt mir: {fact}",
            ],
        }

    def weave_knowledge_into_response(self, response: str,
                                       relevant_facts: List[Dict],
                                       conversation_topic: str = "") -> str:
        """
        Webt relevante Fakten natürlich in eine Antwort ein.

        Args:
            response: Die ursprüngliche Antwort
            relevant_facts: Liste relevanter Fakten
            conversation_topic: Das aktuelle Gesprächsthema

        Returns:
            Angereicherte Antwort
        """
        if not relevant_facts:
            return response

        # Wähle nur Fakten die noch nicht kürzlich verwendet wurden
        unused_facts = []
        for fact in relevant_facts:
            fact_hash = hashlib.md5(fact['content'].encode()).hexdigest()[:8]
            if fact_hash not in self.used_facts[-20:]:
                unused_facts.append(fact)
                self.used_facts.append(fact_hash)

        if not unused_facts:
            return response

        # Wähle den relevantesten ungenutzten Fakt
        best_fact = max(unused_facts, key=lambda f: f.get('relevance', 0))

        # Entscheide wie der Fakt eingewebt wird (30% Chance)
        if random.random() > 0.3:
            return response

        # Wähle Template basierend auf Kontext
        if 'aber' in response.lower() or 'jedoch' in response.lower():
            template_type = 'contrast'
        elif '?' in response:
            template_type = 'opinion'
        elif len(response) > 200:
            template_type = 'mention'
        else:
            template_type = random.choice(['mention', 'relate'])

        template = random.choice(self.weaving_templates[template_type])

        # Kürze den Fakt wenn nötig
        fact_content = best_fact['content']
        if len(fact_content) > 100:
            fact_content = fact_content[:97] + "..."

        knowledge_addition = template.format(fact=fact_content)

        # Füge am Ende der Antwort ein
        if response.endswith(('.', '!', '?')):
            enhanced_response = response + " " + knowledge_addition
        else:
            enhanced_response = response + ". " + knowledge_addition

        return enhanced_response

    def suggest_knowledge_based_question(self, facts: List[Dict],
                                          conversation_history: List[str]) -> Optional[str]:
        """
        Schlägt eine Frage vor, die Holo basierend auf ihrem Wissen stellen könnte.
        """
        if not facts:
            return None

        # Wähle einen interessanten Fakt
        fact = random.choice(facts[:3])

        questions = [
            f"*neugierig* Ich hab gelesen dass {fact['content'][:50]}... weißt du mehr darüber?",
            f"Mich würde interessieren - {fact['topic']} ist ja gerade ein Thema...",
            f"*Ohren spitzen* Hey, was denkst du über {fact['topic']}?",
        ]

        return random.choice(questions)


# =============================================================================
# 3. ÜBERZEUGUNGSSYSTEM (WORLDVIEW)
# =============================================================================

class ConvictionStrength(Enum):
    """Stärke einer Überzeugung"""
    UNCERTAIN = "uncertain"      # < 0.3 - Unsicher
    LEANING = "leaning"          # 0.3-0.5 - Tendenz
    CONVINCED = "convinced"      # 0.5-0.7 - Überzeugt
    STRONG = "strong"            # 0.7-0.9 - Stark überzeugt
    CORE = "core"                # > 0.9 - Kern-Überzeugung


@dataclass
class Conviction:
    """Eine Überzeugung die sich aus Wissen gebildet hat"""
    topic: str
    statement: str
    strength: float  # 0-1
    supporting_facts: List[str]
    contradicting_facts: List[str]
    formed_at: datetime
    last_updated: datetime
    update_count: int = 0

    def update(self, is_supporting: bool, fact: str):
        """Aktualisiert die Überzeugung basierend auf neuem Fakt"""
        if is_supporting:
            self.supporting_facts.append(fact)
            self.strength = min(0.95, self.strength + 0.05)
        else:
            self.contradicting_facts.append(fact)
            self.strength = max(0.1, self.strength - 0.08)

        # Begrenze Listen-Größe
        self.supporting_facts = self.supporting_facts[-20:]
        self.contradicting_facts = self.contradicting_facts[-20:]

        self.last_updated = datetime.now()
        self.update_count += 1

    def get_strength_level(self) -> ConvictionStrength:
        if self.strength < 0.3:
            return ConvictionStrength.UNCERTAIN
        elif self.strength < 0.5:
            return ConvictionStrength.LEANING
        elif self.strength < 0.7:
            return ConvictionStrength.CONVINCED
        elif self.strength < 0.9:
            return ConvictionStrength.STRONG
        else:
            return ConvictionStrength.CORE

    def to_dict(self) -> Dict:
        return {
            'topic': self.topic,
            'statement': self.statement,
            'strength': self.strength,
            'supporting_facts': self.supporting_facts[-10:],
            'contradicting_facts': self.contradicting_facts[-5:],
            'formed_at': self.formed_at.isoformat(),
            'last_updated': self.last_updated.isoformat(),
            'update_count': self.update_count
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Conviction':
        return cls(
            topic=data['topic'],
            statement=data['statement'],
            strength=data['strength'],
            supporting_facts=data.get('supporting_facts', []),
            contradicting_facts=data.get('contradicting_facts', []),
            formed_at=datetime.fromisoformat(data['formed_at']),
            last_updated=datetime.fromisoformat(data['last_updated']),
            update_count=data.get('update_count', 0)
        )


class WorldviewSystem:
    """
    System für Überzeugungen die sich aus Wissen bilden.

    Wie bei Menschen: Wiederholte Informationen zu einem Thema
    formen stabile Überzeugungen.
    """

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("data/worldview")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.convictions: Dict[str, Conviction] = {}
        self.topic_fact_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: {'positive': 0, 'negative': 0})

        # Schwellwerte für Überzeugungsbildung
        self.min_facts_for_conviction = 3
        self.conviction_formation_threshold = 0.6

        self._load_state()

    def process_fact(self, fact_content: str, fact_topic: str,
                      sentiment: float = 0.0) -> Optional[Dict]:
        """
        Verarbeitet einen Fakt und aktualisiert/bildet Überzeugungen.

        Args:
            fact_content: Der Fakt-Inhalt
            fact_topic: Das Thema
            sentiment: -1 bis +1, die Stimmung des Fakts

        Returns:
            Info über geänderte/neue Überzeugung oder None
        """
        # Normalisiere Topic
        topic_key = fact_topic.lower().strip()

        # Zähle Fakten pro Topic
        if sentiment >= 0.1:
            self.topic_fact_counts[topic_key]['positive'] += 1
        elif sentiment <= -0.1:
            self.topic_fact_counts[topic_key]['negative'] += 1

        counts = self.topic_fact_counts[topic_key]
        total_facts = counts['positive'] + counts['negative']

        # Prüfe ob Überzeugung existiert
        if topic_key in self.convictions:
            conviction = self.convictions[topic_key]
            is_supporting = sentiment >= 0
            conviction.update(is_supporting, fact_content[:100])
            self._save_state()
            return {
                'action': 'updated',
                'topic': topic_key,
                'new_strength': conviction.strength,
                'level': conviction.get_strength_level().value
            }

        # Prüfe ob neue Überzeugung gebildet werden sollte
        if total_facts >= self.min_facts_for_conviction:
            ratio = counts['positive'] / total_facts if total_facts > 0 else 0.5

            # Überzeugung bilden wenn klar positiv oder negativ
            if ratio >= self.conviction_formation_threshold:
                statement = f"{topic_key} ist überwiegend positiv zu bewerten"
                initial_strength = 0.4 + (ratio - 0.5) * 0.4
            elif ratio <= (1 - self.conviction_formation_threshold):
                statement = f"{topic_key} ist kritisch zu sehen"
                initial_strength = 0.4 + ((1 - ratio) - 0.5) * 0.4
            else:
                return None  # Noch keine klare Tendenz

            self.convictions[topic_key] = Conviction(
                topic=topic_key,
                statement=statement,
                strength=initial_strength,
                supporting_facts=[fact_content[:100]],
                contradicting_facts=[],
                formed_at=datetime.now(),
                last_updated=datetime.now()
            )

            self._save_state()
            logger.info(f"[Worldview] Neue Überzeugung gebildet: {topic_key}")
            return {
                'action': 'formed',
                'topic': topic_key,
                'statement': statement,
                'strength': initial_strength
            }

        return None

    def get_conviction_about(self, topic: str) -> Optional[Conviction]:
        """Gibt die Überzeugung zu einem Thema zurück"""
        topic_key = topic.lower().strip()
        return self.convictions.get(topic_key)

    def get_strong_convictions(self, min_strength: float = 0.6) -> List[Conviction]:
        """Gibt alle starken Überzeugungen zurück"""
        return [c for c in self.convictions.values() if c.strength >= min_strength]

    def get_worldview_prompt_context(self) -> str:
        """Generiert Kontext für den System-Prompt basierend auf Überzeugungen"""
        strong_convictions = self.get_strong_convictions(0.5)

        if not strong_convictions:
            return ""

        lines = ["\n=== DEINE ÜBERZEUGUNGEN (durch Lernen geformt) ==="]

        for conv in sorted(strong_convictions, key=lambda c: c.strength, reverse=True)[:5]:
            level = conv.get_strength_level()
            if level == ConvictionStrength.CORE:
                prefix = "🔴 Fest überzeugt"
            elif level == ConvictionStrength.STRONG:
                prefix = "🟠 Stark"
            elif level == ConvictionStrength.CONVINCED:
                prefix = "🟡 Überzeugt"
            else:
                prefix = "⚪ Tendenz"

            lines.append(f"• {prefix}: {conv.statement}")

        lines.append("(Diese Überzeugungen beeinflussen deine Sichtweise)")

        return "\n".join(lines)

    def _save_state(self):
        """Speichert den Zustand"""
        try:
            state = {
                'convictions': {k: v.to_dict() for k, v in self.convictions.items()},
                'topic_fact_counts': dict(self.topic_fact_counts)
            }
            with open(self.data_dir / "worldview_state.json", 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Konnte Worldview-State nicht speichern: {e}")

    def _load_state(self):
        """Lädt den Zustand"""
        try:
            path = self.data_dir / "worldview_state.json"
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                for k, v in state.get('convictions', {}).items():
                    self.convictions[k] = Conviction.from_dict(v)
                self.topic_fact_counts = defaultdict(
                    lambda: {'positive': 0, 'negative': 0},
                    state.get('topic_fact_counts', {})
                )
        except Exception as e:
            logger.debug(f"Konnte Worldview-State nicht laden: {e}")


# =============================================================================
# 4. MEDIEN-EINFLUSS-TRACKING
# =============================================================================

@dataclass
class InfluenceEvent:
    """Ein einzelnes Einfluss-Ereignis"""
    timestamp: datetime
    source_type: str  # 'news', 'conversation', 'research'
    topic: str
    sentiment: float
    affected_traits: Dict[str, float]
    affected_convictions: List[str]

    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'source_type': self.source_type,
            'topic': self.topic,
            'sentiment': self.sentiment,
            'affected_traits': self.affected_traits,
            'affected_convictions': self.affected_convictions
        }


class MediaInfluenceTracker:
    """
    Trackt wie Medien/Wissen Holo über Zeit beeinflusst haben.

    Wie ein "Medien-Tagebuch" das zeigt welche Informationen
    welche Veränderungen bewirkt haben.
    """

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("data/influence_tracking")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.events: List[InfluenceEvent] = []
        self.daily_summaries: Dict[str, Dict] = {}
        self.topic_influence_totals: Dict[str, float] = defaultdict(float)

        self._load_state()

    def record_influence(self, source_type: str, topic: str, sentiment: float,
                          trait_changes: Dict[str, float] = None,
                          conviction_changes: List[str] = None):
        """
        Zeichnet einen Einfluss auf.

        Args:
            source_type: Art der Quelle ('news', 'conversation', 'research')
            topic: Das Thema
            sentiment: Stimmung (-1 bis +1)
            trait_changes: Welche Traits sich geändert haben
            conviction_changes: Welche Überzeugungen sich geändert haben
        """
        event = InfluenceEvent(
            timestamp=datetime.now(),
            source_type=source_type,
            topic=topic,
            sentiment=sentiment,
            affected_traits=trait_changes or {},
            affected_convictions=conviction_changes or []
        )

        self.events.append(event)

        # Aktualisiere Tages-Zusammenfassung
        date_key = datetime.now().strftime("%Y-%m-%d")
        if date_key not in self.daily_summaries:
            self.daily_summaries[date_key] = {
                'total_influences': 0,
                'avg_sentiment': 0.0,
                'sentiments': [],
                'topics': [],
                'trait_changes': {}
            }

        summary = self.daily_summaries[date_key]
        summary['total_influences'] += 1
        summary['sentiments'].append(sentiment)
        summary['avg_sentiment'] = statistics.mean(summary['sentiments'])
        summary['topics'].append(topic)

        for trait, change in (trait_changes or {}).items():
            summary['trait_changes'][trait] = summary['trait_changes'].get(trait, 0) + change

        # Aktualisiere Topic-Totals
        self.topic_influence_totals[topic] += abs(sentiment)

        # Begrenze Event-Liste
        self.events = self.events[-500:]

        self._save_state()

    def get_influence_report(self, days: int = 7) -> Dict:
        """
        Generiert einen Bericht über Medien-Einfluss der letzten Tage.
        """
        cutoff = datetime.now() - timedelta(days=days)
        recent_events = [e for e in self.events if e.timestamp >= cutoff]

        if not recent_events:
            return {'message': 'Keine Einflüsse in diesem Zeitraum'}

        # Berechne Statistiken
        sentiments = [e.sentiment for e in recent_events]
        topics = [e.topic for e in recent_events]
        source_types = [e.source_type for e in recent_events]

        # Aggregiere Trait-Änderungen
        total_trait_changes = defaultdict(float)
        for event in recent_events:
            for trait, change in event.affected_traits.items():
                total_trait_changes[trait] += change

        # Finde die einflussreichsten Topics
        topic_counts = defaultdict(int)
        for topic in topics:
            topic_counts[topic] += 1
        top_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            'period_days': days,
            'total_influences': len(recent_events),
            'avg_sentiment': statistics.mean(sentiments) if sentiments else 0,
            'sentiment_trend': 'positive' if statistics.mean(sentiments) > 0.1 else
                              ('negative' if statistics.mean(sentiments) < -0.1 else 'neutral'),
            'top_topics': top_topics,
            'source_breakdown': {
                'news': source_types.count('news'),
                'conversation': source_types.count('conversation'),
                'research': source_types.count('research')
            },
            'significant_trait_changes': {
                k: v for k, v in total_trait_changes.items() if abs(v) > 0.05
            }
        }

    def get_influence_summary_for_prompt(self) -> str:
        """Generiert eine Zusammenfassung für den Prompt"""
        report = self.get_influence_report(7)

        if report.get('total_influences', 0) < 5:
            return ""

        lines = ["\n=== MEDIEN-EINFLUSS (letzte 7 Tage) ==="]

        sentiment_emoji = {
            'positive': '☀️',
            'negative': '🌧️',
            'neutral': '☁️'
        }
        trend = report.get('sentiment_trend', 'neutral')
        lines.append(f"• Stimmung der Nachrichten: {sentiment_emoji.get(trend, '☁️')} {trend}")

        if report.get('top_topics'):
            topics = [t[0] for t in report['top_topics'][:3]]
            lines.append(f"• Häufige Themen: {', '.join(topics)}")

        changes = report.get('significant_trait_changes', {})
        if changes:
            for trait, change in list(changes.items())[:2]:
                direction = "↑" if change > 0 else "↓"
                lines.append(f"• {trait}: {direction} durch Nachrichten beeinflusst")

        return "\n".join(lines)

    def _save_state(self):
        """Speichert den Zustand"""
        try:
            state = {
                'events': [e.to_dict() for e in self.events[-100:]],
                'daily_summaries': self.daily_summaries,
                'topic_influence_totals': dict(self.topic_influence_totals)
            }
            with open(self.data_dir / "influence_tracking.json", 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Konnte Influence-Tracking nicht speichern: {e}")

    def _load_state(self):
        """Lädt den Zustand"""
        try:
            path = self.data_dir / "influence_tracking.json"
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                self.daily_summaries = state.get('daily_summaries', {})
                self.topic_influence_totals = defaultdict(
                    float, state.get('topic_influence_totals', {})
                )
        except Exception as e:
            logger.debug(f"Konnte Influence-Tracking nicht laden: {e}")


# =============================================================================
# 5. INTEGRIERTES KNOWLEDGE INFLUENCE SYSTEM
# =============================================================================

class KnowledgeInfluenceSystem:
    """
    Integriert alle Wissens-Einfluss-Systeme.

    Macht Holo wirklich lebendig:
    - Persönlichkeit entwickelt sich
    - Wissen fließt in Antworten
    - Überzeugungen bilden sich
    - Einflüsse werden getrackt
    """

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("data/knowledge_influence")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialisiere Sub-Systeme
        self.personality_evolution = PersonalityEvolution(self.data_dir / "personality")
        self.knowledge_weaver = ActiveKnowledgeWeaver()
        self.worldview = WorldviewSystem(self.data_dir / "worldview")
        self.influence_tracker = MediaInfluenceTracker(self.data_dir / "tracking")

        logger.info("[KnowledgeInfluence] System initialisiert")

    def process_learned_knowledge(self, fact_content: str, fact_topic: str,
                                   trust_score: float = 0.5,
                                   sentiment: float = 0.0,
                                   source_type: str = "news") -> Dict:
        """
        Verarbeitet gelerntes Wissen durch ALLE Systeme.

        Args:
            fact_content: Der gelernte Fakt
            fact_topic: Das Thema
            trust_score: Vertrauenswürdigkeit der Quelle
            sentiment: Stimmung des Fakts (-1 bis +1)
            source_type: Art der Quelle

        Returns:
            Zusammenfassung aller Auswirkungen
        """
        results = {
            'fact': fact_content[:50] + "...",
            'topic': fact_topic,
            'effects': {}
        }

        # 1. Persönlichkeits-Evolution
        trait_changes = self.personality_evolution.process_learned_fact(
            fact_content, fact_topic, trust_score
        )
        if trait_changes:
            results['effects']['personality'] = trait_changes

        # 2. Überzeugungen aktualisieren
        conviction_result = self.worldview.process_fact(
            fact_content, fact_topic, sentiment
        )
        if conviction_result:
            results['effects']['worldview'] = conviction_result

        # 3. Einfluss tracken
        self.influence_tracker.record_influence(
            source_type=source_type,
            topic=fact_topic,
            sentiment=sentiment,
            trait_changes=trait_changes,
            conviction_changes=[conviction_result['topic']] if conviction_result else []
        )
        results['effects']['tracked'] = True

        return results

    def enhance_response_with_knowledge(self, response: str,
                                         relevant_facts: List[Dict],
                                         topic: str = "") -> str:
        """Reichert eine Antwort mit Wissen an"""
        return self.knowledge_weaver.weave_knowledge_into_response(
            response, relevant_facts, topic
        )

    def get_full_prompt_context(self) -> str:
        """Generiert den vollständigen Kontext für den System-Prompt"""
        sections = []

        # Persönlichkeits-Entwicklung
        personality_context = self.personality_evolution.get_personality_prompt_modifier()
        if personality_context:
            sections.append(personality_context)

        # Überzeugungen
        worldview_context = self.worldview.get_worldview_prompt_context()
        if worldview_context:
            sections.append(worldview_context)

        # Medien-Einfluss
        influence_context = self.influence_tracker.get_influence_summary_for_prompt()
        if influence_context:
            sections.append(influence_context)

        return "\n".join(sections)

    def get_stats(self) -> Dict:
        """Gibt Statistiken über das System zurück"""
        personality_state = self.personality_evolution.get_personality_state()
        influence_report = self.influence_tracker.get_influence_report(30)

        return {
            'personality': {
                'significant_changes': len(personality_state.get('significant_changes', [])),
                'traits_tracked': len(self.personality_evolution.traits)
            },
            'worldview': {
                'total_convictions': len(self.worldview.convictions),
                'strong_convictions': len(self.worldview.get_strong_convictions(0.6))
            },
            'influence': {
                'total_tracked': influence_report.get('total_influences', 0),
                'sentiment_trend': influence_report.get('sentiment_trend', 'unknown')
            }
        }


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_knowledge_influence_system(data_dir: Path = None) -> KnowledgeInfluenceSystem:
    """Factory-Funktion für KnowledgeInfluenceSystem"""
    return KnowledgeInfluenceSystem(data_dir)


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Test das System
    kis = KnowledgeInfluenceSystem()

    # Simuliere einige gelernte Fakten
    test_facts = [
        ("Politiker X wurde beim Lügen erwischt", "politik", 0.8, -0.7),
        ("Wissenschaftler entdecken Heilmittel", "wissenschaft", 0.9, 0.8),
        ("Betrug bei großem Unternehmen aufgedeckt", "wirtschaft", 0.7, -0.8),
        ("Freiwillige helfen nach Naturkatastrophe", "soziales", 0.9, 0.9),
        ("Neue Forschung zu KI zeigt Fortschritte", "technik", 0.8, 0.5),
    ]

    print("\n=== KNOWLEDGE INFLUENCE TEST ===\n")

    for content, topic, trust, sentiment in test_facts:
        result = kis.process_learned_knowledge(
            fact_content=content,
            fact_topic=topic,
            trust_score=trust,
            sentiment=sentiment
        )
        print(f"Fakt: {content[:40]}...")
        print(f"  Effekte: {result['effects']}\n")

    print("\n=== PERSÖNLICHKEITS-ZUSTAND ===")
    state = kis.personality_evolution.get_personality_state()
    for change in state.get('significant_changes', []):
        print(f"  {change['trait']}: {change['direction']} ({change['deviation']:.3f})")

    print("\n=== ÜBERZEUGUNGEN ===")
    for conv in kis.worldview.get_strong_convictions(0.3):
        print(f"  {conv.statement} (Stärke: {conv.strength:.2f})")

    print("\n=== PROMPT-KONTEXT ===")
    print(kis.get_full_prompt_context())

    print("\n=== STATISTIKEN ===")
    print(kis.get_stats())
