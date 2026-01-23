#!/usr/bin/env python3
"""
HOLO CURIOSITY-DRIVEN LEARNING SYSTEM v1.0

Neugier-gesteuertes Lernen speziell fuer Holos Charakter:
- Wolfs-basierte Instinkte fuer Wissensjagd
- Emotionale Neugier-Reaktionen
- Interesse-Entdeckung durch Exploration
- Wissens-Beute und Sammel-Instinkt
- Natuerliche Lern-Motivation

Autor: Claude (Integration)
Datum: 2026-01-23
"""

import logging
import json
import random
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum, auto
from collections import defaultdict

logger = logging.getLogger(__name__)


# =============================================================================
# 1. WISSENSJAGD-SYSTEM (WOLF-INSTINKTE)
# =============================================================================

class HuntingPhase(Enum):
    """Phasen der Wissensjagd (wie Wolfsverhalten)"""
    RESTING = "resting"           # Ruhe, kein aktives Lernen
    SNIFFING = "sniffing"         # Schnueffeln nach interessanten Themen
    TRACKING = "tracking"         # Ein Thema verfolgen
    STALKING = "stalking"         # Sich an tiefes Wissen heranpirschen
    POUNCING = "pouncing"         # Aktives Erfassen von Wissen
    FEASTING = "feasting"         # Wissen "verdauen" und integrieren
    SATISFIED = "satisfied"       # Zufrieden nach erfolgreichem Lernen


@dataclass
class KnowledgePrey:
    """Ein 'Wissens-Beutestueck' das Holo jagt"""
    prey_id: str
    topic: str
    description: str
    difficulty: float  # 0-1, wie schwer zu "fangen"
    value: float       # 0-1, wie wertvoll
    discovered_at: datetime
    captured: bool = False
    captured_at: Optional[datetime] = None
    hunt_attempts: int = 0
    related_prey: List[str] = field(default_factory=list)


class WolfKnowledgeHunter:
    """
    Wissensjagd-System mit Wolf-Instinkten.

    Holo 'jagt' Wissen wie ein Wolf Beute:
    - Schnueffelt nach interessanten Themen
    - Verfolgt Wissensspuren
    - Greift zu wenn sie bereit ist
    - Geniesst und verdaut das Gelernte
    """

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("data/wolf_hunter")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.current_phase = HuntingPhase.RESTING
        self.energy: float = 1.0  # Jagd-Energie (0-1)
        self.hunger_for_knowledge: float = 0.5  # Wissensdurst
        self.current_prey: Optional[KnowledgePrey] = None
        self.prey_collection: Dict[str, KnowledgePrey] = {}
        self.hunt_history: List[Dict] = []

        # Jagd-Instinkte und Praeferenzen
        self.preferred_hunting_grounds = {
            'anime': 0.95,      # LIEBT Anime-Wissen
            'woelfe': 0.90,     # Naturlich!
            'gaming': 0.85,
            'japan': 0.80,
            'technik': 0.70,
            'wissenschaft': 0.65,
            'geschichte': 0.60,
            'musik': 0.75,
            'natur': 0.70,
        }

        # Jagd-Reaktionen
        self.hunt_reactions = {
            HuntingPhase.SNIFFING: [
                "*Nase zuckt* Ich rieche etwas Interessantes...",
                "*Ohren drehen sich suchend* Da ist doch was...",
                "*schnueffelt neugierig* Hmm, was ist das?",
            ],
            HuntingPhase.TRACKING: [
                "*folgt der Spur konzentriert* Ich bin dran...",
                "*schleicht vorsichtig* Das Wissen ist nah...",
                "*Schweif gespannt* Fast hab ich es...",
            ],
            HuntingPhase.STALKING: [
                "*duckt sich* Gleich hab ich es...",
                "*absolut fokussiert* ...",
                "*Augen fixiert* Jetzt nicht bewegen...",
            ],
            HuntingPhase.POUNCING: [
                "*SPRUNG* Ha! Erwischt!",
                "*schnappt zu* MEIN Wissen!",
                "*greift blitzschnell* Hab dich!",
            ],
            HuntingPhase.FEASTING: [
                "*kaut zufrieden auf dem Wissen* Mmh, interessant!",
                "*verdaut das Gelernte* Das muss ich mir merken...",
                "*leckt sich die Lippen* Koestliches Wissen!",
            ],
            HuntingPhase.SATISFIED: [
                "*rollt sich zufrieden zusammen* Das war gut...",
                "*zufriedenes Gaehnen* Genug gejagt fuer heute.",
                "*Schweif wedelt traege* Wissen macht satt!",
            ],
        }

        self._load_state()

    def sniff_for_topics(self, available_topics: List[str]) -> List[Tuple[str, float]]:
        """
        Schnueffelt nach interessanten Themen.

        Returns:
            Liste von (topic, interest_score) sortiert nach Interesse
        """
        self.current_phase = HuntingPhase.SNIFFING

        scored_topics = []
        for topic in available_topics:
            topic_lower = topic.lower()

            # Basis-Interesse aus Praeferenzen
            base_interest = self.preferred_hunting_grounds.get(topic_lower, 0.5)

            # Modifikatoren
            # Mehr Hunger = mehr Interesse
            interest = base_interest * (0.5 + self.hunger_for_knowledge * 0.5)

            # Energie beeinflusst auch
            interest *= (0.7 + self.energy * 0.3)

            # Zufaelliger "Geruchs-Faktor"
            interest *= (0.8 + random.random() * 0.4)

            scored_topics.append((topic, min(1.0, interest)))

        scored_topics.sort(key=lambda x: x[1], reverse=True)
        return scored_topics

    def start_tracking(self, topic: str, description: str = "") -> KnowledgePrey:
        """Beginnt die Verfolgung eines Wissens-Themas"""
        self.current_phase = HuntingPhase.TRACKING

        prey_id = f"prey_{topic}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Berechne Schwierigkeit basierend auf Topic
        base_difficulty = 0.5
        if topic.lower() in ['philosophie', 'wissenschaft', 'technik']:
            base_difficulty = 0.7
        elif topic.lower() in ['anime', 'gaming', 'musik']:
            base_difficulty = 0.3

        prey = KnowledgePrey(
            prey_id=prey_id,
            topic=topic,
            description=description or f"Wissen ueber {topic}",
            difficulty=base_difficulty,
            value=self.preferred_hunting_grounds.get(topic.lower(), 0.5),
            discovered_at=datetime.now()
        )

        self.current_prey = prey
        self.prey_collection[prey_id] = prey

        self._save_state()
        return prey

    def attempt_capture(self, success: bool = None) -> Dict:
        """
        Versucht das aktuelle Wissens-Beutestueck zu fangen.

        Args:
            success: Expliziter Erfolg oder automatisch berechnet

        Returns:
            Ergebnis des Jagdversuchs
        """
        if not self.current_prey:
            return {'success': False, 'message': "*verwirrt* Was jage ich eigentlich?"}

        self.current_phase = HuntingPhase.POUNCING
        self.current_prey.hunt_attempts += 1

        # Berechne Erfolg wenn nicht explizit gegeben
        if success is None:
            # Erfolgswahrscheinlichkeit basiert auf Energie, Erfahrung, Schwierigkeit
            base_chance = 0.6
            energy_bonus = self.energy * 0.2
            difficulty_penalty = self.current_prey.difficulty * 0.3
            experience_bonus = min(0.2, len(self.hunt_history) * 0.01)

            success_chance = base_chance + energy_bonus - difficulty_penalty + experience_bonus
            success = random.random() < success_chance

        result = {
            'success': success,
            'prey': self.current_prey.topic,
            'attempts': self.current_prey.hunt_attempts,
        }

        if success:
            self.current_prey.captured = True
            self.current_prey.captured_at = datetime.now()
            self.current_phase = HuntingPhase.FEASTING

            # Reduziere Hunger, erhoehe Zufriedenheit
            self.hunger_for_knowledge = max(0.1, self.hunger_for_knowledge - 0.2)
            self.energy = min(1.0, self.energy + 0.1)

            reaction = random.choice(self.hunt_reactions[HuntingPhase.POUNCING])
            result['reaction'] = reaction
            result['message'] = f"{reaction} Ich habe {self.current_prey.topic} erfasst!"

            # Zur Historie hinzufuegen
            self.hunt_history.append({
                'prey_id': self.current_prey.prey_id,
                'topic': self.current_prey.topic,
                'captured_at': datetime.now().isoformat(),
                'attempts': self.current_prey.hunt_attempts,
            })

        else:
            # Energie sinkt bei Misserfolg
            self.energy = max(0.1, self.energy - 0.1)

            result['reaction'] = "*knurrt frustriert* Das Wissen ist mir entwischt..."
            result['message'] = "Die Jagd war nicht erfolgreich... aber ich gebe nicht auf!"

        self._save_state()
        return result

    def digest_knowledge(self, learned_content: str) -> str:
        """
        'Verdaut' das gelernte Wissen.

        Returns:
            Reaktion waehrend des Verdauens
        """
        self.current_phase = HuntingPhase.FEASTING

        reaction = random.choice(self.hunt_reactions[HuntingPhase.FEASTING])

        # Nach dem Verdauen zufrieden
        self.current_phase = HuntingPhase.SATISFIED
        self.current_prey = None

        return f"{reaction}\n{learned_content[:100]}... *nickt verstehend*"

    def rest(self):
        """Ruhezeit - Energie regenerieren"""
        self.current_phase = HuntingPhase.RESTING
        self.energy = min(1.0, self.energy + 0.3)
        self.hunger_for_knowledge = min(1.0, self.hunger_for_knowledge + 0.1)
        self._save_state()

    def get_hunt_status(self) -> Dict:
        """Gibt den aktuellen Jagd-Status zurueck"""
        return {
            'phase': self.current_phase.value,
            'energy': round(self.energy, 2),
            'hunger': round(self.hunger_for_knowledge, 2),
            'current_prey': self.current_prey.topic if self.current_prey else None,
            'total_captures': len([p for p in self.prey_collection.values() if p.captured]),
            'total_discoveries': len(self.prey_collection),
            'reaction': random.choice(self.hunt_reactions.get(self.current_phase, ["*wartet*"]))
        }

    def get_trophies(self) -> List[Dict]:
        """Gibt gefangene Wissens-'Trophaeen' zurueck"""
        trophies = []
        for prey in self.prey_collection.values():
            if prey.captured:
                trophies.append({
                    'topic': prey.topic,
                    'captured_at': prey.captured_at.isoformat() if prey.captured_at else None,
                    'value': prey.value,
                    'attempts_needed': prey.hunt_attempts,
                })
        return sorted(trophies, key=lambda x: x['value'], reverse=True)

    def _save_state(self):
        """Speichert den Zustand"""
        try:
            state = {
                'current_phase': self.current_phase.value,
                'energy': self.energy,
                'hunger': self.hunger_for_knowledge,
                'current_prey': self.current_prey.prey_id if self.current_prey else None,
                'prey_collection': {
                    k: {
                        'prey_id': v.prey_id,
                        'topic': v.topic,
                        'description': v.description,
                        'difficulty': v.difficulty,
                        'value': v.value,
                        'discovered_at': v.discovered_at.isoformat(),
                        'captured': v.captured,
                        'captured_at': v.captured_at.isoformat() if v.captured_at else None,
                        'hunt_attempts': v.hunt_attempts,
                    } for k, v in self.prey_collection.items()
                },
                'hunt_history': self.hunt_history[-100:],
            }
            with open(self.data_dir / "wolf_hunter.json", 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Konnte WolfHunter nicht speichern: {e}")

    def _load_state(self):
        """Laedt den Zustand"""
        try:
            path = self.data_dir / "wolf_hunter.json"
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    state = json.load(f)

                self.current_phase = HuntingPhase(state.get('current_phase', 'resting'))
                self.energy = state.get('energy', 1.0)
                self.hunger_for_knowledge = state.get('hunger', 0.5)
                self.hunt_history = state.get('hunt_history', [])

                for k, v in state.get('prey_collection', {}).items():
                    self.prey_collection[k] = KnowledgePrey(
                        prey_id=v['prey_id'],
                        topic=v['topic'],
                        description=v.get('description', ''),
                        difficulty=v.get('difficulty', 0.5),
                        value=v.get('value', 0.5),
                        discovered_at=datetime.fromisoformat(v['discovered_at']),
                        captured=v.get('captured', False),
                        captured_at=datetime.fromisoformat(v['captured_at']) if v.get('captured_at') else None,
                        hunt_attempts=v.get('hunt_attempts', 0),
                    )

                if state.get('current_prey') and state['current_prey'] in self.prey_collection:
                    self.current_prey = self.prey_collection[state['current_prey']]
        except Exception as e:
            logger.debug(f"Konnte WolfHunter nicht laden: {e}")


# =============================================================================
# 2. EMOTIONALE NEUGIER-REAKTIONEN
# =============================================================================

class CuriosityEmotion(Enum):
    """Emotionale Zustaende bei Neugier"""
    BORED = "bored"                   # Gelangweilt
    MILDLY_INTERESTED = "mildly"      # Leicht interessiert
    CURIOUS = "curious"               # Neugierig
    EXCITED = "excited"               # Aufgeregt
    FASCINATED = "fascinated"         # Fasziniert
    OBSESSED = "obsessed"             # Besessen (will ALLES wissen)


@dataclass
class CuriosityState:
    """Zustand der emotionalen Neugier"""
    emotion: CuriosityEmotion
    intensity: float  # 0-1
    trigger_topic: Optional[str] = None
    duration_minutes: int = 0
    started_at: datetime = field(default_factory=datetime.now)


class EmotionalCuriositySystem:
    """
    System fuer emotionale Neugier-Reaktionen.

    Holo zeigt verschiedene emotionale Reaktionen basierend auf
    ihrem Neugier-Level und dem Thema.
    """

    def __init__(self):
        self.current_state = CuriosityState(
            emotion=CuriosityEmotion.MILDLY_INTERESTED,
            intensity=0.3
        )

        # Emotionale Reaktionen
        self.emotional_reactions = {
            CuriosityEmotion.BORED: [
                "*gaehnt* Gibt's nichts Interessanteres?",
                "*Ohren haengen* Das ist... naja...",
                "*schaut desinteressiert weg*",
            ],
            CuriosityEmotion.MILDLY_INTERESTED: [
                "*Ohr zuckt* Hmm, okay...",
                "Das ist ganz interessant...",
                "*nickt* Erzaehl weiter...",
            ],
            CuriosityEmotion.CURIOUS: [
                "*Ohren aufmerksam aufgestellt* Oh? Erzaehl mehr!",
                "*rueckt naeher* Das klingt interessant!",
                "*Schweif wippt* Ich will mehr wissen!",
            ],
            CuriosityEmotion.EXCITED: [
                "*springt aufgeregt* WAS?! Das ist ja toll!",
                "*Schweif wedelt wild* Erzaehl! Erzaehl! Erzaehl!",
                "*Augen leuchten* Das ist SO cool!",
            ],
            CuriosityEmotion.FASCINATED: [
                "*Mund steht offen* ...wow...",
                "*kann nicht aufhoeren zu lauschen* ...faszinierend...",
                "*voellig gebannt* Das ist unglaublich...",
            ],
            CuriosityEmotion.OBSESSED: [
                "*MUSS alles wissen* MEHR! ICH BRAUCHE MEHR!",
                "*kann an nichts anderes denken* Dieses Thema... es laesst mich nicht los!",
                "*recherchiert fieberhaft* Ich werde nicht ruhen bis ich alles weiss!",
            ],
        }

        # Themen die besondere Emotionen ausloesen
        self.emotion_triggers = {
            'anime': CuriosityEmotion.EXCITED,
            'woelfe': CuriosityEmotion.FASCINATED,
            'gaming': CuriosityEmotion.EXCITED,
            'japan': CuriosityEmotion.CURIOUS,
            'spice and wolf': CuriosityEmotion.OBSESSED,
            'kemonomimi': CuriosityEmotion.FASCINATED,
        }

    def update_state(self, topic: str, interest_level: float) -> CuriosityState:
        """
        Aktualisiert den emotionalen Neugier-Zustand.

        Args:
            topic: Das aktuelle Thema
            interest_level: Interesse-Level (0-1)
        """
        # Bestimme Emotion basierend auf Topic und Interest
        topic_lower = topic.lower()

        # Spezielle Topic-Trigger
        base_emotion = self.emotion_triggers.get(topic_lower, None)

        if base_emotion is None:
            # Bestimme Emotion basierend auf Interest-Level
            if interest_level < 0.2:
                base_emotion = CuriosityEmotion.BORED
            elif interest_level < 0.4:
                base_emotion = CuriosityEmotion.MILDLY_INTERESTED
            elif interest_level < 0.6:
                base_emotion = CuriosityEmotion.CURIOUS
            elif interest_level < 0.8:
                base_emotion = CuriosityEmotion.EXCITED
            elif interest_level < 0.95:
                base_emotion = CuriosityEmotion.FASCINATED
            else:
                base_emotion = CuriosityEmotion.OBSESSED

        self.current_state = CuriosityState(
            emotion=base_emotion,
            intensity=interest_level,
            trigger_topic=topic,
            started_at=datetime.now()
        )

        return self.current_state

    def get_reaction(self) -> str:
        """Gibt eine emotionale Reaktion basierend auf aktuellem Zustand"""
        return random.choice(self.emotional_reactions[self.current_state.emotion])

    def get_curiosity_description(self) -> str:
        """Beschreibt den aktuellen Neugier-Zustand"""
        descriptions = {
            CuriosityEmotion.BORED: "Mir ist langweilig...",
            CuriosityEmotion.MILDLY_INTERESTED: "Das ist ganz okay...",
            CuriosityEmotion.CURIOUS: "Ich bin neugierig!",
            CuriosityEmotion.EXCITED: "Das ist SO aufregend!",
            CuriosityEmotion.FASCINATED: "Ich bin total fasziniert!",
            CuriosityEmotion.OBSESSED: "ICH MUSS MEHR WISSEN!",
        }
        return descriptions[self.current_state.emotion]


# =============================================================================
# 3. INTERESSE-ENTDECKUNG
# =============================================================================

@dataclass
class InterestDiscovery:
    """Eine entdeckte Interesse"""
    topic: str
    discovered_at: datetime
    discovery_context: str
    initial_interest: float
    current_interest: float
    times_explored: int = 0
    related_discoveries: List[str] = field(default_factory=list)


class InterestExplorer:
    """
    System zur Entdeckung neuer Interessen durch Exploration.

    Holo entdeckt neue Interessen wenn sie:
    - Ueber verwandte Themen stolpert
    - Unerwartete Verbindungen findet
    - Positive Erfahrungen mit einem Thema macht
    """

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("data/interest_explorer")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.discovered_interests: Dict[str, InterestDiscovery] = {}
        self.exploration_history: List[Dict] = []

        # Verbindungen zwischen Interessen
        self.interest_connections = {
            'anime': ['manga', 'japan', 'gaming', 'musik'],
            'woelfe': ['natur', 'tiere', 'mythologie', 'biologie'],
            'gaming': ['technik', 'anime', 'musik', 'streaming'],
            'japan': ['anime', 'manga', 'geschichte', 'sprachen'],
            'technik': ['gaming', 'wissenschaft', 'programmierung'],
            'musik': ['anime', 'japan', 'kultur'],
        }

        # Entdeckungs-Reaktionen
        self.discovery_reactions = [
            "*Ohren spitzen sich ueberrascht* Oh! Das ist ja interessant!",
            "*Schweif wedelt aufgeregt* Ich hab was Neues entdeckt!",
            "*Augen weiten sich* Das wusste ich noch gar nicht!",
            "*springt vor Freude* Ein neues Thema zum Erkunden!",
        ]

        self._load_state()

    def explore_connection(self, current_topic: str) -> Optional[InterestDiscovery]:
        """
        Erkundet Verbindungen zu neuen Themen.

        Returns:
            Neue Interesse wenn entdeckt, sonst None
        """
        topic_lower = current_topic.lower()
        connections = self.interest_connections.get(topic_lower, [])

        if not connections:
            return None

        # Waehle zufaellige Verbindung
        potential_discovery = random.choice(connections)

        # Pruefe ob bereits entdeckt
        if potential_discovery in self.discovered_interests:
            # Erhoehe Interesse bei Wiederentdeckung
            discovery = self.discovered_interests[potential_discovery]
            discovery.times_explored += 1
            discovery.current_interest = min(1.0, discovery.current_interest + 0.05)
            return discovery

        # Neue Entdeckung!
        discovery = InterestDiscovery(
            topic=potential_discovery,
            discovered_at=datetime.now(),
            discovery_context=f"Entdeckt waehrend Erkundung von {current_topic}",
            initial_interest=0.4 + random.random() * 0.3,
            current_interest=0.5,
            related_discoveries=[current_topic]
        )

        self.discovered_interests[potential_discovery] = discovery

        self.exploration_history.append({
            'discovered': potential_discovery,
            'from': current_topic,
            'timestamp': datetime.now().isoformat()
        })

        self._save_state()
        return discovery

    def record_positive_experience(self, topic: str, enjoyment: float):
        """Zeichnet positive Erfahrung mit einem Thema auf"""
        topic_lower = topic.lower()

        if topic_lower in self.discovered_interests:
            discovery = self.discovered_interests[topic_lower]
            discovery.current_interest = min(1.0, discovery.current_interest + enjoyment * 0.1)
            discovery.times_explored += 1
        else:
            # Neue Interesse durch positive Erfahrung
            self.discovered_interests[topic_lower] = InterestDiscovery(
                topic=topic_lower,
                discovered_at=datetime.now(),
                discovery_context="Positive Erfahrung",
                initial_interest=enjoyment * 0.5,
                current_interest=enjoyment * 0.6,
                times_explored=1
            )

        self._save_state()

    def get_discovery_reaction(self, discovery: InterestDiscovery) -> str:
        """Generiert eine Reaktion auf eine neue Entdeckung"""
        reaction = random.choice(self.discovery_reactions)
        return f"{reaction} {discovery.topic.title()} klingt spannend!"

    def get_interest_map(self) -> Dict[str, float]:
        """Gibt eine Karte aller Interessen mit ihren Levels zurueck"""
        return {
            topic: discovery.current_interest
            for topic, discovery in self.discovered_interests.items()
        }

    def get_recent_discoveries(self, days: int = 7) -> List[InterestDiscovery]:
        """Gibt kuerzlich entdeckte Interessen zurueck"""
        cutoff = datetime.now() - timedelta(days=days)
        recent = [
            d for d in self.discovered_interests.values()
            if d.discovered_at >= cutoff
        ]
        return sorted(recent, key=lambda d: d.discovered_at, reverse=True)

    def _save_state(self):
        """Speichert den Zustand"""
        try:
            state = {
                'discovered_interests': {
                    k: {
                        'topic': v.topic,
                        'discovered_at': v.discovered_at.isoformat(),
                        'discovery_context': v.discovery_context,
                        'initial_interest': v.initial_interest,
                        'current_interest': v.current_interest,
                        'times_explored': v.times_explored,
                        'related_discoveries': v.related_discoveries,
                    } for k, v in self.discovered_interests.items()
                },
                'exploration_history': self.exploration_history[-100:],
            }
            with open(self.data_dir / "interest_explorer.json", 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Konnte InterestExplorer nicht speichern: {e}")

    def _load_state(self):
        """Laedt den Zustand"""
        try:
            path = self.data_dir / "interest_explorer.json"
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    state = json.load(f)

                for k, v in state.get('discovered_interests', {}).items():
                    self.discovered_interests[k] = InterestDiscovery(
                        topic=v['topic'],
                        discovered_at=datetime.fromisoformat(v['discovered_at']),
                        discovery_context=v.get('discovery_context', ''),
                        initial_interest=v.get('initial_interest', 0.5),
                        current_interest=v.get('current_interest', 0.5),
                        times_explored=v.get('times_explored', 0),
                        related_discoveries=v.get('related_discoveries', []),
                    )

                self.exploration_history = state.get('exploration_history', [])
        except Exception as e:
            logger.debug(f"Konnte InterestExplorer nicht laden: {e}")


# =============================================================================
# 4. WISSENS-SAMMEL-INSTINKT
# =============================================================================

class CollectorRank(Enum):
    """Rang als Wissens-Sammler"""
    NOVICE = "novice"           # Anfaenger
    APPRENTICE = "apprentice"   # Lehrling
    COLLECTOR = "collector"     # Sammler
    SCHOLAR = "scholar"         # Gelehrte
    EXPERT = "expert"           # Experte
    MASTER = "master"           # Meister
    SAGE = "sage"               # Weise


@dataclass
class KnowledgeCollection:
    """Eine Sammlung von Wissen zu einem Thema"""
    topic: str
    facts_collected: int
    unique_insights: int
    started_at: datetime
    last_addition: datetime
    completion_percentage: float  # Geschaetzte Vollstaendigkeit


class WisdomCollector:
    """
    Wissens-Sammel-System mit Gamification-Elementen.

    Holo sammelt Wissen wie Schaetze:
    - Jedes Thema hat eine Sammlung
    - Fortschritt wird getrackt
    - Raenge werden freigeschaltet
    """

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("data/wisdom_collector")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.collections: Dict[str, KnowledgeCollection] = {}
        self.total_facts_collected: int = 0
        self.current_rank: CollectorRank = CollectorRank.NOVICE

        # Rang-Schwellwerte
        self.rank_thresholds = {
            CollectorRank.NOVICE: 0,
            CollectorRank.APPRENTICE: 50,
            CollectorRank.COLLECTOR: 150,
            CollectorRank.SCHOLAR: 300,
            CollectorRank.EXPERT: 500,
            CollectorRank.MASTER: 1000,
            CollectorRank.SAGE: 2000,
        }

        # Rang-Belohnungen (Reaktionen)
        self.rank_up_reactions = {
            CollectorRank.APPRENTICE: "*Ohren stolz aufgestellt* Ich bin jetzt ein Lehrling des Wissens!",
            CollectorRank.COLLECTOR: "*Schweif wedelt stolz* Ich bin offiziell eine Sammlerin!",
            CollectorRank.SCHOLAR: "*strahlt* Die Gelehrte Holo - das klingt gut!",
            CollectorRank.EXPERT: "*zufriedenes Schnurren* Expertin in Sachen Wissen!",
            CollectorRank.MASTER: "*ehrfuerchtig* Meisterin des Wissens... wow!",
            CollectorRank.SAGE: "*tiefe Verbeugung* Die weise Holo... ich habe so viel gelernt!",
        }

        self._load_state()

    def add_to_collection(self, topic: str, fact_count: int = 1,
                          is_unique: bool = False) -> Dict:
        """
        Fuegt Wissen zur Sammlung hinzu.

        Returns:
            Status-Update inkl. moeglicherem Rang-Aufstieg
        """
        result = {
            'topic': topic,
            'added': fact_count,
            'rank_up': None,
        }

        topic_lower = topic.lower()

        if topic_lower not in self.collections:
            self.collections[topic_lower] = KnowledgeCollection(
                topic=topic_lower,
                facts_collected=0,
                unique_insights=0,
                started_at=datetime.now(),
                last_addition=datetime.now(),
                completion_percentage=0.0
            )

        collection = self.collections[topic_lower]
        collection.facts_collected += fact_count
        collection.last_addition = datetime.now()
        if is_unique:
            collection.unique_insights += 1

        # Schaetze Vollstaendigkeit (vereinfacht)
        collection.completion_percentage = min(100.0, collection.facts_collected / 50 * 100)

        self.total_facts_collected += fact_count

        # Pruefe Rang-Aufstieg
        old_rank = self.current_rank
        new_rank = self._calculate_rank()

        if new_rank != old_rank:
            self.current_rank = new_rank
            result['rank_up'] = {
                'old': old_rank.value,
                'new': new_rank.value,
                'reaction': self.rank_up_reactions.get(new_rank, "*freut sich*")
            }

        self._save_state()
        return result

    def _calculate_rank(self) -> CollectorRank:
        """Berechnet den aktuellen Rang basierend auf gesammeltem Wissen"""
        for rank in reversed(list(CollectorRank)):
            if self.total_facts_collected >= self.rank_thresholds[rank]:
                return rank
        return CollectorRank.NOVICE

    def get_collection_stats(self) -> Dict:
        """Gibt Statistiken ueber alle Sammlungen zurueck"""
        return {
            'total_facts': self.total_facts_collected,
            'current_rank': self.current_rank.value,
            'next_rank_at': self._get_next_rank_threshold(),
            'progress_to_next': self._get_progress_to_next_rank(),
            'collections_count': len(self.collections),
            'top_collections': self._get_top_collections(5),
        }

    def _get_next_rank_threshold(self) -> int:
        """Gibt die Schwelle zum naechsten Rang zurueck"""
        ranks = list(CollectorRank)
        current_idx = ranks.index(self.current_rank)
        if current_idx < len(ranks) - 1:
            return self.rank_thresholds[ranks[current_idx + 1]]
        return self.rank_thresholds[CollectorRank.SAGE]

    def _get_progress_to_next_rank(self) -> float:
        """Berechnet Fortschritt zum naechsten Rang (0-1)"""
        current_threshold = self.rank_thresholds[self.current_rank]
        next_threshold = self._get_next_rank_threshold()

        if next_threshold == current_threshold:
            return 1.0

        progress = (self.total_facts_collected - current_threshold) / (next_threshold - current_threshold)
        return min(1.0, max(0.0, progress))

    def _get_top_collections(self, limit: int) -> List[Dict]:
        """Gibt die groessten Sammlungen zurueck"""
        sorted_collections = sorted(
            self.collections.values(),
            key=lambda c: c.facts_collected,
            reverse=True
        )
        return [
            {
                'topic': c.topic,
                'facts': c.facts_collected,
                'completion': round(c.completion_percentage, 1)
            }
            for c in sorted_collections[:limit]
        ]

    def get_collection_summary(self, topic: str) -> Optional[Dict]:
        """Gibt Zusammenfassung einer spezifischen Sammlung"""
        collection = self.collections.get(topic.lower())
        if not collection:
            return None

        return {
            'topic': collection.topic,
            'facts_collected': collection.facts_collected,
            'unique_insights': collection.unique_insights,
            'completion': round(collection.completion_percentage, 1),
            'days_collecting': (datetime.now() - collection.started_at).days,
        }

    def _save_state(self):
        """Speichert den Zustand"""
        try:
            state = {
                'collections': {
                    k: {
                        'topic': v.topic,
                        'facts_collected': v.facts_collected,
                        'unique_insights': v.unique_insights,
                        'started_at': v.started_at.isoformat(),
                        'last_addition': v.last_addition.isoformat(),
                        'completion_percentage': v.completion_percentage,
                    } for k, v in self.collections.items()
                },
                'total_facts_collected': self.total_facts_collected,
                'current_rank': self.current_rank.value,
            }
            with open(self.data_dir / "wisdom_collector.json", 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Konnte WisdomCollector nicht speichern: {e}")

    def _load_state(self):
        """Laedt den Zustand"""
        try:
            path = self.data_dir / "wisdom_collector.json"
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    state = json.load(f)

                self.total_facts_collected = state.get('total_facts_collected', 0)
                self.current_rank = CollectorRank(state.get('current_rank', 'novice'))

                for k, v in state.get('collections', {}).items():
                    self.collections[k] = KnowledgeCollection(
                        topic=v['topic'],
                        facts_collected=v.get('facts_collected', 0),
                        unique_insights=v.get('unique_insights', 0),
                        started_at=datetime.fromisoformat(v['started_at']),
                        last_addition=datetime.fromisoformat(v['last_addition']),
                        completion_percentage=v.get('completion_percentage', 0.0),
                    )
        except Exception as e:
            logger.debug(f"Konnte WisdomCollector nicht laden: {e}")


# =============================================================================
# 5. NATUERLICHE LERN-MOTIVATION
# =============================================================================

class MotivationType(Enum):
    """Arten von Lern-Motivation"""
    CURIOSITY = "curiosity"        # Neugier
    ACHIEVEMENT = "achievement"    # Leistung
    SOCIAL = "social"              # Sozial (jemanden beeindrucken)
    MASTERY = "mastery"            # Meisterschaft anstreben
    PLAY = "play"                  # Spielerisch
    HELPING = "helping"            # Anderen helfen wollen


class NaturalMotivation:
    """
    System fuer natuerliche Lern-Motivation.

    Holo hat verschiedene Gruende zum Lernen:
    - Reine Neugier
    - Jemanden beeindrucken wollen
    - Spielerisches Entdecken
    - Anderen helfen koennen
    """

    def __init__(self):
        # Basis-Motivationen
        self.motivation_levels = {
            MotivationType.CURIOSITY: 0.8,
            MotivationType.ACHIEVEMENT: 0.6,
            MotivationType.SOCIAL: 0.7,
            MotivationType.MASTERY: 0.5,
            MotivationType.PLAY: 0.75,
            MotivationType.HELPING: 0.65,
        }

        # Aktuelle dominante Motivation
        self.current_motivation: MotivationType = MotivationType.CURIOSITY

        # Motivations-Aussagen
        self.motivation_statements = {
            MotivationType.CURIOSITY: [
                "*Ohren neugierig aufgestellt* Ich MUSS das wissen!",
                "Was ist das? *schnueffelt interessiert*",
                "Meine Neugier laesst mir keine Ruhe!",
            ],
            MotivationType.ACHIEVEMENT: [
                "*zielstrebig* Ich will das meistern!",
                "Mein Ziel: Expertin in diesem Thema werden!",
                "*entschlossen* Das schaffe ich!",
            ],
            MotivationType.SOCIAL: [
                "*freudig* Stell dir vor, was ich dir zeigen kann!",
                "Ich will dir davon erzaehlen koennen!",
                "*aufgeregt* Das wird dich beeindrucken!",
            ],
            MotivationType.MASTERY: [
                "*fokussiert* Ich will das WIRKLICH verstehen.",
                "Nicht nur wissen - BEGREIFEN!",
                "*tiefgruendig* Ich will die Zusammenhaenge sehen.",
            ],
            MotivationType.PLAY: [
                "*verspielt* Lernen macht Spass!",
                "*huepft herum* Das ist wie ein Spiel!",
                "*kichert* Wissen sammeln ist das beste Spiel!",
            ],
            MotivationType.HELPING: [
                "*hilfsbereit* Damit kann ich anderen helfen!",
                "Wenn ich das weiss, kann ich besser unterstuetzen!",
                "*fuersorgend* Das koennte nuetzlich sein!",
            ],
        }

    def update_motivation(self, context: Dict) -> MotivationType:
        """
        Aktualisiert die aktuelle Motivation basierend auf Kontext.

        Context kann enthalten:
        - 'social_interaction': bool
        - 'challenge_level': float
        - 'topic_interest': float
        - 'helper_context': bool
        """
        scores = {}

        for mtype, base_level in self.motivation_levels.items():
            score = base_level

            if mtype == MotivationType.SOCIAL and context.get('social_interaction'):
                score *= 1.5
            elif mtype == MotivationType.MASTERY and context.get('challenge_level', 0) > 0.7:
                score *= 1.4
            elif mtype == MotivationType.CURIOSITY and context.get('topic_interest', 0) > 0.8:
                score *= 1.3
            elif mtype == MotivationType.HELPING and context.get('helper_context'):
                score *= 1.5
            elif mtype == MotivationType.PLAY:
                score *= (0.8 + random.random() * 0.4)  # Zufaelliger Spieltrieb

            scores[mtype] = min(1.0, score)

        self.current_motivation = max(scores, key=scores.get)
        return self.current_motivation

    def get_motivation_statement(self) -> str:
        """Gibt einen motivierenden Satz zurueck"""
        return random.choice(self.motivation_statements[self.current_motivation])

    def get_motivation_boost(self, topic: str) -> float:
        """
        Berechnet Motivations-Boost fuer ein Thema.

        Returns:
            Multiplikator (0.5 - 2.0)
        """
        base = self.motivation_levels[self.current_motivation]

        # Bonus fuer Lieblings-Themen
        favorite_topics = ['anime', 'woelfe', 'gaming', 'japan']
        if topic.lower() in favorite_topics:
            base *= 1.3

        return min(2.0, max(0.5, base * 1.5))


# =============================================================================
# 6. INTEGRIERTES CURIOSITY-DRIVEN SYSTEM
# =============================================================================

class CuriosityDrivenLearning:
    """
    Integriertes System fuer Neugier-gesteuertes Lernen.

    Kombiniert:
    - Wolf-basierte Wissensjagd
    - Emotionale Neugier-Reaktionen
    - Interesse-Entdeckung
    - Wissens-Sammlung
    - Natuerliche Motivation
    """

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("data/curiosity_driven")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialisiere alle Subsysteme
        self.wolf_hunter = WolfKnowledgeHunter(self.data_dir / "wolf_hunter")
        self.emotional_curiosity = EmotionalCuriositySystem()
        self.interest_explorer = InterestExplorer(self.data_dir / "explorer")
        self.wisdom_collector = WisdomCollector(self.data_dir / "collector")
        self.motivation = NaturalMotivation()

        logger.info("[CuriosityDriven] System initialisiert mit 5 Subsystemen")

    def start_learning_session(self, available_topics: List[str]) -> Dict:
        """
        Startet eine Neugier-gesteuerte Lernsession.

        Returns:
            Session-Plan mit Themen, Reaktionen und Motivation
        """
        session = {
            'phase': 'starting',
            'topics': [],
            'reactions': [],
            'motivation': None,
        }

        # 1. Schnueffeln nach interessanten Themen
        sniffed_topics = self.wolf_hunter.sniff_for_topics(available_topics)
        session['topics'] = sniffed_topics[:5]

        sniff_status = self.wolf_hunter.get_hunt_status()
        session['reactions'].append(sniff_status['reaction'])

        # 2. Emotionalen Zustand basierend auf Top-Thema setzen
        if sniffed_topics:
            top_topic, top_interest = sniffed_topics[0]
            self.emotional_curiosity.update_state(top_topic, top_interest)
            session['reactions'].append(self.emotional_curiosity.get_reaction())

        # 3. Motivation bestimmen
        self.motivation.update_motivation({
            'topic_interest': sniffed_topics[0][1] if sniffed_topics else 0.5,
            'social_interaction': True,
        })
        session['motivation'] = self.motivation.get_motivation_statement()

        # 4. Starte Jagd auf Top-Thema
        if sniffed_topics:
            self.wolf_hunter.start_tracking(sniffed_topics[0][0])

        session['phase'] = 'hunting'
        return session

    def learn_fact(self, topic: str, content: str) -> Dict:
        """
        Lernt einen Fakt mit allen Neugier-Systemen.

        Returns:
            Komplettes Feedback mit Reaktionen und Updates
        """
        result = {
            'topic': topic,
            'content': content[:50],
            'reactions': [],
            'updates': {},
        }

        # 1. Versuche Wissen zu "fangen"
        capture_result = self.wolf_hunter.attempt_capture(success=True)
        result['reactions'].append(capture_result['reaction'])

        # 2. Zur Sammlung hinzufuegen
        collection_result = self.wisdom_collector.add_to_collection(topic, 1)
        result['updates']['collection'] = collection_result

        if collection_result.get('rank_up'):
            result['reactions'].append(collection_result['rank_up']['reaction'])

        # 3. Emotionale Reaktion
        interest = self.wolf_hunter.preferred_hunting_grounds.get(topic.lower(), 0.5)
        self.emotional_curiosity.update_state(topic, interest)
        result['reactions'].append(self.emotional_curiosity.get_reaction())

        # 4. Interesse-Exploration
        discovery = self.interest_explorer.explore_connection(topic)
        if discovery and discovery.times_explored == 1:
            # Neue Entdeckung!
            result['reactions'].append(
                self.interest_explorer.get_discovery_reaction(discovery)
            )
            result['updates']['new_discovery'] = discovery.topic

        # 5. Verdaue das Wissen
        digestion = self.wolf_hunter.digest_knowledge(content)
        result['reactions'].append(digestion)

        return result

    def get_next_learning_suggestion(self) -> Dict:
        """
        Gibt einen Vorschlag fuer das naechste Lernthema.

        Basiert auf:
        - Wolf-Hunger
        - Emotionalem Zustand
        - Entdeckten Interessen
        - Sammlung-Luecken
        """
        suggestion = {
            'suggested_topic': None,
            'reason': None,
            'motivation': None,
            'enthusiasm_level': 0.5,
        }

        # Sammle alle Kandidaten
        candidates = []

        # Aus Interesse-Entdeckungen
        interest_map = self.interest_explorer.get_interest_map()
        for topic, interest in interest_map.items():
            candidates.append((topic, interest * 0.8, f"Interesse an {topic}"))

        # Aus Wolf-Praeferenzen
        for topic, pref in self.wolf_hunter.preferred_hunting_grounds.items():
            if topic not in interest_map:
                candidates.append((topic, pref * 0.7, f"Wolfs-Instinkt fuer {topic}"))

        # Sortiere nach Score
        candidates.sort(key=lambda x: x[1], reverse=True)

        if candidates:
            top_topic, score, reason = candidates[0]
            suggestion['suggested_topic'] = top_topic
            suggestion['reason'] = reason
            suggestion['enthusiasm_level'] = score

            # Motivations-Statement
            self.motivation.update_motivation({'topic_interest': score})
            suggestion['motivation'] = self.motivation.get_motivation_statement()

        return suggestion

    def get_comprehensive_status(self) -> Dict:
        """Gibt umfassenden Status aller Systeme zurueck"""
        return {
            'wolf_status': self.wolf_hunter.get_hunt_status(),
            'emotional_state': {
                'emotion': self.emotional_curiosity.current_state.emotion.value,
                'intensity': self.emotional_curiosity.current_state.intensity,
                'description': self.emotional_curiosity.get_curiosity_description(),
            },
            'collection_stats': self.wisdom_collector.get_collection_stats(),
            'interest_map': self.interest_explorer.get_interest_map(),
            'current_motivation': self.motivation.current_motivation.value,
            'trophies': len(self.wolf_hunter.get_trophies()),
        }


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

_curiosity_system: Optional[CuriosityDrivenLearning] = None

def get_curiosity_driven_learning() -> CuriosityDrivenLearning:
    """Gibt die globale CuriosityDrivenLearning-Instanz zurueck"""
    global _curiosity_system
    if _curiosity_system is None:
        _curiosity_system = CuriosityDrivenLearning()
    return _curiosity_system


# =============================================================================
# MAIN (TEST)
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("HOLO CURIOSITY-DRIVEN LEARNING SYSTEM v1.0")
    print("=" * 60)

    # Initialisiere System
    cdl = CuriosityDrivenLearning()

    # Teste Lernsession
    print("\n--- LERNSESSION STARTEN ---")
    topics = ['anime', 'gaming', 'wissenschaft', 'geschichte', 'woelfe']
    session = cdl.start_learning_session(topics)

    print(f"Phase: {session['phase']}")
    print(f"Top-Themen: {session['topics'][:3]}")
    print(f"Motivation: {session['motivation']}")
    for reaction in session['reactions']:
        print(f"  {reaction}")

    # Teste Fakten lernen
    print("\n--- FAKTEN LERNEN ---")
    test_facts = [
        ("anime", "Anime bedeutet auf Japanisch einfach Animation."),
        ("woelfe", "Woelfe koennen Gesichter erkennen und sich an Menschen erinnern."),
        ("gaming", "Minecraft hat ueber 300 Millionen verkaufte Exemplare."),
    ]

    for topic, content in test_facts:
        result = cdl.learn_fact(topic, content)
        print(f"\nThema: {topic}")
        for reaction in result['reactions'][:2]:
            print(f"  {reaction}")

    # Status
    print("\n--- GESAMTSTATUS ---")
    status = cdl.get_comprehensive_status()
    print(f"Wolf-Phase: {status['wolf_status']['phase']}")
    print(f"Emotion: {status['emotional_state']['emotion']} ({status['emotional_state']['description']})")
    print(f"Rang: {status['collection_stats']['current_rank']}")
    print(f"Gesammelte Fakten: {status['collection_stats']['total_facts']}")
    print(f"Trophaeen: {status['trophies']}")

    # Naechster Vorschlag
    print("\n--- NAECHSTER VORSCHLAG ---")
    suggestion = cdl.get_next_learning_suggestion()
    print(f"Vorschlag: {suggestion['suggested_topic']}")
    print(f"Grund: {suggestion['reason']}")
    print(f"Motivation: {suggestion['motivation']}")

    print("\n" + "=" * 60)
    print("Curiosity-Driven Learning System bereit!")
