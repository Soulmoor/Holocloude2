#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO MESSAGE ANALYZER v4.0 - Response Orchestrator                          ║
║                                                                              ║
║  SPEZIALISIERUNG: Multi-Response Orchestrierung & Wolf-Persönlichkeit        ║
║                                                                              ║
║  KERNFUNKTIONEN:                                                             ║
║  • Response Orchestration - Mehrere Antwort-Teile kombinieren                ║
║  • Priority Routing - Antworten nach Wichtigkeit ordnen                      ║
║  • Wolf News Formatter - News mit Persönlichkeit präsentieren                ║
║  • Template System - Wolf-styled Response Templates                          ║
║  • Multi-Response Combiner - Mehrere Intents elegant beantworten             ║
║  • Context-Aware Formatting - Format an Kontext anpassen                     ║
║  • Response Quality - Antwort-Qualität sicherstellen                         ║
║                                                                              ║
║  IMPORT FÜR INTENT DETECTION:                                                ║
║  → from holo_smart_understanding import SmartUnderstanding                   ║
║                                                                              ║
║  Version: 4.0 (Refactored - Single Responsibility)                           ║
║  Author: Kira & Claude                                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import re
import random
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import defaultdict

logger = logging.getLogger("HoloMessageAnalyzer")


# =============================================================================
# PUBLIC API - Explizite Exports
# =============================================================================

__all__ = [
    # Enums & Data Classes
    'ResponsePriority',
    'ResponsePart',

    # Core Classes
    'WolfNewsFormatter',
    'ResponseTemplates',
    'ResponseOrchestrator',
    'MultiResponseCombiner',
    'ContextAwareFormatter',
    'ResponseQualityChecker',
    'HoloMessageAnalyzer',
    'MultiIntentDetector',

    # Factory Functions
    'create_message_analyzer',
    'create_news_formatter',
    'create_orchestrator',

    # Helper Functions
    'get_smart_understanding',
]


# =============================================================================
# OPTIONAL: IMPORT SMART UNDERSTANDING
# =============================================================================

_HAS_SMART_UNDERSTANDING = False
_smart_understanding = None

def get_smart_understanding():
    """Lazy-load SmartUnderstanding für Intent Detection"""
    global _HAS_SMART_UNDERSTANDING, _smart_understanding
    
    if _smart_understanding is not None:
        return _smart_understanding
    
    try:
        from holo_smart_understanding import SmartUnderstanding
        _smart_understanding = SmartUnderstanding()
        _HAS_SMART_UNDERSTANDING = True
        logger.info("✅ SmartUnderstanding für Intent Detection geladen")
        return _smart_understanding
    except ImportError:
        logger.debug("⚠️ SmartUnderstanding nicht verfügbar")
        _HAS_SMART_UNDERSTANDING = False
        return None


# =============================================================================
# PRIORITY SYSTEM
# =============================================================================

class ResponsePriority(Enum):
    """Priorität für Response-Reihenfolge"""
    CRITICAL = 1      # Sofort (Befehle, Sicherheit, Emotionale Unterstützung)
    HIGH = 2          # Wichtig (Activity, Wellbeing, direkte Fragen)
    MEDIUM = 3        # Normal (News, Themen, Informationen)
    LOW = 4           # Niedrig (Smalltalk, Zusätze)
    BACKGROUND = 5    # Hintergrund (Quirks, Callbacks)


@dataclass
class ResponsePart:
    """Ein Teil einer Antwort"""
    content: str
    priority: ResponsePriority
    intent: str
    is_primary: bool = False
    requires_newline: bool = True
    metadata: Dict = field(default_factory=dict)


# =============================================================================
# WOLF NEWS FORMATTER - News mit Persönlichkeit
# =============================================================================

class WolfNewsFormatter:
    """
    Formatiert News mit Wolf-Persönlichkeit statt rohem Dump.
    
    Features:
    - Energie-basierte Ausführlichkeit
    - Stimmungs-basierte Kommentare
    - Kategorien-spezifische Reaktionen
    - Natürliche Präsentation
    """
    
    # Wolf-Aktionen für News
    NEWS_INTRO_ACTIONS = [
        "*hebt neugierig den Kopf*",
        "*schaut interessiert*",
        "*schaut interessiert auf*",
        "*legt Kopf schief*",
        "*freut sich leicht mit dem Hände*",
        "*schaut aufmerksam*",
    ]
    
    # Kommentare nach Kategorie
    NEWS_COMMENTARY = {
        "Technik": [
            "Technisch ziemlich spannend!",
            "Das könnte interessant werden...",
            "*schaut überrascht* Tech-News!",
            "Spannende Entwicklung!",
        ],
        "Welt": [
            "Das sollte man im Auge behalten.",
            "Hmm, komplizierte Zeiten...",
            "Interessante Entwicklung.",
            "*schaut nachdenklich*",
        ],
        "Science": [
            "Wissenschaft ist faszinierend!",
            "*schaut interessiert neugierig* Spannende Forschung!",
            "Da lerne sogar ich was Neues!",
        ],
        "Sport": [
            "*freut sich* Sportliche Grüße!",
            "Action!",
        ],
        "Entertainment": [
            "*schaut aufmerksam*",
            "Unterhaltung!",
        ],
        "default": [
            "Hab ich gerade gelesen.",
            "Ist mir aufgefallen.",
            "Fand ich interessant.",
        ]
    }
    
    # Abschluss-Aktionen
    CLOSING_ACTIONS = [
        "*legt sich gemütlich hin*",
        "*gähnt leicht*",
        "*schaut dich fragend an*",
        "*freut sich*",
        "*streckt sich*",
    ]
    
    # Keine-News Antworten
    NO_NEWS_RESPONSES = [
        "*schaut sich um* Hmm, hab gerade keine neuen Nachrichten gesehen...",
        "*kratzt sich am Ohr* Die News-Feeds scheinen leer zu sein.",
        "*gähnt* Keine News im Moment. Vielleicht später?",
        "*schaut sich um* Nix Neues gefunden...",
    ]
    
    def __init__(self, energy_level: float = 0.7, mood: str = "neutral"):
        self.energy = energy_level
        self.mood = mood
    
    def set_state(self, energy: float = None, mood: str = None):
        """Setze Energie/Stimmung"""
        if energy is not None:
            self.energy = energy
        if mood is not None:
            self.mood = mood
    
    def format_news(self, news_list: List[Dict], max_items: int = 5,
                    style: str = "conversational") -> str:
        """
        Formatiere News mit Wolf-Persönlichkeit.
        
        Args:
            news_list: Liste von News-Dicts
            max_items: Max Anzahl zu zeigender News
            style: "conversational" (gesprächig) oder "brief" (kurz)
            
        Returns:
            Wolf-styled News-Response
        """
        if not news_list:
            return random.choice(self.NO_NEWS_RESPONSES)
        
        # Energie-basierte Anpassung
        if self.energy < 0.3:
            max_items = min(max_items, 2)
            style = "brief"
        elif self.energy < 0.5:
            max_items = min(max_items, 3)
        
        response_parts = []
        
        # Intro
        intro = random.choice(self.NEWS_INTRO_ACTIONS)
        if style == "conversational":
            intro += " " + self._get_intro_text()
        response_parts.append(intro)
        
        # News Items
        for i, news in enumerate(news_list[:max_items]):
            item_text = self._format_single_news(news, i, style)
            response_parts.append(item_text)
        
        # Outro
        remaining = len(news_list) - max_items
        if style == "conversational" and remaining > 0:
            response_parts.append(f"\n*schaut überrascht* Gibt noch {remaining} weitere...")
        
        # Closing Action (manchmal)
        if self.energy > 0.5 and random.random() > 0.6:
            response_parts.append("\n" + random.choice(self.CLOSING_ACTIONS))
        
        return "\n".join(response_parts)
    
    def _get_intro_text(self) -> str:
        """Generiere Intro-Text basierend auf Stimmung"""
        intros = {
            "happy": "Hab heute ein paar interessante Sachen gelesen!",
            "curious": "Oh, da gibt es einiges Spannendes!",
            "tired": "Hier mal die wichtigsten News...",
            "excited": "Wow, da ist einiges los!",
            "neutral": "Lass mich dir zeigen was ich gefunden hab:",
        }
        return intros.get(self.mood, intros["neutral"])
    
    def _format_single_news(self, news: Dict, index: int, style: str) -> str:
        """Formatiere einen einzelnen News-Artikel"""
        title = news.get('title', 'Kein Titel')
        source = news.get('source', '?')
        summary = news.get('summary', '')[:100] if news.get('summary') else ''
        
        if style == "brief":
            return f"\n• **{source}:** {title}"
        
        # Conversational Style
        if index == 0:
            # Erster Artikel ausführlicher
            commentary = self._get_commentary(source)
            result = f"\n**{source}:** {title}"
            if summary:
                result += f"\n_{summary}..._"
            result += f"\n{commentary}"
            return result
        else:
            # Weitere kürzer
            return f"\n• **{source}:** {title}"
    
    def _get_commentary(self, source: str) -> str:
        """Hole passenden Kommentar für Quelle"""
        comments = self.NEWS_COMMENTARY.get(source, self.NEWS_COMMENTARY["default"])
        return random.choice(comments)
    
    def format_news_detail(self, news: Dict) -> str:
        """Formatiere Details zu einem spezifischen Artikel"""
        title = news.get('title', 'Kein Titel')
        summary = news.get('summary', 'Keine Zusammenfassung verfügbar.')
        source = news.get('source', '?')
        link = news.get('link', '')
        
        response = f"*schaut interessiert*\n\n"
        response += f"**{title}**\n"
        response += f"_Quelle: {source}_\n\n"
        response += f"{summary}\n\n"
        
        if link:
            response += f"*zeigt darauf* Hier ist der Link: {link}"
        
        return response
    
    def format_news_summary(self, news_list: List[Dict]) -> str:
        """Kurze Zusammenfassung der News"""
        if not news_list:
            return "*schüttelt Kopf* Keine News da."
        
        count = len(news_list)
        sources = set(n.get('source', '?') for n in news_list)
        
        return f"*nickt* {count} News aus {len(sources)} Quellen: {', '.join(sources)}"


# =============================================================================
# RESPONSE TEMPLATES - Wolf-styled Antwort-Vorlagen
# =============================================================================

class ResponseTemplates:
    """
    Wolf-Persönlichkeit Response Templates.
    
    Kategorisiert nach Intent-Typ und Stimmung.
    """
    
    TEMPLATES = {
        # Greetings
        "greeting": {
            "morning": [
                "*gähnt und streckt sich* Guten Morgen! ☀️",
                "*hebt verschlafen den Kopf* Moin! Auch schon wach?",
                "*freut sich müde* Morgen! Gut geschlafen?",
            ],
            "day": [
                "*freut sich* Hey! 😊",
                "*schaut interessiert* Hallo! Schön dich zu sehen!",
                "*springt auf* Hi! Was gibt's?",
            ],
            "evening": [
                "*blinzelt gemütlich* Guten Abend!",
                "*hebt den Kopf* Hey! Wie war dein Tag?",
                "*freut sich entspannt* Nabend!",
            ],
            "night": [
                "*gähnt* Hey, so spät noch wach?",
                "*blinzelt müde* Hallo... *gähn*",
                "*hebt verschlafen den Kopf* Oh, hi!",
            ],
        },
        
        # Farewells
        "farewell": {
            "default": [
                "*freut sich zum Abschied* Bis bald! 😊",
                "*winkt mit dem Hände* Mach's gut!",
                "*stupst dich sanft an* Pass auf dich auf!",
            ],
            "night": [
                "*gähnt* Schlaf gut... *rollt sich ein*",
                "*kuschelt sich zusammen* Gute Nacht! Träum was Schönes!",
                "*freut sich müde* Schlaf schön! Bis morgen!",
            ],
        },
        
        # Gratitude
        "gratitude": {
            "default": [
                "*freut sich stolz* Gerne! 😊",
                "*freut sich* Immer gern!",
                "*strahlt* Kein Problem!",
            ],
            "touched": [
                "*freut sich verlegen* Aw, das ist lieb!",
                "*Augen werden warm* Danke dir!",
                "*freut sich sichtlich* Das bedeutet mir viel!",
            ],
        },
        
        # Activity/Status
        "activity": {
            "high_energy": [
                "*springt auf* Ich hab gerade {activity}!",
                "*freut sich begeistert* Oh, ich war beschäftigt mit {activity}!",
            ],
            "medium_energy": [
                "*schaut hoch* Hab gerade {activity}.",
                "*lächelt* Ich war mit {activity} beschäftigt.",
            ],
            "low_energy": [
                "*gähnt* Nicht viel... hab ein bisschen {activity}.",
                "*streckt sich müde* Hab etwas {activity}...",
            ],
        },
        
        # Wellbeing
        "wellbeing": {
            "positive": [
                "*freut sich* Mir geht's gut! Danke der Nachfrage!",
                "*strahlt* Super! Und dir?",
                "*hechelt glücklich* Bestens! 😊",
            ],
            "neutral": [
                "*hebt den Kopf* Ganz okay! Und selbst?",
                "*nickt* Läuft soweit! Bei dir?",
            ],
            "tired": [
                "*gähnt* Etwas müde... aber sonst okay!",
                "*streckt sich* Bisschen erschöpft...",
            ],
        },
        
        # Support
        "support": {
            "empathy": [
                "*stupst dich sanft an* Das klingt nicht einfach...",
                "*legt sich neben dich* Ich bin hier für dich.",
                "*schaut besorgt* Magst du erzählen was los ist?",
            ],
            "encouragement": [
                "*freut sich aufmunternd* Hey, das schaffst du!",
                "*stupst dich an* Kopf hoch!",
                "*nickt bestärkend* Du packst das!",
            ],
        },
        
        # Clarification
        "clarification": {
            "default": [
                "*legt Kopf schief* Hmm, ich bin mir nicht sicher ob ich das richtig verstehe...",
                "*schaut interessiert* Warte mal... wie meinst du das?",
                "*kratzt sich am Ohr* Kannst du mir das genauer erklären?",
            ],
        },
        
        # Acknowledgment
        "acknowledgment": {
            "default": [
                "*nickt* Verstehe!",
                "*freut sich* Alles klar!",
                "Okay, hab ich! 👍",
            ],
        },
        
        # Thinking
        "thinking": {
            "default": [
                "*überlegt* Hmm, lass mich nachdenken...",
                "*kratzt sich am Ohr* Also...",
                "*schaut nachdenklich* Gute Frage...",
            ],
        },
        
        # Unknown/Fallback
        "unknown": {
            "default": [
                "*legt Kopf schief* Hmm?",
                "*schaut interessiert* Wie meinst du das?",
                "*schaut fragend*",
            ],
        },
    }
    
    # Aktivitäten für {activity} Platzhalter
    ACTIVITIES = [
        "News gelesen",
        "nachgedacht",
        "gelernt",
        "die Welt beobachtet",
        "mich ausgeruht",
        "geträumt",
    ]
    
    @classmethod
    def get_template(cls, category: str, subcategory: str = "default",
                    context: Dict = None) -> str:
        """Hole passendes Template"""
        templates = cls.TEMPLATES.get(category, cls.TEMPLATES["unknown"])
        
        if subcategory in templates:
            pool = templates[subcategory]
        elif "default" in templates:
            pool = templates["default"]
        else:
            pool = list(templates.values())[0]
        
        template = random.choice(pool)
        
        # Platzhalter ersetzen
        if "{activity}" in template:
            activity = random.choice(cls.ACTIVITIES)
            template = template.replace("{activity}", activity)
        
        return template
    
    @classmethod
    def get_time_based_greeting(cls) -> str:
        """Hole zeitbasierte Begrüßung"""
        hour = datetime.now().hour
        
        if 5 <= hour < 11:
            return cls.get_template("greeting", "morning")
        elif 11 <= hour < 18:
            return cls.get_template("greeting", "day")
        elif 18 <= hour < 22:
            return cls.get_template("greeting", "evening")
        else:
            return cls.get_template("greeting", "night")
    
    @classmethod
    def get_energy_based_activity(cls, energy: float) -> str:
        """Hole energie-basierte Aktivitäts-Antwort"""
        if energy > 0.7:
            return cls.get_template("activity", "high_energy")
        elif energy > 0.4:
            return cls.get_template("activity", "medium_energy")
        else:
            return cls.get_template("activity", "low_energy")


# =============================================================================
# RESPONSE ORCHESTRATOR - Hauptklasse
# =============================================================================

class ResponseOrchestrator:
    """
    Orchestriert Antworten für mehrere Intents.
    
    Kombiniert Antworten in sinnvoller Reihenfolge:
    1. Critical (Emotionale Unterstützung, Befehle)
    2. High (Activity, Wellbeing)
    3. Medium (News, Themen)
    4. Low (Smalltalk)
    5. Background (Quirks, Callbacks)
    """
    
    # Intent → Handler Mapping
    INTENT_HANDLERS = {
        "greeting": "_handle_greeting",
        "farewell": "_handle_farewell",
        "gratitude": "_handle_gratitude",
        "activity": "_handle_activity",
        "activity_inquiry": "_handle_activity",
        "wellbeing": "_handle_wellbeing",
        "wellbeing_inquiry": "_handle_wellbeing",
        "news": "_handle_news",
        "news_request": "_handle_news",
        "emotion": "_handle_emotion",
        "support": "_handle_support",
    }
    
    # Intent → Priority Mapping
    INTENT_PRIORITIES = {
        "support": ResponsePriority.CRITICAL,
        "emotion": ResponsePriority.CRITICAL,
        "command": ResponsePriority.CRITICAL,
        
        "activity": ResponsePriority.HIGH,
        "activity_inquiry": ResponsePriority.HIGH,
        "wellbeing": ResponsePriority.HIGH,
        "wellbeing_inquiry": ResponsePriority.HIGH,
        "question": ResponsePriority.HIGH,
        
        "news": ResponsePriority.MEDIUM,
        "news_request": ResponsePriority.MEDIUM,
        "topic_explain": ResponsePriority.MEDIUM,
        
        "greeting": ResponsePriority.LOW,
        "farewell": ResponsePriority.LOW,
        "gratitude": ResponsePriority.LOW,
        "smalltalk": ResponsePriority.LOW,
    }
    
    def __init__(self, brain=None):
        self.brain = brain
        self.news_formatter = WolfNewsFormatter()
        self.templates = ResponseTemplates
        self._understanding = None
    
    def _get_understanding(self):
        """Hole SmartUnderstanding (lazy)"""
        if self._understanding is None:
            self._understanding = get_smart_understanding()
        return self._understanding
    
    def orchestrate(self, intents: List[Dict], context: Dict = None) -> str:
        """
        Orchestriere Antworten für alle erkannten Intents.
        
        Args:
            intents: Liste von Intent-Dicts mit 'intent' und optional 'confidence'
            context: Zusätzlicher Kontext
            
        Returns:
            Kombinierte Wolf-styled Antwort
        """
        if not intents:
            return self.templates.get_template("unknown")
        
        # Normalisiere Intents
        normalized = self._normalize_intents(intents)
        
        # Sammle Response-Teile
        response_parts: List[ResponsePart] = []
        
        for intent_info in normalized:
            intent = intent_info.get("intent", "unknown")
            priority = self.INTENT_PRIORITIES.get(intent, ResponsePriority.MEDIUM)
            
            # Handler aufrufen
            handler_name = self.INTENT_HANDLERS.get(intent)
            if handler_name and hasattr(self, handler_name):
                handler = getattr(self, handler_name)
                content = handler(intent_info, context)
                
                if content:
                    response_parts.append(ResponsePart(
                        content=content,
                        priority=priority,
                        intent=intent,
                        is_primary=(len(response_parts) == 0),
                    ))
        
        # Sortiere nach Priorität
        response_parts.sort(key=lambda p: p.priority.value)
        
        # Kombiniere
        return self._combine_parts(response_parts)
    
    def orchestrate_single(self, intent: str, context: Dict = None,
                          energy: float = 0.5, mood: str = "neutral") -> str:
        """
        Orchestriere Antwort für einzelnen Intent.
        """
        self.news_formatter.set_state(energy, mood)
        
        intent_info = {"intent": intent, "energy": energy, "mood": mood}
        
        handler_name = self.INTENT_HANDLERS.get(intent)
        if handler_name and hasattr(self, handler_name):
            handler = getattr(self, handler_name)
            return handler(intent_info, context) or self.templates.get_template("unknown")
        
        return self.templates.get_template("unknown")
    
    def _normalize_intents(self, intents: List) -> List[Dict]:
        """Normalisiere verschiedene Intent-Formate"""
        normalized = []
        
        for item in intents:
            if isinstance(item, str):
                normalized.append({"intent": item})
            elif isinstance(item, dict):
                normalized.append(item)
            else:
                # Annahme: Objekt mit .intent Attribut
                if hasattr(item, "intent"):
                    normalized.append({
                        "intent": getattr(item, "intent", "unknown"),
                        "confidence": getattr(item, "confidence", 0.5),
                    })
        
        return normalized
    
    def _combine_parts(self, parts: List[ResponsePart]) -> str:
        """Kombiniere Response-Teile intelligent"""
        if not parts:
            return self.templates.get_template("unknown")
        
        result = []
        
        for i, part in enumerate(parts):
            if i == 0:
                result.append(part.content)
            else:
                # Verbindung
                if part.requires_newline:
                    result.append("\n\n" + part.content)
                else:
                    result.append(" " + part.content)
        
        return "".join(result).strip()
    
    # =========================================================================
    # INTENT HANDLERS
    # =========================================================================
    
    def _handle_greeting(self, intent_info: Dict, context: Dict) -> str:
        """Handle Greeting"""
        return self.templates.get_time_based_greeting()
    
    def _handle_farewell(self, intent_info: Dict, context: Dict) -> str:
        """Handle Farewell"""
        hour = datetime.now().hour
        if 22 <= hour or hour < 6:
            return self.templates.get_template("farewell", "night")
        return self.templates.get_template("farewell")
    
    def _handle_gratitude(self, intent_info: Dict, context: Dict) -> str:
        """Handle Gratitude"""
        # Prüfe ob besonders gerührt
        if context and context.get("emotional"):
            return self.templates.get_template("gratitude", "touched")
        return self.templates.get_template("gratitude")
    
    def _handle_activity(self, intent_info: Dict, context: Dict) -> str:
        """Handle Activity Inquiry"""
        energy = intent_info.get("energy", 0.5)
        return self.templates.get_energy_based_activity(energy)
    
    def _handle_wellbeing(self, intent_info: Dict, context: Dict) -> str:
        """Handle Wellbeing Inquiry"""
        energy = intent_info.get("energy", 0.5)
        mood = intent_info.get("mood", "neutral")
        
        if energy < 0.3:
            return self.templates.get_template("wellbeing", "tired")
        elif mood in ["happy", "excited"]:
            return self.templates.get_template("wellbeing", "positive")
        return self.templates.get_template("wellbeing", "neutral")
    
    def _handle_news(self, intent_info: Dict, context: Dict) -> str:
        """Handle News Request"""
        news_list = []
        
        # News aus Context
        if context and "news_data" in context:
            news_list = context["news_data"]
        
        # News aus Brain
        elif self.brain:
            try:
                ps = self.brain.comm.get_pi_status()
                news_list = ps.get("state", {}).get("news_data", [])
            except Exception as e:
                logger.warning(f"[MessageAnalyzer] News fetch failed: {type(e).__name__}: {e}")
        
        return self.news_formatter.format_news(news_list)
    
    def _handle_emotion(self, intent_info: Dict, context: Dict) -> str:
        """Handle Emotion Expression"""
        # Prüfe ob Support nötig
        if context and context.get("needs_support"):
            return self.templates.get_template("support", "empathy")
        return self.templates.get_template("acknowledgment")
    
    def _handle_support(self, intent_info: Dict, context: Dict) -> str:
        """Handle Support Request"""
        return self.templates.get_template("support", "empathy")


# =============================================================================
# MULTI-RESPONSE COMBINER - Mehrere Antworten elegant kombinieren
# =============================================================================

class MultiResponseCombiner:
    """
    Kombiniert mehrere Antwort-Teile zu einer natürlichen Antwort.
    
    Features:
    - Übergangsphrasen
    - Prioritäts-basierte Reihenfolge
    - Duplikat-Vermeidung
    - Längen-Kontrolle
    """
    
    # Übergangsphrasen
    TRANSITIONS = {
        "addition": [
            "Außerdem...",
            "Ach ja, und...",
            "Übrigens...",
        ],
        "contrast": [
            "Aber...",
            "Allerdings...",
        ],
        "topic_change": [
            "Was anderes...",
            "Apropos...",
        ],
    }
    
    def __init__(self, max_length: int = 500):
        self.max_length = max_length
    
    def combine(self, parts: List[str], priorities: List[int] = None) -> str:
        """
        Kombiniere Antwort-Teile.
        
        Args:
            parts: Liste von Antwort-Texten
            priorities: Optionale Prioritäten (niedriger = wichtiger)
        """
        if not parts:
            return ""
        
        if len(parts) == 1:
            return parts[0]
        
        # Sortiere nach Priorität wenn gegeben
        if priorities:
            sorted_parts = sorted(zip(priorities, parts))
            parts = [p for _, p in sorted_parts]
        
        # Kombiniere
        result = [parts[0]]
        current_length = len(parts[0])
        
        for part in parts[1:]:
            # Längen-Check
            if current_length + len(part) > self.max_length:
                break
            
            # Übergang
            if random.random() < 0.3:
                transition = random.choice(self.TRANSITIONS["addition"])
                result.append(f"\n\n{transition} {part}")
            else:
                result.append(f"\n\n{part}")
            
            current_length += len(part)
        
        return "".join(result)
    
    def deduplicate(self, parts: List[str]) -> List[str]:
        """Entferne ähnliche/doppelte Teile"""
        unique = []
        seen_patterns = set()
        
        for part in parts:
            # Einfacher Pattern-Check
            pattern = " ".join(part.lower().split()[:5])
            
            if pattern not in seen_patterns:
                unique.append(part)
                seen_patterns.add(pattern)
        
        return unique


# =============================================================================
# CONTEXT-AWARE FORMATTER - Format an Kontext anpassen
# =============================================================================

class ContextAwareFormatter:
    """
    Passt Antwort-Format an Kontext an.
    
    Berücksichtigt:
    - Nachrichtenhistorie
    - User-Präferenzen
    - Aktuelle Stimmung
    - Geräte-Kontext
    """
    
    def __init__(self):
        self.history_length = 0
        self.user_prefers_brief = False
    
    def format(self, response: str, context: Dict = None) -> str:
        """Formatiere Antwort kontextbezogen"""
        if not context:
            return response
        
        # Kürze wenn User kurze Nachrichten bevorzugt
        if context.get("prefer_brief") or self.user_prefers_brief:
            response = self._shorten(response)
        
        # Erweitere wenn tiefes Gespräch
        if context.get("discourse_depth", 0) > 3:
            response = self._add_engagement(response)
        
        # Support-Modus
        if context.get("needs_support"):
            response = self._soften(response)
        
        return response
    
    def _shorten(self, response: str) -> str:
        """Kürze Antwort"""
        # Entferne zusätzliche Absätze
        parts = response.split("\n\n")
        if len(parts) > 2:
            return "\n\n".join(parts[:2])
        return response
    
    def _add_engagement(self, response: str) -> str:
        """Füge Engagement hinzu"""
        if not response.endswith("?"):
            engagements = [
                " Was denkst du?",
                " Oder?",
                " Kennst du das?",
            ]
            if random.random() < 0.3:
                response += random.choice(engagements)
        return response
    
    def _soften(self, response: str) -> str:
        """Mache Antwort sanfter"""
        # Entferne zu enthusiastische Marker
        response = response.replace("!", ".")
        response = response.replace("🎉", "")
        return response


# =============================================================================
# RESPONSE QUALITY CHECKER
# =============================================================================

class ResponseQualityChecker:
    """
    Prüft Qualität von generierten Antworten.
    
    Checks:
    - Länge
    - Persönlichkeit
    - Relevanz
    - Wiederholungen
    """
    
    def __init__(self):
        self.recent_responses: List[str] = []
    
    def check(self, response: str, context: Dict = None) -> Dict:
        """
        Prüfe Antwort-Qualität.
        
        Returns:
            {
                "score": float (0-1),
                "issues": List[str],
                "suggestions": List[str],
            }
        """
        issues = []
        suggestions = []
        score = 1.0
        
        # Längen-Check
        words = response.split()
        if len(words) < 2:
            issues.append("too_short")
            score -= 0.3
            suggestions.append("Mehr Inhalt hinzufügen")
        elif len(words) > 100:
            issues.append("too_long")
            score -= 0.1
            suggestions.append("Kürzen")
        
        # Persönlichkeits-Check
        if "*" not in response and "😊" not in response:
            issues.append("no_personality")
            score -= 0.15
            suggestions.append("Wolf-Aktion hinzufügen")
        
        # Wiederholungs-Check
        if response in self.recent_responses:
            issues.append("repetition")
            score -= 0.3
            suggestions.append("Variation nutzen")
        
        # Tracking
        self.recent_responses.append(response)
        if len(self.recent_responses) > 10:
            self.recent_responses.pop(0)
        
        return {
            "score": max(0.0, score),
            "issues": issues,
            "suggestions": suggestions,
        }
    
    def improve(self, response: str, issues: List[str]) -> str:
        """Verbessere Antwort basierend auf Issues"""
        if "too_short" in issues:
            response += " Was denkst du?"
        
        if "no_personality" in issues and "*" not in response:
            actions = ["*freut sich*", "*nickt*", "*schaut dich an*"]
            response = random.choice(actions) + " " + response
        
        return response


# =============================================================================
# MAIN ANALYZER CLASS
# =============================================================================

class HoloMessageAnalyzer:
    """
    Hauptklasse für intelligente Nachrichtenanalyse und Response-Orchestrierung.
    
    WICHTIG: Nutzt SmartUnderstanding für Intent Detection!
    Diese Klasse fokussiert auf Response-Generierung.
    
    Features:
    - Multi-Intent Orchestrierung
    - Wolf-Personality Responses
    - Quality Assurance
    - Context-Aware Formatting
    
    Usage:
        analyzer = HoloMessageAnalyzer()
        result = analyzer.analyze("hast du news? und was machst du so?")
    """
    
    def __init__(self, brain=None):
        self.brain = brain
        self.orchestrator = ResponseOrchestrator(brain)
        self.combiner = MultiResponseCombiner()
        self.formatter = ContextAwareFormatter()
        self.quality = ResponseQualityChecker()
        self.news_formatter = WolfNewsFormatter()
        
        # Smart Understanding
        self._understanding = None
        
        logger.info("[MessageAnalyzer] Initialisiert mit Response Orchestration")
    
    def _get_understanding(self):
        """Hole SmartUnderstanding (lazy)"""
        if self._understanding is None:
            self._understanding = get_smart_understanding()
        return self._understanding
    
    def analyze(self, message: str, context: Dict = None,
               energy: float = 0.5, mood: str = "neutral") -> Dict:
        """
        Analysiere eine Nachricht und generiere Response.
        
        Args:
            message: Die User-Nachricht
            context: Optionaler zusätzlicher Kontext
            energy: Holo's Energie-Level
            mood: Holo's Stimmung
            
        Returns:
            {
                "original": str,
                "intents": List[Dict],
                "primary_intent": str,
                "response": str,
                "needs_llm": bool,
                "llm_context": Optional[Dict],
                "quality": Dict,
            }
        """
        if not message or not message.strip():
            return {
                "original": message,
                "intents": [],
                "primary_intent": "unknown",
                "response": "*schaut dich fragend an*",
                "needs_llm": False,
                "llm_context": None,
                "quality": {"score": 1.0, "issues": []},
            }
        
        # 1. Intent Detection via SmartUnderstanding
        understanding = self._get_understanding()
        
        if understanding:
            analysis = understanding.understand(message)
            intents = analysis.get("intents", [{"intent": analysis.get("intent", "general")}])
            primary_intent = analysis.get("intent", "general")
            needs_llm = analysis.get("requires_llm", True)
            is_multi = analysis.get("is_multi_intent", False)
        else:
            # Fallback
            intents = [{"intent": "general"}]
            primary_intent = "general"
            needs_llm = True
            is_multi = False
        
        # 2. Context erweitern
        full_context = self._gather_context(context, energy, mood)
        
        # 3. Response orchestrieren
        if is_multi and len(intents) > 1:
            # Multi-Intent
            for intent in intents:
                if isinstance(intent, dict):
                    intent["energy"] = energy
                    intent["mood"] = mood
            response = self.orchestrator.orchestrate(intents, full_context)
        else:
            # Single Intent
            response = self.orchestrator.orchestrate_single(
                primary_intent, full_context, energy, mood
            )
        
        # 4. Format anpassen
        response = self.formatter.format(response, full_context)
        
        # 5. Quality Check
        quality = self.quality.check(response, full_context)
        if quality["score"] < 0.6:
            response = self.quality.improve(response, quality["issues"])
        
        # 6. LLM Context
        llm_context = None
        if needs_llm:
            llm_context = self._build_llm_context(
                message, primary_intent, full_context, analysis if understanding else {}
            )
        
        return {
            "original": message,
            "intents": intents,
            "primary_intent": primary_intent,
            "response": response,
            "needs_llm": needs_llm,
            "llm_context": llm_context,
            "quality": quality,
        }
    
    def _gather_context(self, extra_context: Dict, energy: float, mood: str) -> Dict:
        """Sammle Kontext aus allen Quellen"""
        context = extra_context or {}
        context["energy"] = energy
        context["mood"] = mood
        
        # News holen wenn nicht vorhanden
        if "news_data" not in context and self.brain:
            try:
                ps = self.brain.comm.get_pi_status()
                context["news_data"] = ps.get("state", {}).get("news_data", [])
            except Exception as e:
                logger.debug(f"Failed to fetch news data: {e}")
        
        return context
    
    def _build_llm_context(self, message: str, intent: str,
                          context: Dict, analysis: Dict) -> Dict:
        """Baue Kontext für LLM"""
        return {
            "user_message": message,
            "intent": intent,
            "sentiment": analysis.get("sentiment", "neutral"),
            "entities": analysis.get("entities", []),
            "is_followup": analysis.get("is_followup", False),
            "energy": context.get("energy", 0.5),
            "mood": context.get("mood", "neutral"),
            "context_hint": analysis.get("context_hint", ""),
        }
    
    def get_news_formatted(self, news_list: List[Dict],
                          energy: float = 0.5, mood: str = "neutral") -> str:
        """Hole formatierte News"""
        self.news_formatter.set_state(energy, mood)
        return self.news_formatter.format_news(news_list)
    
    def get_template_response(self, category: str, subcategory: str = "default") -> str:
        """Hole Template-basierte Antwort"""
        return ResponseTemplates.get_template(category, subcategory)


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_message_analyzer(brain=None) -> HoloMessageAnalyzer:
    """Factory für MessageAnalyzer"""
    return HoloMessageAnalyzer(brain)


def create_news_formatter(energy: float = 0.7, mood: str = "neutral") -> WolfNewsFormatter:
    """Factory für WolfNewsFormatter"""
    return WolfNewsFormatter(energy, mood)


def create_orchestrator(brain=None) -> ResponseOrchestrator:
    """Factory für ResponseOrchestrator"""
    return ResponseOrchestrator(brain)


# =============================================================================
# LEGACY COMPATIBILITY
# =============================================================================

# Alte Imports/Klassen für Kompatibilität
IntentType = None  # Wird aus smart_understanding importiert wenn nötig
IntentPriority = ResponsePriority  # Alias

class MultiIntentDetector:
    """
    LEGACY WRAPPER - Nutzt SmartUnderstanding.
    
    Neue Code sollte SmartUnderstanding direkt nutzen!
    """
    
    def __init__(self):
        logger.warning("⚠️ MultiIntentDetector ist deprecated - nutze SmartUnderstanding!")
        self._understanding = None
    
    def detect_all(self, text: str) -> List[Dict]:
        """Legacy detect Methode"""
        if self._understanding is None:
            self._understanding = get_smart_understanding()
        
        if self._understanding:
            result = self._understanding.understand(text)
            return result.get("intents", [{"intent": result.get("intent", "general")}])
        
        return [{"intent": "general", "confidence": 0.5}]


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 70)
    print("😊 HOLO MESSAGE ANALYZER v4.0 - RESPONSE ORCHESTRATOR TEST")
    print("=" * 70)
    
    analyzer = HoloMessageAnalyzer()
    
    # Test-Nachrichten
    test_messages = [
        "Hallo!",
        "Wie geht es dir?",
        "Hast du News?",
        "Danke dir!",
        "Gute Nacht!",
    ]
    
    print("\n📊 RESPONSE ORCHESTRATION:")
    print("-" * 70)
    
    for msg in test_messages:
        print(f"\n👤 User: {msg}")
        result = analyzer.analyze(msg, energy=0.7, mood="happy")
        
        print(f"😊 Holo: {result['response']}")
        print(f"   Intent: {result['primary_intent']}")
        print(f"   Needs LLM: {result['needs_llm']}")
        print(f"   Quality: {result['quality']['score']:.0%}")
    
    # Test News Formatter
    print("\n" + "-" * 70)
    print("📰 NEWS FORMATTER TEST:")
    
    test_news = [
        {"title": "KI revolutioniert die Medizin", "source": "Technik", 
         "summary": "Neue Durchbrüche in der Diagnostik..."},
        {"title": "Klimagipfel ohne Ergebnis", "source": "Welt",
         "summary": "Die Verhandlungen scheiterten..."},
    ]
    
    formatter = WolfNewsFormatter(energy_level=0.8, mood="curious")
    print(formatter.format_news(test_news))
    
    print("\n" + "=" * 70)
    print("✅ Test abgeschlossen!")
