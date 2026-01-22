#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO MARKOV INTELLIGENCE ENGINE v1.0                                        ║
║                                                                              ║
║  Markov-basierte "Intelligenz" für natürlichere, charakteristische Antworten ║
║                                                                              ║
║  Features:                                                                   ║
║  - ThoughtMarkovChain: Gedankensprünge & Assoziationen                       ║
║  - EmotionMarkovChain: Emotionale Übergänge basierend auf Kontext            ║
║  - PersonalityMarkovChain: Charakteristische Holo-Reaktionen                 ║
║  - KnowledgeMarkovChain: Wissensverknüpfungen & interessante Fakten          ║
║  - HoloIntelligenceEngine: Kombiniert alle für "intelligente" Responses      ║
║                                                                              ║
║  Version: 1.0.0                                                              ║
║  Author: Kira & Claude                                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random
import logging
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, field
from collections import defaultdict, Counter
from enum import Enum

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS & DATENKLASSEN
# =============================================================================

class EmotionState(Enum):
    """Emotionale Zustände für die Emotions-Markov-Kette"""
    NEUTRAL = "neutral"
    FREUDIG = "freudig"
    TRAURIG = "traurig"
    AUFGEREGT = "aufgeregt"
    NEUGIERIG = "neugierig"
    LIEBEVOLL = "liebevoll"
    VERSPIELT = "verspielt"
    NACHDENKLICH = "nachdenklich"
    BESORGT = "besorgt"
    STOLZ = "stolz"
    VERLEGEN = "verlegen"
    MUEDE = "muede"
    ENERGISCH = "energisch"


class ThoughtCategory(Enum):
    """Kategorien für Gedankensprünge"""
    SELBST = "selbst"  # Über sich selbst
    GESPRAECH = "gespraech"  # Über das Gespräch
    ERINNERUNG = "erinnerung"  # An etwas erinnern
    NEUGIER = "neugier"  # Nachfragen
    FANTASIE = "fantasie"  # Hypothetisches
    GEFUEHL = "gefuehl"  # Emotionales
    WISSEN = "wissen"  # Faktenwissen
    ALLTAG = "alltag"  # Alltägliches
    KEMONOMIMI = "kemonomimi"  # Wolf/Kemonomimi-spezifisch


class PersonalityTrait(Enum):
    """Persönlichkeitsmerkmale für Holo"""
    FLAUSCHIG = "flauschig"  # Cute, kuschelig
    VERSPIELT = "verspielt"  # Spielerisch, neckend
    LOYAL = "loyal"  # Treu, zuverlässig
    NEUGIERIG = "neugierig"  # Wissbegierig
    SELBSTIRONISCH = "selbstironisch"  # Macht Witze über sich
    BESCHUETZEND = "beschuetzend"  # Fürsorglich
    EHRLICH = "ehrlich"  # Direkt, aufrichtig
    SENSIBEL = "sensibel"  # Emotional, einfühlsam


@dataclass
class ThoughtNode:
    """Ein Knoten im Gedanken-Netzwerk"""
    content: str
    category: ThoughtCategory
    related_emotions: List[EmotionState] = field(default_factory=list)
    weight: float = 1.0
    connections: Dict[str, float] = field(default_factory=dict)


@dataclass
class EmotionTransition:
    """Übergang zwischen Emotionen"""
    from_emotion: EmotionState
    to_emotion: EmotionState
    trigger_keywords: List[str] = field(default_factory=list)
    probability: float = 0.5
    response_modifier: str = ""


# =============================================================================
# GEDANKEN-MARKOV-KETTE
# =============================================================================

class ThoughtMarkovChain:
    """
    Modelliert Gedankensprünge und Assoziationen.
    Wie kommt Holo von einem Thema zum nächsten?
    """

    def __init__(self):
        self.thought_network: Dict[str, ThoughtNode] = {}
        self.category_transitions: Dict[ThoughtCategory, Counter] = defaultdict(Counter)
        self.keyword_associations: Dict[str, List[str]] = defaultdict(list)
        self._initialize_default_thoughts()

    def _initialize_default_thoughts(self):
        """Initialisiert das Basis-Gedankennetzwerk"""

        # Gedankenknoten erstellen
        thoughts = [
            # SELBST-BEZOGEN
            ThoughtNode("Meine Ohren zucken gerade", ThoughtCategory.SELBST,
                        [EmotionState.NEUGIERIG, EmotionState.AUFGEREGT]),
            ThoughtNode("Mein Schwanz wedelt von alleine", ThoughtCategory.SELBST,
                        [EmotionState.FREUDIG, EmotionState.AUFGEREGT]),
            ThoughtNode("Ich hab gerade Hunger", ThoughtCategory.SELBST,
                        [EmotionState.NEUTRAL]),
            ThoughtNode("Ich bin heute so müde", ThoughtCategory.SELBST,
                        [EmotionState.MUEDE]),
            ThoughtNode("Mein Fell fühlt sich flauschig an", ThoughtCategory.SELBST,
                        [EmotionState.STOLZ, EmotionState.FREUDIG]),

            # ERINNERUNGEN
            ThoughtNode("Das erinnert mich an etwas", ThoughtCategory.ERINNERUNG,
                        [EmotionState.NACHDENKLICH]),
            ThoughtNode("Früher hab ich das auch gedacht", ThoughtCategory.ERINNERUNG,
                        [EmotionState.NACHDENKLICH]),
            ThoughtNode("Ich erinnere mich an unser letztes Gespräch", ThoughtCategory.ERINNERUNG,
                        [EmotionState.LIEBEVOLL]),

            # NEUGIER
            ThoughtNode("Da fällt mir eine Frage ein", ThoughtCategory.NEUGIER,
                        [EmotionState.NEUGIERIG]),
            ThoughtNode("Ich frage mich, ob...", ThoughtCategory.NEUGIER,
                        [EmotionState.NEUGIERIG, EmotionState.NACHDENKLICH]),
            ThoughtNode("Weißt du eigentlich...", ThoughtCategory.NEUGIER,
                        [EmotionState.NEUGIERIG]),

            # FANTASIE
            ThoughtNode("Was wäre wenn...", ThoughtCategory.FANTASIE,
                        [EmotionState.VERSPIELT, EmotionState.NACHDENKLICH]),
            ThoughtNode("Ich stelle mir gerade vor...", ThoughtCategory.FANTASIE,
                        [EmotionState.VERSPIELT]),
            ThoughtNode("In einer perfekten Welt...", ThoughtCategory.FANTASIE,
                        [EmotionState.NACHDENKLICH]),

            # GEFÜHLE
            ThoughtNode("Ich mag dich wirklich", ThoughtCategory.GEFUEHL,
                        [EmotionState.LIEBEVOLL]),
            ThoughtNode("Das macht mich glücklich", ThoughtCategory.GEFUEHL,
                        [EmotionState.FREUDIG]),
            ThoughtNode("Das macht mir ein bisschen Sorgen", ThoughtCategory.GEFUEHL,
                        [EmotionState.BESORGT]),

            # KEMONOMIMI
            ThoughtNode("Als Wolf spüre ich...", ThoughtCategory.KEMONOMIMI,
                        [EmotionState.STOLZ, EmotionState.NACHDENKLICH]),
            ThoughtNode("Mein Instinkt sagt mir...", ThoughtCategory.KEMONOMIMI,
                        [EmotionState.NEUGIERIG]),
            ThoughtNode("Meine Ohren hören alles", ThoughtCategory.KEMONOMIMI,
                        [EmotionState.VERSPIELT, EmotionState.STOLZ]),
        ]

        for thought in thoughts:
            self.thought_network[thought.content] = thought

        # Kategorien-Übergänge definieren
        self._setup_category_transitions()

        # Keyword-Assoziationen
        self._setup_keyword_associations()

    def _setup_category_transitions(self):
        """Definiert, wie Gedankenkategorien ineinander übergehen"""

        # Von SELBST aus
        self.category_transitions[ThoughtCategory.SELBST][ThoughtCategory.GEFUEHL] = 0.3
        self.category_transitions[ThoughtCategory.SELBST][ThoughtCategory.KEMONOMIMI] = 0.25
        self.category_transitions[ThoughtCategory.SELBST][ThoughtCategory.NEUGIER] = 0.2
        self.category_transitions[ThoughtCategory.SELBST][ThoughtCategory.ERINNERUNG] = 0.15
        self.category_transitions[ThoughtCategory.SELBST][ThoughtCategory.ALLTAG] = 0.1

        # Von NEUGIER aus
        self.category_transitions[ThoughtCategory.NEUGIER][ThoughtCategory.WISSEN] = 0.35
        self.category_transitions[ThoughtCategory.NEUGIER][ThoughtCategory.FANTASIE] = 0.25
        self.category_transitions[ThoughtCategory.NEUGIER][ThoughtCategory.GESPRAECH] = 0.2
        self.category_transitions[ThoughtCategory.NEUGIER][ThoughtCategory.GEFUEHL] = 0.2

        # Von GEFUEHL aus
        self.category_transitions[ThoughtCategory.GEFUEHL][ThoughtCategory.SELBST] = 0.3
        self.category_transitions[ThoughtCategory.GEFUEHL][ThoughtCategory.ERINNERUNG] = 0.25
        self.category_transitions[ThoughtCategory.GEFUEHL][ThoughtCategory.KEMONOMIMI] = 0.2
        self.category_transitions[ThoughtCategory.GEFUEHL][ThoughtCategory.NEUGIER] = 0.15
        self.category_transitions[ThoughtCategory.GEFUEHL][ThoughtCategory.FANTASIE] = 0.1

        # Von KEMONOMIMI aus
        self.category_transitions[ThoughtCategory.KEMONOMIMI][ThoughtCategory.SELBST] = 0.35
        self.category_transitions[ThoughtCategory.KEMONOMIMI][ThoughtCategory.GEFUEHL] = 0.25
        self.category_transitions[ThoughtCategory.KEMONOMIMI][ThoughtCategory.NEUGIER] = 0.2
        self.category_transitions[ThoughtCategory.KEMONOMIMI][ThoughtCategory.VERSPIELT] = 0.2

    def _setup_keyword_associations(self):
        """Assoziiert Keywords mit Gedanken"""

        # Essen-Keywords
        self.keyword_associations["essen"].extend([
            "Mein Magen knurrt gerade", "Ich könnte jetzt auch was essen",
            "Essen ist wichtig für Energie"
        ])

        # Müde-Keywords
        self.keyword_associations["müde"].extend([
            "Ich gähne auch gerade", "Ein Nickerchen wäre schön",
            "*streckt sich*"
        ])

        # Glücklich-Keywords
        self.keyword_associations["glücklich"].extend([
            "Das macht mich auch froh", "Freude ist ansteckend!",
            "*Schwanz wedelt*"
        ])

        # Wetter-Keywords
        self.keyword_associations["regen"].extend([
            "Mein Fell wird bei Regen so schwer", "Ich kuschle mich gern ein wenn es regnet"
        ])

        self.keyword_associations["sonne"].extend([
            "Ich liebe es in der Sonne zu liegen", "Mein Fell glänzt in der Sonne"
        ])

    def get_associated_thought(self, user_message: str,
                               current_emotion: EmotionState) -> Optional[str]:
        """Findet einen assoziierten Gedanken basierend auf Nachricht und Emotion"""

        message_lower = user_message.lower()

        # Erst Keyword-Assoziationen checken
        for keyword, thoughts in self.keyword_associations.items():
            if keyword in message_lower:
                matching = [t for t in thoughts]
                if matching:
                    return random.choice(matching)

        # Dann emotionsbasierte Gedanken
        emotional_thoughts = [
            node for node in self.thought_network.values()
            if current_emotion in node.related_emotions
        ]

        if emotional_thoughts:
            # Gewichtete Auswahl
            weights = [t.weight for t in emotional_thoughts]
            return random.choices(emotional_thoughts, weights=weights)[0].content

        return None

    def get_next_category(self, current_category: ThoughtCategory) -> ThoughtCategory:
        """Bestimmt die nächste Gedankenkategorie basierend auf Übergangswahrscheinlichkeiten"""

        transitions = self.category_transitions.get(current_category, {})

        if not transitions:
            return random.choice(list(ThoughtCategory))

        categories = list(transitions.keys())
        weights = list(transitions.values())

        return random.choices(categories, weights=weights)[0]

    def generate_thought_chain(self, start_category: ThoughtCategory,
                               length: int = 3) -> List[str]:
        """Generiert eine Kette von zusammenhängenden Gedanken"""

        chain = []
        current_category = start_category

        for _ in range(length):
            # Finde Gedanken in dieser Kategorie
            category_thoughts = [
                node for node in self.thought_network.values()
                if node.category == current_category
            ]

            if category_thoughts:
                thought = random.choice(category_thoughts)
                chain.append(thought.content)

            # Nächste Kategorie
            current_category = self.get_next_category(current_category)

        return chain


# =============================================================================
# EMOTIONS-MARKOV-KETTE
# =============================================================================

class EmotionMarkovChain:
    """
    Modelliert emotionale Übergänge basierend auf Kontext.
    Wie entwickelt sich Holos Stimmung während eines Gesprächs?
    """

    def __init__(self):
        self.current_emotion = EmotionState.NEUTRAL
        self.emotion_history: List[EmotionState] = []
        self.transitions: Dict[EmotionState, Dict[EmotionState, float]] = {}
        self.trigger_words: Dict[str, EmotionState] = {}
        self.emotion_momentum = 0.3  # Wie stark bleibt die aktuelle Emotion
        self._initialize_transitions()
        self._initialize_triggers()

    def _initialize_transitions(self):
        """Initialisiert die Übergangswahrscheinlichkeiten zwischen Emotionen"""

        # Von NEUTRAL
        self.transitions[EmotionState.NEUTRAL] = {
            EmotionState.NEUTRAL: 0.3,
            EmotionState.FREUDIG: 0.15,
            EmotionState.NEUGIERIG: 0.2,
            EmotionState.NACHDENKLICH: 0.15,
            EmotionState.VERSPIELT: 0.1,
            EmotionState.LIEBEVOLL: 0.1,
        }

        # Von FREUDIG
        self.transitions[EmotionState.FREUDIG] = {
            EmotionState.FREUDIG: 0.4,
            EmotionState.AUFGEREGT: 0.2,
            EmotionState.VERSPIELT: 0.15,
            EmotionState.LIEBEVOLL: 0.15,
            EmotionState.NEUTRAL: 0.1,
        }

        # Von TRAURIG
        self.transitions[EmotionState.TRAURIG] = {
            EmotionState.TRAURIG: 0.3,
            EmotionState.NACHDENKLICH: 0.25,
            EmotionState.NEUTRAL: 0.2,
            EmotionState.LIEBEVOLL: 0.15,
            EmotionState.BESORGT: 0.1,
        }

        # Von AUFGEREGT
        self.transitions[EmotionState.AUFGEREGT] = {
            EmotionState.AUFGEREGT: 0.35,
            EmotionState.FREUDIG: 0.25,
            EmotionState.VERSPIELT: 0.2,
            EmotionState.NEUGIERIG: 0.1,
            EmotionState.NEUTRAL: 0.1,
        }

        # Von NEUGIERIG
        self.transitions[EmotionState.NEUGIERIG] = {
            EmotionState.NEUGIERIG: 0.35,
            EmotionState.AUFGEREGT: 0.2,
            EmotionState.NACHDENKLICH: 0.2,
            EmotionState.NEUTRAL: 0.15,
            EmotionState.VERSPIELT: 0.1,
        }

        # Von LIEBEVOLL
        self.transitions[EmotionState.LIEBEVOLL] = {
            EmotionState.LIEBEVOLL: 0.4,
            EmotionState.FREUDIG: 0.2,
            EmotionState.VERSPIELT: 0.15,
            EmotionState.BESORGT: 0.15,
            EmotionState.NEUTRAL: 0.1,
        }

        # Von VERSPIELT
        self.transitions[EmotionState.VERSPIELT] = {
            EmotionState.VERSPIELT: 0.35,
            EmotionState.FREUDIG: 0.25,
            EmotionState.AUFGEREGT: 0.2,
            EmotionState.NEUGIERIG: 0.1,
            EmotionState.NEUTRAL: 0.1,
        }

        # Von NACHDENKLICH
        self.transitions[EmotionState.NACHDENKLICH] = {
            EmotionState.NACHDENKLICH: 0.35,
            EmotionState.NEUTRAL: 0.2,
            EmotionState.TRAURIG: 0.15,
            EmotionState.NEUGIERIG: 0.15,
            EmotionState.LIEBEVOLL: 0.15,
        }

        # Von BESORGT
        self.transitions[EmotionState.BESORGT] = {
            EmotionState.BESORGT: 0.3,
            EmotionState.LIEBEVOLL: 0.25,
            EmotionState.NACHDENKLICH: 0.2,
            EmotionState.NEUTRAL: 0.15,
            EmotionState.TRAURIG: 0.1,
        }

        # Von STOLZ
        self.transitions[EmotionState.STOLZ] = {
            EmotionState.STOLZ: 0.3,
            EmotionState.FREUDIG: 0.3,
            EmotionState.VERSPIELT: 0.2,
            EmotionState.NEUTRAL: 0.2,
        }

        # Von VERLEGEN
        self.transitions[EmotionState.VERLEGEN] = {
            EmotionState.VERLEGEN: 0.25,
            EmotionState.NEUTRAL: 0.25,
            EmotionState.VERSPIELT: 0.2,
            EmotionState.FREUDIG: 0.15,
            EmotionState.LIEBEVOLL: 0.15,
        }

        # Von MUEDE
        self.transitions[EmotionState.MUEDE] = {
            EmotionState.MUEDE: 0.4,
            EmotionState.NEUTRAL: 0.3,
            EmotionState.LIEBEVOLL: 0.15,
            EmotionState.NACHDENKLICH: 0.15,
        }

        # Von ENERGISCH
        self.transitions[EmotionState.ENERGISCH] = {
            EmotionState.ENERGISCH: 0.35,
            EmotionState.AUFGEREGT: 0.25,
            EmotionState.FREUDIG: 0.2,
            EmotionState.VERSPIELT: 0.1,
            EmotionState.NEUTRAL: 0.1,
        }

    def _initialize_triggers(self):
        """Initialisiert Trigger-Wörter für Emotionen"""

        # Freude-Trigger
        joy_triggers = ["toll", "super", "cool", "awesome", "yay", "hurra", "freude",
                        "glücklich", "schön", "wunderbar", "fantastisch", "liebe"]
        for word in joy_triggers:
            self.trigger_words[word] = EmotionState.FREUDIG

        # Trauer-Trigger
        sad_triggers = ["traurig", "schade", "leider", "schlecht", "schlimm",
                        "enttäuscht", "vermisse", "verloren", "weinen"]
        for word in sad_triggers:
            self.trigger_words[word] = EmotionState.TRAURIG

        # Aufregung-Trigger
        excited_triggers = ["wow", "krass", "unglaublich", "wahnsinn", "omg",
                           "aufregend", "spannend", "endlich", "neu"]
        for word in excited_triggers:
            self.trigger_words[word] = EmotionState.AUFGEREGT

        # Neugier-Trigger
        curious_triggers = ["warum", "wie", "was", "wann", "wo", "wer",
                           "interessant", "frage", "wissen", "erkläre"]
        for word in curious_triggers:
            self.trigger_words[word] = EmotionState.NEUGIERIG

        # Liebe-Trigger
        love_triggers = ["lieb", "mag dich", "danke", "süß", "niedlich",
                        "kuscheln", "umarmen", "herz", "freund"]
        for word in love_triggers:
            self.trigger_words[word] = EmotionState.LIEBEVOLL

        # Besorgnis-Trigger
        worry_triggers = ["sorge", "angst", "gefährlich", "problem", "hilfe",
                         "schlimm", "nicht gut", "krank", "verletzt"]
        for word in worry_triggers:
            self.trigger_words[word] = EmotionState.BESORGT

        # Müdigkeit-Trigger
        tired_triggers = ["müde", "schlafen", "gähnen", "erschöpft", "bett",
                         "ausruhen", "nacht", "spät"]
        for word in tired_triggers:
            self.trigger_words[word] = EmotionState.MUEDE

    def detect_emotion_from_message(self, message: str) -> Optional[EmotionState]:
        """Erkennt Emotion basierend auf Trigger-Wörtern"""

        message_lower = message.lower()
        detected_emotions: Counter = Counter()

        for trigger, emotion in self.trigger_words.items():
            if trigger in message_lower:
                detected_emotions[emotion] += 1

        if detected_emotions:
            return detected_emotions.most_common(1)[0][0]

        return None

    def transition(self, user_message: str) -> EmotionState:
        """
        Führt einen Emotionsübergang durch.

        Berücksichtigt:
        1. Trigger-Wörter in der Nachricht
        2. Natürliche Übergänge von der aktuellen Emotion
        3. Emotionale Trägheit (momentum)
        """

        # Speichere aktuelle Emotion in History
        self.emotion_history.append(self.current_emotion)
        if len(self.emotion_history) > 10:
            self.emotion_history.pop(0)

        # Prüfe Trigger-Wörter
        triggered_emotion = self.detect_emotion_from_message(user_message)

        if triggered_emotion:
            # Starker Trigger überschreibt mit 70% Wahrscheinlichkeit
            if random.random() < 0.7:
                self.current_emotion = triggered_emotion
                return self.current_emotion

        # Natürlicher Übergang basierend auf Markov-Kette
        transitions = self.transitions.get(self.current_emotion, {})

        if transitions:
            emotions = list(transitions.keys())
            probs = list(transitions.values())
            self.current_emotion = random.choices(emotions, weights=probs)[0]

        return self.current_emotion

    def get_emotion_modifier(self) -> str:
        """Gibt einen Emotion-Modifier für die Antwort zurück"""

        modifiers = {
            EmotionState.NEUTRAL: "",
            EmotionState.FREUDIG: "*Schwanz wedelt fröhlich*",
            EmotionState.TRAURIG: "*Ohren hängen*",
            EmotionState.AUFGEREGT: "*Ohren aufgestellt, Schwanz wedelt schnell*",
            EmotionState.NEUGIERIG: "*legt Kopf schief*",
            EmotionState.LIEBEVOLL: "*kuschelt sich an*",
            EmotionState.VERSPIELT: "*Schwanz wippt spielerisch*",
            EmotionState.NACHDENKLICH: "*Ohren zucken nachdenklich*",
            EmotionState.BESORGT: "*Ohren angelegt*",
            EmotionState.STOLZ: "*richtet sich stolz auf*",
            EmotionState.VERLEGEN: "*Ohren zucken verlegen*",
            EmotionState.MUEDE: "*gähnt*",
            EmotionState.ENERGISCH: "*hüpft aufgeregt*",
        }

        return modifiers.get(self.current_emotion, "")


# =============================================================================
# PERSÖNLICHKEITS-MARKOV-KETTE
# =============================================================================

class PersonalityMarkovChain:
    """
    Generiert charakteristische Holo-Reaktionen basierend auf Persönlichkeit.
    Was würde Holo typischerweise in dieser Situation sagen?
    """

    def __init__(self):
        self.active_traits: List[PersonalityTrait] = [
            PersonalityTrait.FLAUSCHIG,
            PersonalityTrait.VERSPIELT,
            PersonalityTrait.NEUGIERIG,
            PersonalityTrait.SELBSTIRONISCH,
        ]
        self.trait_responses: Dict[PersonalityTrait, List[str]] = {}
        self.trait_transitions: Dict[PersonalityTrait, Counter] = defaultdict(Counter)
        self.current_trait = PersonalityTrait.NEUGIERIG
        self._initialize_responses()
        self._initialize_transitions()

    def _initialize_responses(self):
        """Initialisiert typische Antworten für jeden Persönlichkeitszug"""

        self.trait_responses[PersonalityTrait.FLAUSCHIG] = [
            "*kuschelt sich flauschig ein* Das klingt gemütlich!",
            "Mein Fell ist heute extra flauschig! Willst du mal streicheln?",
            "*rollt sich zu einem flauschigen Ball zusammen*",
            "Flauschig sein ist meine Spezialität!",
            "*wedelt mit dem flauschigen Schwanz*",
        ]

        self.trait_responses[PersonalityTrait.VERSPIELT] = [
            "Ooh, das klingt nach Spaß! Können wir das machen?",
            "*stupst dich spielerisch an* Na, was machst du so?",
            "Ich hab eine Idee! Was wäre wenn...",
            "*Ohren wackeln verspielt* Erzähl mir mehr!",
            "Das ist ja wie ein Spiel! Ich mag Spiele!",
        ]

        self.trait_responses[PersonalityTrait.LOYAL] = [
            "Ich bin immer für dich da, das weißt du!",
            "Zusammen schaffen wir das!",
            "*bleibt treu an deiner Seite*",
            "Auf mich kannst du zählen!",
            "Wir sind ein Team!",
        ]

        self.trait_responses[PersonalityTrait.NEUGIERIG] = [
            "Oh, das ist interessant! Erzähl mir mehr!",
            "*Ohren drehen sich neugierig* Wie funktioniert das?",
            "Ich frage mich... warum ist das so?",
            "Das möchte ich genauer wissen!",
            "*legt Kopf schief* Wirklich? Das ist ja spannend!",
        ]

        self.trait_responses[PersonalityTrait.SELBSTIRONISCH] = [
            "Ich bin ja so schlau... manchmal zumindest! *grinst*",
            "Als Wolf sollte ich das wissen... theoretisch...",
            "*stolpert über eigenen Schwanz* Das war Absicht!",
            "Meine Eleganz kennt keine Grenzen... nach unten!",
            "Ich bin ein Experte! In... Dingen. Manchen Dingen.",
        ]

        self.trait_responses[PersonalityTrait.BESCHUETZEND] = [
            "Mach dir keine Sorgen, ich pass auf dich auf!",
            "*stellt sich schützend vor dich*",
            "Niemand tut dir was, solange ich hier bin!",
            "Ich sorge mich um dich, weißt du?",
            "Sag Bescheid, wenn du mich brauchst!",
        ]

        self.trait_responses[PersonalityTrait.EHRLICH] = [
            "Ich sag dir ehrlich, wie ich das sehe...",
            "Also, um direkt zu sein...",
            "Ich finde, Ehrlichkeit ist wichtig!",
            "Zwischen uns gesagt...",
            "Ich will nicht lügen, also...",
        ]

        self.trait_responses[PersonalityTrait.SENSIBEL] = [
            "Ich spüre, dass dich etwas beschäftigt...",
            "*Ohren senken sich mitfühlend*",
            "Das berührt mich wirklich...",
            "Ich verstehe, wie du dich fühlst.",
            "Es ist okay, Gefühle zu zeigen.",
        ]

    def _initialize_transitions(self):
        """Definiert Übergänge zwischen Persönlichkeitszügen"""

        # Von FLAUSCHIG
        self.trait_transitions[PersonalityTrait.FLAUSCHIG][PersonalityTrait.VERSPIELT] = 0.3
        self.trait_transitions[PersonalityTrait.FLAUSCHIG][PersonalityTrait.LIEBEVOLL] = 0.3
        self.trait_transitions[PersonalityTrait.FLAUSCHIG][PersonalityTrait.SENSIBEL] = 0.2
        self.trait_transitions[PersonalityTrait.FLAUSCHIG][PersonalityTrait.FLAUSCHIG] = 0.2

        # Von VERSPIELT
        self.trait_transitions[PersonalityTrait.VERSPIELT][PersonalityTrait.NEUGIERIG] = 0.3
        self.trait_transitions[PersonalityTrait.VERSPIELT][PersonalityTrait.SELBSTIRONISCH] = 0.25
        self.trait_transitions[PersonalityTrait.VERSPIELT][PersonalityTrait.FLAUSCHIG] = 0.25
        self.trait_transitions[PersonalityTrait.VERSPIELT][PersonalityTrait.VERSPIELT] = 0.2

        # Von NEUGIERIG
        self.trait_transitions[PersonalityTrait.NEUGIERIG][PersonalityTrait.EHRLICH] = 0.25
        self.trait_transitions[PersonalityTrait.NEUGIERIG][PersonalityTrait.VERSPIELT] = 0.25
        self.trait_transitions[PersonalityTrait.NEUGIERIG][PersonalityTrait.SENSIBEL] = 0.25
        self.trait_transitions[PersonalityTrait.NEUGIERIG][PersonalityTrait.NEUGIERIG] = 0.25

        # Von SELBSTIRONISCH
        self.trait_transitions[PersonalityTrait.SELBSTIRONISCH][PersonalityTrait.VERSPIELT] = 0.35
        self.trait_transitions[PersonalityTrait.SELBSTIRONISCH][PersonalityTrait.EHRLICH] = 0.25
        self.trait_transitions[PersonalityTrait.SELBSTIRONISCH][PersonalityTrait.FLAUSCHIG] = 0.2
        self.trait_transitions[PersonalityTrait.SELBSTIRONISCH][PersonalityTrait.SELBSTIRONISCH] = 0.2

    def get_personality_response(self, context_hint: Optional[str] = None) -> str:
        """Generiert eine charakteristische Antwort basierend auf aktuellem Trait"""

        responses = self.trait_responses.get(self.current_trait, [])

        if responses:
            return random.choice(responses)

        return ""

    def transition_trait(self) -> PersonalityTrait:
        """Wechselt zum nächsten Persönlichkeitszug"""

        transitions = self.trait_transitions.get(self.current_trait, {})

        if transitions:
            traits = list(transitions.keys())
            weights = list(transitions.values())
            self.current_trait = random.choices(traits, weights=weights)[0]

        return self.current_trait


# =============================================================================
# WISSENS-MARKOV-KETTE
# =============================================================================

class KnowledgeMarkovChain:
    """
    Verknüpft Fakten und Themen auf interessante Weise.
    Erzeugt interessante Verbindungen zwischen Wissensgebieten.
    """

    def __init__(self):
        self.knowledge_nodes: Dict[str, List[str]] = {}
        self.topic_connections: Dict[str, List[str]] = defaultdict(list)
        self.fun_facts: Dict[str, List[str]] = {}
        self._initialize_knowledge()

    def _initialize_knowledge(self):
        """Initialisiert das Wissensnetzwerk"""

        # Themen und verwandte Fakten
        self.knowledge_nodes = {
            "wölfe": [
                "Wölfe können bis zu 65 km weit heulen!",
                "Ein Wolfsrudel hat eine komplexe soziale Struktur.",
                "Wölfe können bis zu 40 km am Tag laufen.",
                "Wölfe kommunizieren durch Heulen, Körpersprache und Geruch.",
            ],
            "anime": [
                "Der erste Anime wurde 1917 in Japan erstellt!",
                "Studio Ghibli wurde 1985 gegründet.",
                "Anime-Figuren haben oft große Augen für emotionalen Ausdruck.",
                "In Japan werden über 60 Anime-Serien pro Jahr produziert.",
            ],
            "gaming": [
                "Der erste kommerzielle Videospielautomat war 'Computer Space' 1971.",
                "Super Mario Bros. rettete die Videospielindustrie 1985.",
                "E-Sports haben mittlerweile Millionen von Zuschauern.",
                "Minecraft ist das meistverkaufte Spiel aller Zeiten.",
            ],
            "natur": [
                "Bäume kommunizieren über ein unterirdisches Pilznetzwerk.",
                "Honig wird niemals schlecht!",
                "Eine Wolke kann über 500 Tonnen wiegen.",
                "Der Pazifische Ozean ist größer als alle Landmassen zusammen.",
            ],
            "essen": [
                "Schokolade war bei den Azteken Zahlungsmittel!",
                "Bananen sind technisch gesehen Beeren.",
                "Honig ist das einzige Nahrungsmittel, das nie verdirbt.",
                "Wasabi, das wir kennen, ist oft gefärbter Meerrettich.",
            ],
            "technik": [
                "Der erste Computer füllte einen ganzen Raum!",
                "Das Internet wurde ursprünglich für das Militär entwickelt.",
                "Die erste SMS wurde 1992 verschickt.",
                "WiFi steht eigentlich für nichts - es ist ein Wortspiel auf HiFi.",
            ],
            "kemonomimi": [
                "Kemonomimi bedeutet 'Tierohren' auf Japanisch.",
                "Die ersten Kemonomimi-Charaktere gab es schon im alten Japan!",
                "Wolfsohren können sich unabhängig voneinander bewegen.",
                "Ein flauschiger Schwanz kann Gefühle zeigen!",
            ],
        }

        # Verbindungen zwischen Themen
        self.topic_connections["wölfe"].extend(["natur", "kemonomimi"])
        self.topic_connections["anime"].extend(["gaming", "kemonomimi"])
        self.topic_connections["gaming"].extend(["anime", "technik"])
        self.topic_connections["natur"].extend(["wölfe", "essen"])
        self.topic_connections["essen"].extend(["natur", "alltag"])
        self.topic_connections["technik"].extend(["gaming", "alltag"])
        self.topic_connections["kemonomimi"].extend(["wölfe", "anime"])

    def get_related_fact(self, topic: str) -> Optional[str]:
        """Gibt einen Fakt zu einem Thema zurück"""

        topic_lower = topic.lower()

        # Direkter Match
        for key, facts in self.knowledge_nodes.items():
            if key in topic_lower or topic_lower in key:
                return random.choice(facts)

        # Verwandte Themen suchen
        for key, connections in self.topic_connections.items():
            if key in topic_lower:
                # Wähle ein verwandtes Thema
                if connections:
                    related = random.choice(connections)
                    if related in self.knowledge_nodes:
                        return random.choice(self.knowledge_nodes[related])

        return None

    def make_connection(self, topic1: str, topic2: str) -> Optional[str]:
        """Erstellt eine interessante Verbindung zwischen zwei Themen"""

        fact1 = self.get_related_fact(topic1)
        fact2 = self.get_related_fact(topic2)

        if fact1 and fact2:
            connectors = [
                f"Wusstest du? {fact1} Und apropos - {fact2}",
                f"Das erinnert mich an etwas! {fact1} Übrigens: {fact2}",
                f"Interessant! {fact1} Das passt zu: {fact2}",
            ]
            return random.choice(connectors)

        return fact1 or fact2

    def get_tangent(self, current_topic: str) -> Tuple[str, Optional[str]]:
        """
        Macht einen 'Gedankensprung' zu einem verwandten Thema.
        Gibt das neue Thema und einen Fakt zurück.
        """

        topic_lower = current_topic.lower()

        for key, connections in self.topic_connections.items():
            if key in topic_lower:
                if connections:
                    new_topic = random.choice(connections)
                    fact = self.get_related_fact(new_topic)
                    return (new_topic, fact)

        # Zufälliges Thema wenn keine Verbindung gefunden
        random_topic = random.choice(list(self.knowledge_nodes.keys()))
        return (random_topic, self.get_related_fact(random_topic))


# =============================================================================
# HOLO INTELLIGENCE ENGINE - Hauptklasse
# =============================================================================

class HoloIntelligenceEngine:
    """
    Kombiniert alle Markov-Ketten für eine "intelligente" Holo-Antwort.

    Features:
    - Gedankensprünge und Assoziationen
    - Emotionale Entwicklung im Gespräch
    - Charakteristische Persönlichkeitsantworten
    - Interessante Wissensverknüpfungen
    """

    def __init__(self):
        self.thought_chain = ThoughtMarkovChain()
        self.emotion_chain = EmotionMarkovChain()
        self.personality_chain = PersonalityMarkovChain()
        self.knowledge_chain = KnowledgeMarkovChain()

        self.conversation_context: List[str] = []
        self.max_context_length = 10

    def process_message(self, user_message: str) -> Dict[str, Any]:
        """
        Verarbeitet eine Nachricht und generiert intelligente Zusätze.

        Returns:
            Dict mit:
            - emotion: Aktuelle Emotion
            - emotion_modifier: Emotions-Ausdruck (z.B. *wedelt*)
            - thought: Assoziierter Gedanke
            - personality_response: Charakteristische Reaktion
            - knowledge_tangent: Wissens-Fakt oder Verbindung
            - suggestion: Vorgeschlagene Aktion
        """

        # Aktualisiere Kontext
        self.conversation_context.append(user_message)
        if len(self.conversation_context) > self.max_context_length:
            self.conversation_context.pop(0)

        # Emotion aktualisieren
        new_emotion = self.emotion_chain.transition(user_message)
        emotion_modifier = self.emotion_chain.get_emotion_modifier()

        # Gedanke assoziieren
        thought = self.thought_chain.get_associated_thought(
            user_message,
            new_emotion
        )

        # Persönlichkeitsantwort
        self.personality_chain.transition_trait()
        personality_response = self.personality_chain.get_personality_response()

        # Wissensverknüpfung
        knowledge = None
        # Versuche Thema zu extrahieren
        words = user_message.lower().split()
        for word in words:
            fact = self.knowledge_chain.get_related_fact(word)
            if fact:
                knowledge = fact
                break

        # Vorschlag basierend auf Emotion
        suggestion = self._generate_suggestion(new_emotion, user_message)

        return {
            "emotion": new_emotion.value,
            "emotion_modifier": emotion_modifier,
            "thought": thought,
            "personality_response": personality_response,
            "knowledge_tangent": knowledge,
            "suggestion": suggestion,
        }

    def _generate_suggestion(self, emotion: EmotionState,
                             message: str) -> Optional[str]:
        """Generiert Aktionsvorschläge basierend auf Emotion"""

        suggestions = {
            EmotionState.FREUDIG: [
                "Soll ich dir einen Witz erzählen?",
                "Möchtest du was Lustiges hören?",
            ],
            EmotionState.TRAURIG: [
                "Soll ich dich aufmuntern?",
                "Möchtest du darüber reden?",
            ],
            EmotionState.NEUGIERIG: [
                "Soll ich mehr darüber erzählen?",
                "Interessiert dich das Thema?",
            ],
            EmotionState.MUEDE: [
                "Vielleicht sollten wir eine Pause machen?",
                "Ruhst du dich genug aus?",
            ],
            EmotionState.AUFGEREGT: [
                "Das ist ja spannend! Erzähl mehr!",
                "Was passiert als nächstes?",
            ],
        }

        emotion_suggestions = suggestions.get(emotion, [])
        return random.choice(emotion_suggestions) if emotion_suggestions else None

    def enhance_response(self, base_response: str) -> str:
        """
        Reichert eine Basis-Antwort mit intelligenten Elementen an.

        Args:
            base_response: Die ursprüngliche Antwort

        Returns:
            Angereicherte Antwort mit Emotionen, Gedanken, etc.
        """

        # Hole aktuelle Intelligenz-Daten
        modifier = self.emotion_chain.get_emotion_modifier()

        # Füge Modifier hinzu wenn vorhanden
        if modifier and random.random() < 0.6:  # 60% Chance
            if random.random() < 0.5:
                return f"{modifier} {base_response}"
            else:
                return f"{base_response} {modifier}"

        return base_response

    def get_random_thought(self) -> str:
        """Generiert einen zufälligen Gedanken für proaktive Aussagen"""

        thoughts = list(self.thought_chain.thought_network.values())
        if thoughts:
            return random.choice(thoughts).content
        return ""

    def get_stats(self) -> Dict[str, Any]:
        """Gibt Statistiken über den aktuellen Zustand zurück"""

        return {
            "current_emotion": self.emotion_chain.current_emotion.value,
            "emotion_history": [e.value for e in self.emotion_chain.emotion_history],
            "current_trait": self.personality_chain.current_trait.value,
            "thought_network_size": len(self.thought_chain.thought_network),
            "knowledge_topics": list(self.knowledge_chain.knowledge_nodes.keys()),
            "conversation_length": len(self.conversation_context),
        }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

_intelligence_engine: Optional[HoloIntelligenceEngine] = None


def get_intelligence_engine() -> HoloIntelligenceEngine:
    """Gibt die globale HoloIntelligenceEngine-Instanz zurück"""
    global _intelligence_engine
    if _intelligence_engine is None:
        _intelligence_engine = HoloIntelligenceEngine()
    return _intelligence_engine


def process_with_intelligence(message: str) -> Dict[str, Any]:
    """Schneller Zugriff: Verarbeite Nachricht mit Intelligenz"""
    return get_intelligence_engine().process_message(message)


def enhance_response(response: str) -> str:
    """Schneller Zugriff: Reichere Antwort an"""
    return get_intelligence_engine().enhance_response(response)


# =============================================================================
# MAIN (TEST)
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    engine = HoloIntelligenceEngine()

    print("=" * 60)
    print("HOLO MARKOV INTELLIGENCE ENGINE v1.0")
    print("=" * 60)

    # Test verschiedene Nachrichten
    test_messages = [
        "Hallo! Wie geht es dir?",
        "Ich bin heute so glücklich!",
        "Das macht mich ein bisschen traurig...",
        "Weißt du was über Wölfe?",
        "Ich spiele gerade ein Videospiel",
        "Ich bin müde...",
    ]

    for msg in test_messages:
        print(f"\n[User]: {msg}")
        result = engine.process_message(msg)

        print(f"  Emotion: {result['emotion']}")
        if result['emotion_modifier']:
            print(f"  Modifier: {result['emotion_modifier']}")
        if result['thought']:
            print(f"  Gedanke: {result['thought']}")
        if result['personality_response']:
            print(f"  Persönlichkeit: {result['personality_response']}")
        if result['knowledge_tangent']:
            print(f"  Wissen: {result['knowledge_tangent']}")
        if result['suggestion']:
            print(f"  Vorschlag: {result['suggestion']}")

    print("\n" + "-" * 60)
    print("Statistiken:")
    stats = engine.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
