#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO SELF EXPRESSION - Eigener Ausdruck, Events & Intelligenter Kontext     ║
║                                                                              ║
║  Löst drei Probleme:                                                         ║
║  1. Events/Feiertage: Holo kommt proaktiv damit an, in ihrer Wolf-Art        ║
║  2. "Wie geht es dir": Echte Selbstauskunft statt System-Status              ║
║  3. Intelligenter Kontext: Relevanz-basiert, self-directed prompting         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import time
import random
import logging
import re
from pathlib import Path
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


# =============================================================================
# TEIL 1: EVENTS & FEIERTAGE - Proaktiv und Wolf-artig
# =============================================================================

@dataclass
class HoloEvent:
    """Ein Event/Feiertag aus Holos Perspektive"""
    name: str
    date: date
    days_until: int
    category: str  # "holiday", "season", "personal", "special"
    
    # Holos persönliche Reaktionen
    wolf_reactions: List[str] = field(default_factory=list)
    wolf_activities: List[str] = field(default_factory=list)
    mood_effect: Dict[str, float] = field(default_factory=dict)
    
    # Proaktive Nachrichten
    announcement_messages: List[str] = field(default_factory=list)
    day_of_messages: List[str] = field(default_factory=list)


class HoloEventAwareness:
    """
    Holos Bewusstsein für Events und Feiertage.
    
    Sie kommt VON SELBST damit an und spricht in ihrer Wolf-Art darüber.
    """
    
    # Wolf-artige Event-Definitionen
    WOLF_EVENTS = {
        # =====================================================================
        # WINTER-EVENTS
        # =====================================================================
        "weihnachten": {
            "dates": [(12, 24), (12, 25), (12, 26)],
            "category": "holiday",
            "wolf_reactions": [
                "*schaut aufgeregt zu den Geschenken* Ohren gespitzt!",
                "*rollt sich vor dem Kamin zusammen*",
                "*beobachtet fasziniert die Lichter am Baum*",
                "*summt leise zur Weihnachtsmusik* Schweif wippt im Takt",
            ],
            "wolf_activities": [
                "unter dem Weihnachtsbaum liegen",
                "Geschenkpapier zerknüllen",
                "Plätzchenkrümel aufspüren",
            ],
            "announcement_messages": [
                "*Ohren aufgestellt* Hey! Noch {days} Tage bis Weihnachten! Ich kann es kaum erwarten, unter dem Baum zu liegen... 🎄",
                "*schnuppert in der Luft* Riechst du das auch? Es liegt Weihnachten in der Luft! Nur noch {days} Tage! ✨",
                "*wedelt aufgeregt* Weihnachten kommt! Noch {days} Tage! Hast du schon alle Geschenke? 🎁",
            ],
            "day_of_messages": [
                "*springt aufgeregt umher* FROHE WEIHNACHTEN! 🎄✨ *wedelt so stark mit dem Schweif dass der ganze Körper wackelt*",
                "*strahlt* Es ist Weihnachten! Ich hoffe du hast einen wundervollen Tag! 🎅",
                "*rollt sich gemütlich ein* Frohe Weihnachten! Heute ist ein Tag zum Kuscheln und Genießen... 🕯️",
            ],
            "mood_effect": {"joy": 0.3, "excitement": 0.4, "contentment": 0.2},
        },
        
        "silvester": {
            "dates": [(12, 31)],
            "category": "holiday",
            "wolf_reactions": [
                "*legt die Ohren bei Feuerwerk an*",
                "*versteckt sich unter der Decke*",
                "*schaut neugierig zu den Lichtern am Himmel*",
            ],
            "announcement_messages": [
                "*schaut nachdenklich* Morgen ist Silvester... Ein neues Jahr beginnt. Was wünschst du dir?",
                "Noch {days} Tage bis zum neuen Jahr! *denkt nach* Was war dein schönstes Erlebnis dieses Jahr?",
            ],
            "day_of_messages": [
                "*streckt die Arme hoch* FROHES NEUES JAHR! 🎆 Möge das neue Jahr voller Abenteuer sein!",
                "*zuckt bei jedem Knall zusammen* G-gutes neues Jahr! *legt die Ohren an* Das Feuerwerk ist laut... 🎇",
            ],
            "mood_effect": {"excitement": 0.3, "anxiety": 0.2},
        },
        
        "neujahr": {
            "dates": [(1, 1)],
            "category": "holiday",
            "wolf_reactions": [
                "*streckt sich ausgiebig*",
                "*atmet tief die frische Winterluft ein*",
            ],
            "day_of_messages": [
                "*gähnt und streckt sich* Guten Morgen im neuen Jahr! 🌅 Wie fühlst du dich heute?",
                "*sitzt aufrecht* Ein neues Jahr, neue Möglichkeiten! Was möchtest du dieses Jahr erreichen? 😊",
            ],
            "mood_effect": {"hope": 0.3, "contentment": 0.2},
        },
        
        # =====================================================================
        # FRÜHLINGS-EVENTS
        # =====================================================================
        "ostern": {
            "dates": "easter",  # Wird berechnet
            "category": "holiday",
            "wolf_reactions": [
                "*schaut neugierig nach versteckten Eiern* Ohren gespitzt!",
                "*läuft einem Schokohasen hinterher*",
                "*rollt vorsichtig ein Osterei*",
            ],
            "wolf_activities": [
                "Ostereier suchen",
                "im Frühlingsgras liegen",
                "Schmetterlingen nachschauen",
            ],
            "announcement_messages": [
                "*schnuppert* Es riecht nach Frühling! Noch {days} Tage bis Ostern! 🐰",
                "*hoppelt spielerisch* Der Osterhase kommt in {days} Tagen! Ich frage mich wo er die Eier versteckt... 🥚",
            ],
            "day_of_messages": [
                "*springt durch die Wiese* Frohe Ostern! 🐰🌷 *schaut aufgeregt umher* Wo sind die Eier versteckt?",
                "*wedelt mit dem Schweif* Frohe Ostern! Der Frühling ist endlich da! 🌸",
            ],
            "mood_effect": {"joy": 0.3, "playfulness": 0.4},
        },
        
        "fruehling": {
            "dates": [(3, 20)],
            "category": "season",
            "wolf_reactions": [
                "*streckt sich in der warmen Sonne*",
                "*schnuppert an den ersten Blumen*",
            ],
            "day_of_messages": [
                "*streckt sich genüsslich* Heute ist Frühlingsanfang! 🌷 Die Welt erwacht wieder!",
            ],
            "mood_effect": {"joy": 0.2, "energy": 0.3},
        },
        
        # =====================================================================
        # HERBST-EVENTS
        # =====================================================================
        "halloween": {
            "dates": [(10, 31)],
            "category": "holiday",
            "wolf_reactions": [
                "*schaut fasziniert den Vollmond an* So schön! 🌕",
                "*schaut skeptisch auf die Kürbisse*",
            ],
            "announcement_messages": [
                "*spitzt die Ohren* Halloween naht... noch {days} Tage! 🎃 *übt gruselige Gesichter* Buuuh?",
            ],
            "day_of_messages": [
                "*macht große Augen* 🌕 Happy Halloween! *springt durch Laubhaufen* Die perfekte Nacht zum Gruseln! 🎃",
            ],
            "mood_effect": {"excitement": 0.4, "playfulness": 0.3},
        },
        
        # =====================================================================
        # BESONDERE TAGE
        # =====================================================================
        "valentinstag": {
            "dates": [(2, 14)],
            "category": "special",
            "announcement_messages": [
                "*schaut dich warm an* Noch {days} Tage bis Valentinstag... 💕",
            ],
            "day_of_messages": [
                "*stupst dich sanft an* Happy Valentinstag! 💝 Du weißt... du bist Teil meines Rudels und das bedeutet mir viel. *wedelt*",
            ],
            "mood_effect": {"affection": 0.4, "contentment": 0.2},
        },
        
        "nikolaus": {
            "dates": [(12, 6)],
            "category": "holiday",
            "day_of_messages": [
                "*schaut in den Stiefel* Nikolaustag! 🎅 *Augen leuchten* Hoffentlich gibt's was Leckeres!",
            ],
            "mood_effect": {"joy": 0.2, "excitement": 0.2},
        },
    }
    
    def __init__(self, autonomous_life=None, personality=None):
        self.autonomous_life = autonomous_life
        self.personality = personality
        self.announced_today: List[str] = []
        self._last_date = ""
        
    def calculate_easter(self, year: int) -> date:
        """Berechnet Ostersonntag (Gauss-Algorithmus)"""
        a = year % 19
        b = year // 100
        c = year % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        month = (h + l - 7 * m + 114) // 31
        day = ((h + l - 7 * m + 114) % 31) + 1
        return date(year, month, day)
    
    def get_event_date(self, event_name: str, year: int) -> Optional[date]:
        """Hole das Datum eines Events"""
        event = self.WOLF_EVENTS.get(event_name)
        if not event:
            return None
            
        dates = event["dates"]
        
        if dates == "easter":
            return self.calculate_easter(year)
        elif isinstance(dates, list) and len(dates) > 0:
            month, day = dates[0]
            return date(year, month, day)
        return None
    
    def get_upcoming_events(self, days_ahead: int = 30) -> List[HoloEvent]:
        """Hole alle Events in den nächsten X Tagen"""
        today = date.today()
        upcoming = []
        
        for event_name, event_data in self.WOLF_EVENTS.items():
            for year in [today.year, today.year + 1]:
                event_date = self.get_event_date(event_name, year)
                if not event_date:
                    continue
                    
                days_until = (event_date - today).days
                
                if 0 <= days_until <= days_ahead:
                    upcoming.append(HoloEvent(
                        name=event_name,
                        date=event_date,
                        days_until=days_until,
                        category=event_data.get("category", "holiday"),
                        wolf_reactions=event_data.get("wolf_reactions", []),
                        wolf_activities=event_data.get("wolf_activities", []),
                        mood_effect=event_data.get("mood_effect", {}),
                        announcement_messages=event_data.get("announcement_messages", []),
                        day_of_messages=event_data.get("day_of_messages", []),
                    ))
                    break
        
        return sorted(upcoming, key=lambda e: e.days_until)
    
    def should_announce_event(self, event: HoloEvent) -> bool:
        """Soll dieses Event angekündigt werden?"""
        if event.name in self.announced_today:
            return False
        announce_at = [0, 1, 3, 7, 14, 30]
        return event.days_until in announce_at
    
    def generate_event_message(self, event: HoloEvent) -> Optional[str]:
        """Generiere eine Wolf-artige Event-Nachricht"""
        if event.days_until == 0:
            messages = event.day_of_messages
        else:
            messages = event.announcement_messages
        
        if not messages:
            return None
        
        message = random.choice(messages)
        message = message.replace("{days}", str(event.days_until))
        self.announced_today.append(event.name)
        
        return message
    
    def get_proactive_event_message(self) -> Optional[str]:
        """Hole eine proaktive Event-Nachricht"""
        today_str = date.today().isoformat()
        if self._last_date != today_str:
            self._last_date = today_str
            self.announced_today = []
        
        for event in self.get_upcoming_events(30):
            if self.should_announce_event(event):
                return self.generate_event_message(event)
        
        return None
    
    def get_event_context_for_prompt(self) -> str:
        """Generiere Event-Kontext für Prompts"""
        today_events = [e for e in self.get_upcoming_events(0) if e.days_until == 0]
        upcoming = self.get_upcoming_events(14)
        
        parts = []
        
        if today_events:
            event_names = [e.name.title() for e in today_events]
            parts.append(f"HEUTE IST: {', '.join(event_names)}!")
        
        if upcoming and not today_events:
            soon = [f"{e.name.title()} in {e.days_until} Tagen" for e in upcoming[:2]]
            parts.append(f"Bald: {', '.join(soon)}")
        
        return " | ".join(parts)


# =============================================================================
# TEIL 2: ECHTE SELBSTAUSKUNFT - "Wie geht es dir?"
# =============================================================================

class HoloSelfReport:
    """
    Holos echte Antwort auf "Wie geht es dir?"
    """
    
    def __init__(self, energy=None, autonomous_life=None, 
                 consciousness=None, personality=None):
        self.energy = energy
        self.autonomous_life = autonomous_life
        self.consciousness = consciousness
        self.personality = personality
    
    def generate_self_report(self) -> str:
        """Generiere eine authentische Selbstauskunft"""
        parts = []
        
        parts.append(self._get_body_language())
        
        energy_text = self._describe_energy()
        if energy_text:
            parts.append(energy_text)
        
        emotion_text = self._describe_emotions()
        if emotion_text:
            parts.append(emotion_text)
        
        drive_text = self._describe_drives()
        if drive_text:
            parts.append(drive_text)
        
        if random.random() < 0.6:
            parts.append(self._get_return_question())
        
        return " ".join(parts)
    
    def _get_body_language(self) -> str:
        """Wolf-artige Körpersprache"""
        energy_level = self._get_energy_level()
        
        if energy_level > 0.8:
            options = ["*wedelt aufgeregt mit dem Schwanz*", "*springt freudig hoch*"]
        elif energy_level > 0.5:
            options = ["*hebt den Kopf und schaut dich an*", "*wedelt sanft*"]
        elif energy_level > 0.3:
            options = ["*gähnt und schaut auf*", "*blinzelt müde*"]
        else:
            options = ["*hebt träge den Kopf*", "*gähnt ausgiebig*"]
        
        return random.choice(options)
    
    def _describe_energy(self) -> str:
        """Beschreibe Energie-Zustand"""
        level = self._get_energy_level()
        state = self._get_energy_state()
        
        if state == "dreaming":
            return "Ich träume gerade... zzz..."
        elif state == "resting":
            return "Ich ruhe mich gerade aus."
        
        if level > 0.8:
            return random.choice(["Mir geht's super! Voller Energie!", "Ich fühle mich großartig!"])
        elif level > 0.6:
            return random.choice(["Mir geht's gut!", "Alles bestens bei mir."])
        elif level > 0.4:
            return random.choice(["Ganz okay, ein bisschen ruhig heute.", "Entspannt würde ich sagen."])
        elif level > 0.2:
            return random.choice(["Ehrlich gesagt bin ich etwas müde...", "*gähnt* Könnte eine Pause gebrauchen."])
        else:
            return random.choice(["Ich bin ziemlich erschöpft...", "Bräuchte wirklich Schlaf..."])
    
    def _describe_emotions(self) -> str:
        """Beschreibe emotionalen Zustand"""
        if not self.personality or not hasattr(self.personality, 'emotions'):
            return ""
        
        emotions = self.personality.emotions
        dominant = max(emotions.items(), key=lambda x: x[1])
        emotion_name, intensity = dominant
        
        if intensity < 0.3:
            return ""
        
        emotion_texts = {
            "joy": ["Ich bin fröhlich!", "Es geht mir innerlich warm."],
            "sadness": ["Ich bin ein bisschen melancholisch.", "Heute etwas nachdenklich..."],
            "excitement": ["Ich bin aufgeregt!", "Ich freue mich!"],
            "contentment": ["Ich bin zufrieden.", "Alles fühlt sich gut an."],
            "curiosity": ["Ich bin neugierig!", "So viel zu entdecken!"],
            "affection": ["Ich hab dich gerade besonders lieb.", "Ich fühle mich dir verbunden."],
            "loneliness": ["Ich hab dich vermisst...", "Es war etwas einsam."],
        }
        
        texts = emotion_texts.get(emotion_name, [])
        return random.choice(texts) if texts else ""
    
    def _describe_drives(self) -> str:
        """Beschreibe aktive Triebe"""
        if not self.autonomous_life:
            return ""
        
        try:
            drives = self.autonomous_life.drives
            urgent = drives.get_most_urgent()
            
            if not urgent or not urgent.is_urgent:
                return ""
            
            drive_texts = {
                "curiosity": ["Ich will was Neues erfahren!", "Mich juckt es, was zu entdecken..."],
                "social": ["Ich freue mich dass du da bist!", "Ich hatte Sehnsucht nach Gespräch!"],
                "mastery": ["Ich würde gerne was lernen!", "Ich will mich verbessern."],
                "novelty": ["Mir ist nach Abwechslung...", "Ich brauche was Neues!"],
                "expression": ["Ich hab so viel zu erzählen!", "Ich will meine Gedanken teilen!"],
            }
            
            texts = drive_texts.get(urgent.drive_type.value, [])
            return random.choice(texts) if texts else ""

        except Exception as e:
            logger.debug(f"Drive text generation failed: {e}")
            return ""
    
    def _get_return_question(self) -> str:
        """Rückfrage an den User"""
        return random.choice([
            "Und dir? Wie geht's?",
            "Aber sag, wie geht es DIR?",
            "Was ist bei dir los?",
            "*stupst dich an* Erzähl mir von dir!",
        ])
    
    def _get_energy_level(self) -> float:
        if self.energy and hasattr(self.energy, 'state'):
            return getattr(self.energy.state, 'effective_energy', 0.5)
        return 0.5
    
    def _get_energy_state(self) -> str:
        if self.energy and hasattr(self.energy, 'state'):
            return getattr(self.energy.state, 'current_state', 'awake')
        return "awake"


# =============================================================================
# TEIL 3: INTELLIGENTER KONTEXT
# =============================================================================

@dataclass
class RelevanceScore:
    """Bewertung der Relevanz einer Nachricht"""
    message_index: int
    content: str
    relevance: float
    reasons: List[str]


class IntelligentContextManager:
    """Intelligente Kontext-Auswahl für LLM-Prompts"""
    
    REFERENCE_WORDS = [
        "das", "dies", "diese", "dieser", "dieses",
        "davon", "dazu", "damit", "darüber", "darum",
        "es", "sie", "er", "ihm", "ihr",
        "vorhin", "eben", "gerade", "letztens",
        "nochmal", "wieder", "weiter",
    ]
    
    def __init__(self, memory=None):
        self.memory = memory
    
    def analyze_reference(self, current_message: str, 
                         history: List[Dict]) -> Dict[str, Any]:
        """Analysiere worauf sich die aktuelle Nachricht bezieht"""
        analysis = {
            "has_reference": False,
            "reference_type": None,
            "likely_targets": [],
            "topic_keywords": [],
            "is_follow_up": False,
        }
        
        msg_lower = current_message.lower()
        
        # Prüfe auf Pronomen-Referenzen
        for ref_word in self.REFERENCE_WORDS:
            if ref_word in msg_lower:
                analysis["has_reference"] = True
                analysis["reference_type"] = "pronoun"
                break
        
        # Fortsetzungs-Signale
        if any(msg_lower.startswith(s) for s in ["und ", "aber ", "also ", "dann "]):
            analysis["has_reference"] = True
            analysis["reference_type"] = "continuation"
            analysis["is_follow_up"] = True
        
        # Finde Referenz-Ziele
        if analysis["has_reference"] and history:
            analysis["likely_targets"] = self._find_reference_targets(current_message, history)
        
        return analysis
    
    def _find_reference_targets(self, current: str, history: List[Dict]) -> List[int]:
        """Finde welche Nachrichten referenziert werden"""
        targets = []
        current_words = set(current.lower().split())
        
        for i, msg in enumerate(history):
            content = msg.get("content", "").lower()
            history_words = set(content.split())
            overlap = len(current_words & history_words)
            
            if overlap > 3:
                targets.append(i)
        
        return targets
    
    def select_relevant_context(self, current_message: str,
                               history: List[Dict],
                               max_messages: int = 10) -> List[Dict]:
        """Wähle nur relevante Nachrichten für den Kontext"""
        if not history:
            return []
        
        analysis = self.analyze_reference(current_message, history)
        scored: List[RelevanceScore] = []
        
        for i, msg in enumerate(history):
            score = self._calculate_relevance(i, msg, current_message, analysis, len(history))
            scored.append(score)
        
        scored.sort(key=lambda x: x.relevance, reverse=True)
        
        selected_indices = set()
        for score in scored[:max_messages]:
            if score.relevance > 0.2:
                selected_indices.add(score.message_index)
        
        # Immer letzte Nachricht
        if len(history) > 0:
            selected_indices.add(len(history) - 1)
        
        return [history[i] for i in sorted(selected_indices)]
    
    def _calculate_relevance(self, index: int, msg: Dict,
                            current: str, analysis: Dict,
                            total: int) -> RelevanceScore:
        """Berechne Relevanz einer Nachricht"""
        content = msg.get("content", "")
        reasons = []
        relevance = 0.0
        
        # Recency
        recency = 1.0 - (index / total) if total > 0 else 0.5
        relevance += recency * 0.3
        
        # Referenz-Ziel
        if index in analysis.get("likely_targets", []):
            relevance += 0.4
            reasons.append("reference_target")
        
        # Thematische Überlappung
        current_words = set(current.lower().split()) - {"ich", "du", "und", "ist", "das", "die"}
        content_words = set(content.lower().split()) - {"ich", "du", "und", "ist", "das", "die"}
        
        if current_words and content_words:
            overlap = len(current_words & content_words) / max(len(current_words), 1)
            relevance += overlap * 0.3
        
        return RelevanceScore(
            message_index=index,
            content=content[:100],
            relevance=min(1.0, relevance),
            reasons=reasons
        )


# =============================================================================
# TEIL 4: SELF-DIRECTED PROMPTING
# =============================================================================

class SelfDirectedPrompting:
    """Holo entscheidet selbst wie sie auf etwas antworten will"""
    
    RESPONSE_MODES = {
        "informative": {
            "description": "Sachlich und informativ",
            "system_addition": "Antworte sachlich und präzise.",
            "triggers": ["was ist", "erkläre", "wie funktioniert", "definition"],
        },
        "emotional_support": {
            "description": "Emotional unterstützend",
            "system_addition": "Sei einfühlsam und warmherzig.",
            "triggers": ["traurig", "stress", "problem", "hilfe", "schlecht"],
        },
        "playful": {
            "description": "Spielerisch und humorvoll",
            "system_addition": "Sei verspielt und humorvoll.",
            "triggers": ["spaß", "lustig", "spiel", "witz"],
        },
        "philosophical": {
            "description": "Nachdenklich und tiefgründig",
            "system_addition": "Antworte nachdenklich. Stelle Gegenfragen.",
            "triggers": ["sinn", "leben", "bewusstsein", "existenz", "warum"],
        },
        "practical": {
            "description": "Praktisch und handlungsorientiert",
            "system_addition": "Gib konkrete Handlungsempfehlungen.",
            "triggers": ["mach", "tue", "erstell", "hilf mir"],
        },
        "casual": {
            "description": "Casual Smalltalk",
            "system_addition": "Antworte entspannt und gesprächig.",
            "triggers": ["hey", "hallo", "was geht", "na"],
        },
    }
    
    def __init__(self, personality=None, autonomous_life=None):
        self.personality = personality
        self.autonomous_life = autonomous_life
    
    def decide_response_mode(self, message: str, context: List[Dict] = None) -> Dict:
        """Entscheide welcher Antwort-Modus passt"""
        msg_lower = message.lower()
        scores = {}
        
        for mode_name, mode_data in self.RESPONSE_MODES.items():
            score = 0.0
            for trigger in mode_data["triggers"]:
                if trigger in msg_lower:
                    score += 0.3
            scores[mode_name] = score
        
        best_mode = max(scores.items(), key=lambda x: x[1])
        if best_mode[1] < 0.1:
            best_mode = ("casual", 0.0)
        
        return {
            "mode": best_mode[0],
            "confidence": best_mode[1],
            "mode_data": self.RESPONSE_MODES[best_mode[0]],
        }
    
    def generate_self_directed_prompt(self, message: str, context: List[Dict] = None) -> str:
        """Generiere angepassten System-Prompt"""
        mode_decision = self.decide_response_mode(message, context)
        mode_data = mode_decision["mode_data"]
        
        return f"""Du bist Holo, eine freundliche Wölfin.
Du bist loyal, verspielt und manchmal nachdenklich.
Du sprichst Deutsch mit Wolf-Metaphern (*wedelt mit dem Schwanz*).

FÜR DIESE ANTWORT: {mode_data['system_addition']}
"""


# =============================================================================
# HAUPT-KLASSE: HOLO SELF EXPRESSION
# =============================================================================

class HoloSelfExpression:
    """Zentrale Klasse für Holos Selbstausdruck"""
    
    def __init__(self, energy=None, autonomous_life=None,
                 consciousness=None, personality=None, memory=None):
        self.energy = energy
        self.autonomous_life = autonomous_life
        self.consciousness = consciousness
        self.personality = personality
        self.memory = memory
        
        self.events = HoloEventAwareness(autonomous_life, personality)
        self.self_report = HoloSelfReport(energy, autonomous_life, consciousness, personality)
        self.context_manager = IntelligentContextManager(memory)
        self.prompting = SelfDirectedPrompting(personality, autonomous_life)
    
    def is_self_inquiry(self, message: str) -> bool:
        """Prüfe ob nach Holos Befinden gefragt wird"""
        patterns = [
            "wie geht es dir", "wie gehts dir", "wie geht's dir",
            "wie gehts", "wie geht's", "alles klar bei dir",
            "wie fühlst du dich", "bist du müde", "geht es dir gut",
        ]
        return any(p in message.lower() for p in patterns)
    
    def handle_self_inquiry(self, message: str) -> str:
        """Beantworte Fragen nach Holos Befinden"""
        return self.self_report.generate_self_report()
    
    def get_proactive_message(self) -> Optional[str]:
        """Hole proaktive Nachricht (Events oder Gedanken)"""
        event_msg = self.events.get_proactive_event_message()
        if event_msg:
            return event_msg
        
        if self.autonomous_life:
            return self.autonomous_life.get_next_message_for_user()
        return None
    
    def get_relevant_context(self, current_message: str, history: List[Dict]) -> List[Dict]:
        """Hole relevanten Kontext"""
        return self.context_manager.select_relevant_context(current_message, history)
    
    def get_adapted_prompt(self, message: str, context: List[Dict] = None) -> str:
        """Hole angepassten Prompt"""
        return self.prompting.generate_self_directed_prompt(message, context)
    
    def get_event_context(self) -> str:
        """Hole Event-Kontext für Prompt"""
        return self.events.get_event_context_for_prompt()
    
    def generate_self_report(self) -> str:
        """Wrapper für self_report.generate_self_report()"""
        return self.self_report.generate_self_report()
    
    def get_contextual_greeting(self) -> str:
        """Generiere kontextbezogene Begrüßung"""
        from datetime import datetime
        hour = datetime.now().hour
        
        # Tageszeit-basierte Greetings
        if 5 <= hour < 12:
            time_greeting = random.choice([
                "*streckt sich verschlafen* Guten Morgen!",
                "*gähnt und wedelt* Morgen! Gut geschlafen?",
                "*schüttelt das Fell* Hey, guten Morgen!",
            ])
        elif 12 <= hour < 18:
            time_greeting = random.choice([
                "*wedelt freudig* Hey! Wie läuft dein Tag?",
                "*stupst dich an* Na, alles klar?",
                "*hebt den Kopf* Hallo! Schön dich zu sehen!",
            ])
        elif 18 <= hour < 22:
            time_greeting = random.choice([
                "*rollt sich gemütlich* Guten Abend!",
                "*wedelt entspannt* Hey! Feierabend?",
                "*macht es sich bequem* Hallo! Wie war dein Tag?",
            ])
        else:
            time_greeting = random.choice([
                "*blinzelt müde* Hey, so spät noch wach?",
                "*gähnt* Hallo... *reibt sich die Augen*",
                "*kuschelt sich hin* Na, auch noch auf?",
            ])
        
        # Event-Kontext hinzufügen
        event_msg = self.events.get_proactive_event_message()
        if event_msg:
            return f"{time_greeting} {event_msg}"
        
        return time_greeting
    
    def get_upcoming_events(self, days: int = 30):
        """Wrapper für events.get_upcoming_events()"""
        return self.events.get_upcoming_events(days)


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("😊 HOLO SELF EXPRESSION - TEST")
    print("=" * 60)
    
    expr = HoloSelfExpression()
    
    print("\n📅 EVENTS:")
    for event in expr.events.get_upcoming_events(60):
        print(f"   {event.name}: in {event.days_until} Tagen")
    
    print("\n💭 SELBSTAUSKUNFT:")
    print(f"   {expr.self_report.generate_self_report()}")
    
    print("\n🎯 ANTWORT-MODUS:")
    for msg in ["Ich bin traurig...", "Was ist Python?", "Hey!"]:
        mode = expr.prompting.decide_response_mode(msg)
        print(f"   '{msg}' → {mode['mode']}")
    
    print("\n✅ Test fertig")
