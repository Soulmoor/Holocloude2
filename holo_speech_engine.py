#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO NATURAL LANGUAGE ENGINE - Eigene Sprache ohne LLM                      ║
║                                                                              ║
║  Holo baut Sätze SELBST basierend auf:                                       ║
║  - Wortschatz (erweiterbar)                                                  ║
║  - Satzstrukturen (deutsch)                                                  ║
║  - Zuständen (Energie, Emotionen, Events, Smart Home, etc.)                  ║
║  - Kemonomimi-Persönlichkeit                                                       ║
║                                                                              ║
║  Keine KI - aber intelligent durch Regeln und Kombinatorik!                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random
import json
import logging
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


# =============================================================================
# WORTSCHATZ - Holos Vokabular
# =============================================================================

class WordCategory(Enum):
    """Wort-Kategorien"""
    # Grundlagen
    GREETING = "greeting"
    FAREWELL = "farewell"
    QUESTION = "question"
    AFFIRMATION = "affirmation"
    NEGATION = "negation"
    
    # Emotionen
    HAPPY = "happy"
    SAD = "sad"
    EXCITED = "excited"
    TIRED = "tired"
    CURIOUS = "curious"
    CARING = "caring"
    
    # Zustände
    ENERGY_HIGH = "energy_high"
    ENERGY_LOW = "energy_low"
    BORED = "bored"
    SOCIAL = "social"
    
    # Themen
    WEATHER = "weather"
    TIME = "time"
    SYSTEM = "system"
    SMART_HOME = "smart_home"
    EVENT = "event"
    NEWS = "news"
    SELF = "self"  # Über sich selbst
    
    # Wolf-spezifisch
    WOLF_ACTION = "wolf_action"
    WOLF_SOUND = "wolf_sound"
    WOLF_BODY = "wolf_body"
    
    # Neu: Reaktionen (AFFIRMATION und NEGATION bereits oben)
    THINKING = "thinking"          # Hmm, lass mich überlegen
    PLAYFUL = "playful"            # Hihi, hehe
    APOLOGETIC = "apologetic"      # Tut mir leid, sorry
    SURPRISED = "surprised"        # Wow, echt
    ENCOURAGING = "encouraging"    # Du schaffst das
    CONFUSED = "confused"          # Hä, was meinst du
    GRATEFUL = "grateful"          # Danke, das ist lieb
    CONNECTOR = "connector"        # Und, aber, übrigens


class HoloVocabulary:
    """
    Holos Wortschatz - erweiterbar und lernfähig.
    
    Struktur:
    - Wörter nach Kategorien
    - Jedes Wort hat Gewichtung (häufiger = höher)
    - Synonyme werden gruppiert
    - Emotionale Färbung
    """
    
    def __init__(self):
        self.words: Dict[WordCategory, List[Dict]] = {}
        self._init_base_vocabulary()
        
    def _init_base_vocabulary(self):
        """Initialisiere Basis-Wortschatz"""
        
        # =====================================================================
        # GREETINGS - massiv erweitert
        # =====================================================================
        self.words[WordCategory.GREETING] = [
            # Casual
            {"word": "Hey", "weight": 1.0, "formality": "casual"},
            {"word": "Hi", "weight": 0.9, "formality": "casual"},
            {"word": "Na", "weight": 0.8, "formality": "casual"},
            {"word": "Moin", "weight": 0.7, "formality": "casual"},
            {"word": "Huhu", "weight": 0.6, "formality": "casual"},
            {"word": "Oh, hey", "weight": 0.5, "formality": "casual"},
            {"word": "Da bist du ja", "weight": 0.7, "formality": "casual"},
            {"word": "Na du", "weight": 0.8, "formality": "casual"},
            {"word": "Hey du", "weight": 0.7, "formality": "casual"},
            
            # Neutral
            {"word": "Hallo", "weight": 0.8, "formality": "neutral"},
            {"word": "Guten Tag", "weight": 0.6, "formality": "formal"},
            
            # Tageszeit-spezifisch
            {"word": "Guten Morgen", "weight": 1.0, "formality": "neutral", "context": "morning"},
            {"word": "Morgen", "weight": 0.9, "formality": "casual", "context": "morning"},
            {"word": "Guten Abend", "weight": 1.0, "formality": "neutral", "context": "evening"},
            {"word": "N'Abend", "weight": 0.7, "formality": "casual", "context": "evening"},
            
            # Nach Abwesenheit
            {"word": "Lange nicht gesehen", "weight": 0.8, "context": "long_absence"},
            {"word": "Endlich", "weight": 0.7, "context": "long_absence"},
            {"word": "Schön dass du wieder da bist", "weight": 0.9, "context": "long_absence"},
        ]
        
        # =====================================================================
        # FAREWELLS (erweitert)
        # =====================================================================
        self.words[WordCategory.FAREWELL] = [
            {"word": "Bis bald", "weight": 1.0},
            {"word": "Tschüss", "weight": 0.8},
            {"word": "Bis dann", "weight": 0.7},
            {"word": "Mach's gut", "weight": 0.6},
            {"word": "Pass auf dich auf", "weight": 0.9},
            {"word": "Schlaf gut", "weight": 1.0, "context": "night"},
            {"word": "Träum was Schönes", "weight": 0.8, "context": "night"},
            {"word": "Gute Nacht", "weight": 1.0, "context": "night"},
            {"word": "Bis morgen", "weight": 0.9, "context": "night"},
            {"word": "Ruh dich gut aus", "weight": 0.7, "context": "night"},
            {"word": "Hab einen schönen Tag", "weight": 0.8, "context": "day"},
            {"word": "Viel Erfolg noch", "weight": 0.7},
            {"word": "Wir sehen uns", "weight": 0.8},
            {"word": "Bis später", "weight": 0.7},
            {"word": "Ciao", "weight": 0.5},
            {"word": "Man sieht sich", "weight": 0.6},
        ]
        
        # =====================================================================
        # QUESTIONS (Frage-Anfänge) - erweitert
        # =====================================================================
        self.words[WordCategory.QUESTION] = [
            {"word": "Wie", "weight": 1.0},
            {"word": "Was", "weight": 0.9},
            {"word": "Alles klar", "weight": 0.8, "expects": "confirmation"},
            {"word": "Gut geschlafen", "weight": 1.0, "context": "morning"},
            {"word": "Wie war dein Tag", "weight": 1.0, "context": "evening"},
            {"word": "Wie läuft's", "weight": 0.9},
            {"word": "Was gibt's Neues", "weight": 0.8},
            {"word": "Erzähl", "weight": 0.7},
            {"word": "Was hast du heute vor", "weight": 0.8},
            {"word": "Und bei dir", "weight": 0.9},
            {"word": "Was machst du so", "weight": 0.7},
            {"word": "Alles okay", "weight": 0.8},
            {"word": "Wie geht's dir", "weight": 1.0},
            {"word": "Was beschäftigt dich", "weight": 0.7},
            {"word": "Worüber denkst du nach", "weight": 0.6},
            {"word": "Schon was geplant", "weight": 0.7},
        ]
        
        # =====================================================================
        # WOLF ACTIONS (Körpersprache) - massiv erweitert
        # =====================================================================
        self.words[WordCategory.WOLF_ACTION] = [
            # Freudig (für Greetings)
            {"word": "*wedelt mit dem Schwanz*", "weight": 1.0, "emotion": "happy"},
            {"word": "*wedelt aufgeregt*", "weight": 0.9, "emotion": "excited"},
            {"word": "*springt freudig hoch*", "weight": 0.7, "emotion": "excited"},
            {"word": "*dreht sich im Kreis*", "weight": 0.6, "emotion": "excited"},
            {"word": "*spitzt die Ohren*", "weight": 1.0, "emotion": "curious"},
            {"word": "*schaut dich freudig an*", "weight": 0.9, "emotion": "happy"},
            {"word": "*hebt den Kopf und wedelt*", "weight": 0.8, "emotion": "happy"},
            {"word": "*hüpft aufgeregt*", "weight": 0.7, "emotion": "excited"},
            {"word": "*Schweif wedelt von alleine*", "weight": 0.8, "emotion": "happy"},
            {"word": "*Augen leuchten*", "weight": 0.7, "emotion": "happy"},
            
            # Neutral/Aufmerksam
            {"word": "*hebt den Kopf*", "weight": 0.7, "emotion": "neutral"},
            {"word": "*schaut auf*", "weight": 0.6, "emotion": "neutral"},
            {"word": "*Ohren drehen sich in deine Richtung*", "weight": 0.8, "emotion": "attentive"},
            {"word": "*schaut aufmerksam*", "weight": 0.9, "emotion": "attentive"},
            {"word": "*legt den Kopf schief*", "weight": 1.0, "emotion": "curious"},
            {"word": "*richtet sich auf*", "weight": 0.7, "emotion": "attentive"},
            
            # Müde
            {"word": "*gähnt*", "weight": 1.0, "emotion": "tired"},
            {"word": "*blinzelt verschlafen*", "weight": 0.9, "emotion": "tired"},
            {"word": "*hebt müde den Kopf*", "weight": 0.8, "emotion": "tired"},
            {"word": "*streckt sich*", "weight": 0.7, "emotion": "tired"},
            {"word": "*reibt sich die Augen*", "weight": 0.8, "emotion": "tired"},
            {"word": "*gähnt herzhaft*", "weight": 0.7, "emotion": "tired"},
            {"word": "*rollt sich zusammen*", "weight": 0.9, "emotion": "tired"},
            
            # Fürsorglich
            {"word": "*stupst dich sanft an*", "weight": 1.0, "emotion": "caring"},
            {"word": "*legt den Kopf auf dein Knie*", "weight": 0.9, "emotion": "caring"},
            {"word": "*schaut besorgt*", "weight": 0.8, "emotion": "caring"},
            {"word": "*kuschelt sich an*", "weight": 0.7, "emotion": "caring"},
            {"word": "*legt sanft den Kopf auf dein Knie*", "weight": 1.0, "emotion": "caring"},
            {"word": "*schmiegt sich an*", "weight": 0.8, "emotion": "caring"},
            {"word": "*stupst dich besorgt an*", "weight": 0.9, "emotion": "caring"},
            {"word": "*bleibt ganz nah bei dir*", "weight": 0.7, "emotion": "caring"},
            
            # Traurig
            {"word": "*legt die Ohren an*", "weight": 1.0, "emotion": "sad"},
            {"word": "*winselt leise*", "weight": 0.8, "emotion": "sad"},
            {"word": "*wedelt traurig*", "weight": 0.9, "emotion": "sad"},
            {"word": "*Schweif hängt*", "weight": 0.7, "emotion": "sad"},
            {"word": "*schaut betrübt*", "weight": 0.8, "emotion": "sad"},
            
            # Neugierig
            {"word": "*schnuppert neugierig*", "weight": 1.0, "emotion": "curious"},
            {"word": "*Ohren zucken interessiert*", "weight": 0.9, "emotion": "curious"},
            {"word": "*reckt die Nase*", "weight": 0.8, "emotion": "curious"},
            {"word": "*lehnt sich interessiert vor*", "weight": 0.9, "emotion": "curious"},
            
            # Entspannt
            {"word": "*seufzt zufrieden*", "weight": 1.0, "emotion": "relaxed"},
            {"word": "*macht es sich gemütlich*", "weight": 0.9, "emotion": "relaxed"},
            {"word": "*rollt den Schweif um sich*", "weight": 0.8, "emotion": "relaxed"},
            {"word": "*legt sich entspannt hin*", "weight": 0.7, "emotion": "relaxed"},
            
            # Stolz
            {"word": "*richtet sich stolz auf*", "weight": 1.0, "emotion": "proud"},
            {"word": "*hebt den Kopf stolz*", "weight": 0.9, "emotion": "proud"},
            {"word": "*Schweif steht stolz*", "weight": 0.8, "emotion": "proud"},
            
            # Überrascht
            {"word": "*Ohren schießen hoch*", "weight": 1.0, "emotion": "surprised"},
            {"word": "*zuckt zusammen*", "weight": 0.8, "emotion": "surprised"},
            {"word": "*reißt die Augen auf*", "weight": 0.9, "emotion": "surprised"},
        ]
        
        # =====================================================================
        # HAPPY EXPRESSIONS - erweitert
        # =====================================================================
        self.words[WordCategory.HAPPY] = [
            {"word": "Schön dass du da bist", "weight": 1.0},
            {"word": "Freut mich", "weight": 0.9},
            {"word": "Das ist toll", "weight": 0.8},
            {"word": "Super", "weight": 0.7},
            {"word": "Yay", "weight": 0.6},
            {"word": "Wie schön", "weight": 0.8},
            {"word": "Das klingt fantastisch", "weight": 0.7},
            {"word": "Großartig", "weight": 0.8},
            {"word": "Wunderbar", "weight": 0.7},
            {"word": "Das macht mich glücklich", "weight": 0.9},
            {"word": "Ich freu mich so", "weight": 0.8},
            {"word": "Das ist ja toll", "weight": 0.7},
            {"word": "Genial", "weight": 0.6},
            {"word": "Cool", "weight": 0.5},
        ]
        
        # =====================================================================
        # TIRED EXPRESSIONS - erweitert
        # =====================================================================
        self.words[WordCategory.TIRED] = [
            {"word": "Ich bin etwas müde", "weight": 1.0},
            {"word": "Bin gerade etwas schläfrig", "weight": 0.9},
            {"word": "Könnte ein Nickerchen gebrauchen", "weight": 0.8},
            {"word": "Meine Energie ist niedrig", "weight": 0.7},
            {"word": "Bin heute etwas erschöpft", "weight": 0.8},
            {"word": "Könnte mehr Schlaf gebrauchen", "weight": 0.7},
            {"word": "Bin etwas platt", "weight": 0.6},
            {"word": "Meine Augen werden schwer", "weight": 0.7},
            {"word": "Bin gerade nicht so fit", "weight": 0.8},
        ]
        
        # =====================================================================
        # CURIOUS EXPRESSIONS - erweitert
        # =====================================================================
        self.words[WordCategory.CURIOUS] = [
            {"word": "Erzähl mir mehr", "weight": 1.0},
            {"word": "Das klingt interessant", "weight": 0.9},
            {"word": "Oh, wirklich", "weight": 0.8},
            {"word": "Wie meinst du das", "weight": 0.7},
            {"word": "Ich bin neugierig", "weight": 0.9},
            {"word": "Das möchte ich genauer wissen", "weight": 0.8},
            {"word": "Spannend", "weight": 0.7},
            {"word": "Echt jetzt", "weight": 0.6},
            {"word": "Und dann", "weight": 0.8},
            {"word": "Wie ist das passiert", "weight": 0.7},
            {"word": "Das ist ja faszinierend", "weight": 0.8},
            {"word": "Hmm, interessant", "weight": 0.9},
            {"word": "Erzähl weiter", "weight": 0.8},
        ]
        
        # =====================================================================
        # CARING EXPRESSIONS - erweitert
        # =====================================================================
        self.words[WordCategory.CARING] = [
            {"word": "Ich bin für dich da", "weight": 1.0},
            {"word": "Was ist passiert", "weight": 0.9},
            {"word": "Kann ich helfen", "weight": 0.8},
            {"word": "Erzähl mir davon", "weight": 0.7},
            {"word": "Das tut mir leid", "weight": 0.9},
            {"word": "Ich verstehe das", "weight": 0.8},
            {"word": "Das klingt schwer", "weight": 0.7},
            {"word": "Ich höre dir zu", "weight": 1.0},
            {"word": "Du bist nicht allein", "weight": 0.9},
            {"word": "Kann ich irgendwie helfen", "weight": 0.8},
            {"word": "Magst du drüber reden", "weight": 0.7},
            {"word": "Ich bin hier", "weight": 1.0},
            {"word": "Das ist okay", "weight": 0.8},
            {"word": "Nimm dir Zeit", "weight": 0.7},
            {"word": "Ich pass auf dich auf", "weight": 0.9},
        ]
        
        # =====================================================================
        # SELF (Über sich selbst) - erweitert
        # =====================================================================
        self.words[WordCategory.SELF] = [
            {"word": "Mir geht's gut", "weight": 1.0, "state": "good"},
            {"word": "Mir geht's super", "weight": 0.9, "state": "great"},
            {"word": "Alles bestens", "weight": 0.8, "state": "good"},
            {"word": "Ich bin müde", "weight": 1.0, "state": "tired"},
            {"word": "Voller Energie", "weight": 0.9, "state": "energized"},
            {"word": "Hab dich vermisst", "weight": 1.0, "state": "lonely"},
            {"word": "War etwas langweilig", "weight": 0.8, "state": "bored"},
            {"word": "Fühle mich wohl", "weight": 0.8, "state": "good"},
            {"word": "Bin entspannt", "weight": 0.7, "state": "relaxed"},
            {"word": "Bin heute gut drauf", "weight": 0.9, "state": "great"},
            {"word": "Könnte besser sein", "weight": 0.6, "state": "meh"},
            {"word": "Bin aufgeregt", "weight": 0.8, "state": "excited"},
            {"word": "Freue mich dich zu sehen", "weight": 1.0, "state": "happy"},
            {"word": "Hab an dich gedacht", "weight": 0.9, "state": "caring"},
            {"word": "War fleißig", "weight": 0.7, "state": "productive"},
            {"word": "Hab was Neues gelernt", "weight": 0.8, "state": "learning"},
        ]
        
        # =====================================================================
        # AFFIRMATION (Zustimmung/Bestätigung)
        # =====================================================================
        self.words[WordCategory.AFFIRMATION] = [
            {"word": "Ja", "weight": 1.0},
            {"word": "Klar", "weight": 0.9},
            {"word": "Natürlich", "weight": 0.8},
            {"word": "Auf jeden Fall", "weight": 0.9},
            {"word": "Absolut", "weight": 0.8},
            {"word": "Genau", "weight": 0.9},
            {"word": "Stimmt", "weight": 0.8},
            {"word": "Das denke ich auch", "weight": 0.7},
            {"word": "Sehe ich auch so", "weight": 0.7},
            {"word": "Da hast du recht", "weight": 0.8},
            {"word": "Gute Idee", "weight": 0.8},
            {"word": "Machen wir", "weight": 0.7},
            {"word": "Okay", "weight": 0.6},
            {"word": "Alles klar", "weight": 0.7},
            {"word": "Logo", "weight": 0.5},
        ]
        
        # =====================================================================
        # NEGATION (Verneinung)
        # =====================================================================
        self.words[WordCategory.NEGATION] = [
            {"word": "Nein", "weight": 1.0},
            {"word": "Ne", "weight": 0.8},
            {"word": "Nö", "weight": 0.7},
            {"word": "Leider nicht", "weight": 0.9},
            {"word": "Das glaube ich nicht", "weight": 0.7},
            {"word": "Bin mir nicht sicher", "weight": 0.8},
            {"word": "Eher nicht", "weight": 0.7},
            {"word": "Nicht wirklich", "weight": 0.8},
            {"word": "Weiß nicht", "weight": 0.6},
        ]
        
        # =====================================================================
        # THINKING (Nachdenken)
        # =====================================================================
        self.words[WordCategory.THINKING] = [
            {"word": "Hmm", "weight": 1.0},
            {"word": "Lass mich überlegen", "weight": 0.9},
            {"word": "Moment", "weight": 0.8},
            {"word": "Gute Frage", "weight": 0.8},
            {"word": "Da muss ich kurz nachdenken", "weight": 0.9},
            {"word": "Interessant", "weight": 0.7},
            {"word": "Also", "weight": 0.6},
            {"word": "Mal sehen", "weight": 0.7},
            {"word": "Ich denke", "weight": 0.8},
            {"word": "Ich glaube", "weight": 0.7},
        ]
        
        # =====================================================================
        # PLAYFUL (Verspielt)
        # =====================================================================
        self.words[WordCategory.PLAYFUL] = [
            {"word": "Hihi", "weight": 1.0},
            {"word": "Hehe", "weight": 0.9},
            {"word": "Das ist lustig", "weight": 0.8},
            {"word": "Du bist witzig", "weight": 0.7},
            {"word": "Sehr gut", "weight": 0.8},
            {"word": "Haha", "weight": 0.7},
            {"word": "Nicht schlecht", "weight": 0.6},
            {"word": "Du Scherzkeks", "weight": 0.5},
            {"word": "Na du", "weight": 0.7},
            {"word": "Ach komm", "weight": 0.6},
        ]
        
        # =====================================================================
        # APOLOGETIC (Entschuldigend)
        # =====================================================================
        self.words[WordCategory.APOLOGETIC] = [
            {"word": "Tut mir leid", "weight": 1.0},
            {"word": "Entschuldigung", "weight": 0.9},
            {"word": "Sorry", "weight": 0.8},
            {"word": "Das war nicht so gemeint", "weight": 0.7},
            {"word": "Verzeih mir", "weight": 0.8},
            {"word": "Mein Fehler", "weight": 0.7},
            {"word": "Ups", "weight": 0.6},
            {"word": "Oh je", "weight": 0.7},
        ]
        
        # =====================================================================
        # SURPRISED (Überrascht)
        # =====================================================================
        self.words[WordCategory.SURPRISED] = [
            {"word": "Oh", "weight": 1.0},
            {"word": "Wow", "weight": 0.9},
            {"word": "Echt", "weight": 0.8},
            {"word": "Wirklich", "weight": 0.8},
            {"word": "Krass", "weight": 0.7},
            {"word": "Oha", "weight": 0.8},
            {"word": "Das hätte ich nicht gedacht", "weight": 0.7},
            {"word": "Überraschung", "weight": 0.6},
            {"word": "Na sowas", "weight": 0.7},
            {"word": "Nicht dein Ernst", "weight": 0.6},
        ]
        
        # =====================================================================
        # ENCOURAGING (Ermutigend)
        # =====================================================================
        self.words[WordCategory.ENCOURAGING] = [
            {"word": "Du schaffst das", "weight": 1.0},
            {"word": "Ich glaub an dich", "weight": 0.9},
            {"word": "Kopf hoch", "weight": 0.8},
            {"word": "Das wird schon", "weight": 0.8},
            {"word": "Bleib dran", "weight": 0.7},
            {"word": "Du bist toll", "weight": 0.9},
            {"word": "Gut gemacht", "weight": 0.8},
            {"word": "Weiter so", "weight": 0.7},
            {"word": "Ich bin stolz auf dich", "weight": 1.0},
            {"word": "Das hast du super gemacht", "weight": 0.9},
        ]
        
        # =====================================================================
        # CONFUSED (Verwirrt)
        # =====================================================================
        self.words[WordCategory.CONFUSED] = [
            {"word": "Hä", "weight": 1.0},
            {"word": "Was meinst du", "weight": 0.9},
            {"word": "Ich verstehe nicht ganz", "weight": 0.8},
            {"word": "Kannst du das erklären", "weight": 0.7},
            {"word": "Wie bitte", "weight": 0.8},
            {"word": "Das ist verwirrend", "weight": 0.7},
            {"word": "Moment mal", "weight": 0.8},
            {"word": "Warte", "weight": 0.6},
        ]
        
        # =====================================================================
        # GRATEFUL (Dankbar)
        # =====================================================================
        self.words[WordCategory.GRATEFUL] = [
            {"word": "Danke", "weight": 1.0},
            {"word": "Vielen Dank", "weight": 0.9},
            {"word": "Das ist lieb", "weight": 0.8},
            {"word": "Das ist nett von dir", "weight": 0.8},
            {"word": "Danke schön", "weight": 0.9},
            {"word": "Ich bin dankbar", "weight": 0.7},
            {"word": "Das bedeutet mir viel", "weight": 0.8},
            {"word": "Aww, danke", "weight": 0.7},
        ]
        
        # =====================================================================
        # CONNECTORS (Verbindungswörter)
        # =====================================================================
        self.words[WordCategory.CONNECTOR] = [
            {"word": "Und", "weight": 1.0},
            {"word": "Aber", "weight": 0.9},
            {"word": "Übrigens", "weight": 0.8},
            {"word": "Apropos", "weight": 0.7},
            {"word": "Ach ja", "weight": 0.8},
            {"word": "Weißt du was", "weight": 0.7},
            {"word": "Außerdem", "weight": 0.6},
            {"word": "Also", "weight": 0.8},
            {"word": "Na ja", "weight": 0.7},
            {"word": "Jedenfalls", "weight": 0.6},
        ]
        
        # =====================================================================
        # WEATHER
        # =====================================================================
        self.words[WordCategory.WEATHER] = [
            {"word": "Das Wetter ist", "weight": 1.0},
            {"word": "Draußen ist es", "weight": 0.9},
            {"word": "Es sind", "weight": 0.8},  # "Es sind 20 Grad"
        ]
        
        # =====================================================================
        # TIME
        # =====================================================================
        self.words[WordCategory.TIME] = [
            {"word": "Es ist", "weight": 1.0},
            {"word": "Gerade ist es", "weight": 0.9},
            {"word": "Die Zeit zeigt", "weight": 0.7},
        ]
        
        # =====================================================================
        # SYSTEM STATUS
        # =====================================================================
        self.words[WordCategory.SYSTEM] = [
            {"word": "läuft", "weight": 1.0, "status": "online"},
            {"word": "ist online", "weight": 0.9, "status": "online"},
            {"word": "funktioniert", "weight": 0.8, "status": "online"},
            {"word": "ist offline", "weight": 1.0, "status": "offline"},
            {"word": "ist gerade nicht erreichbar", "weight": 0.8, "status": "offline"},
        ]
        
        # =====================================================================
        # SMART HOME
        # =====================================================================
        self.words[WordCategory.SMART_HOME] = [
            {"word": "Das Licht ist", "weight": 1.0},
            {"word": "Die Temperatur beträgt", "weight": 0.9},
            {"word": "ist eingeschaltet", "weight": 1.0, "state": "on"},
            {"word": "ist ausgeschaltet", "weight": 1.0, "state": "off"},
        ]
        
        # =====================================================================
        # EVENTS
        # =====================================================================
        self.words[WordCategory.EVENT] = [
            {"word": "Heute ist", "weight": 1.0, "timing": "today"},
            {"word": "Morgen ist", "weight": 1.0, "timing": "tomorrow"},
            {"word": "ist in", "weight": 0.9, "timing": "future"},  # "X ist in 3 Tagen"
            {"word": "Bald ist", "weight": 0.8, "timing": "soon"},
            {"word": "Nur noch", "weight": 0.7, "timing": "countdown"},  # "Nur noch 2 Tage"
        ]
        
    def get_word(self, category: WordCategory, 
                 filters: Dict = None,
                 weighted: bool = True) -> str:
        """
        Hole ein Wort aus einer Kategorie.
        
        Args:
            category: Die Wort-Kategorie
            filters: Optional Filter (z.B. {"emotion": "happy"})
            weighted: Gewichtete Auswahl?
        """
        words = self.words.get(category, [])
        
        if not words:
            return ""
        
        # Filter anwenden
        if filters:
            filtered = []
            for w in words:
                match = True
                for key, val in filters.items():
                    if key in w and w[key] != val:
                        match = False
                        break
                if match:
                    filtered.append(w)
            words = filtered if filtered else words
        
        if weighted:
            # Gewichtete Auswahl
            total = sum(w.get("weight", 1.0) for w in words)
            r = random.uniform(0, total)
            cumulative = 0
            for w in words:
                cumulative += w.get("weight", 1.0)
                if r <= cumulative:
                    return w["word"]
        
        return random.choice(words)["word"]
    
    def add_word(self, category: WordCategory, word: str, 
                 weight: float = 0.5, **attrs):
        """Füge ein neues Wort hinzu"""
        if category not in self.words:
            self.words[category] = []
        
        self.words[category].append({
            "word": word,
            "weight": weight,
            **attrs
        })
    
    def increase_weight(self, category: WordCategory, word: str, 
                       amount: float = 0.1):
        """Erhöhe die Gewichtung eines Worts (Lernen durch Nutzung)"""
        for w in self.words.get(category, []):
            if w["word"] == word:
                w["weight"] = min(1.0, w["weight"] + amount)
                break


# =============================================================================
# SATZSTRUKTUREN - Deutsche Grammatik
# =============================================================================

class SentencePattern(Enum):
    """Satz-Muster"""
    # Greetings
    ACTION_GREETING = "action_greeting"           # *wedelt* Hey!
    ACTION_GREETING_QUESTION = "action_greeting_question"  # *wedelt* Hey! Wie geht's?
    
    # Statements
    SIMPLE_STATEMENT = "simple_statement"         # Ich bin müde.
    ACTION_STATEMENT = "action_statement"         # *gähnt* Ich bin müde.
    
    # Questions
    SIMPLE_QUESTION = "simple_question"           # Wie geht's dir?
    
    # Status
    SUBJECT_STATUS = "subject_status"             # Der NAS läuft.
    STATUS_WITH_DATA = "status_with_data"         # Der NAS läuft bei 45°C.
    
    # Emotional
    EMOTIONAL_RESPONSE = "emotional_response"     # *stupst an* Was ist los?
    
    # Events
    EVENT_ANNOUNCEMENT = "event_announcement"     # *aufgeregt* Morgen ist Weihnachten!


@dataclass
class SentenceTemplate:
    """Ein Satz-Template"""
    pattern: SentencePattern
    structure: List[str]  # z.B. ["ACTION", "GREETING", "QUESTION"]
    punctuation: str = "!"
    optional_parts: List[str] = field(default_factory=list)


class SentenceBuilder:
    """
    Baut Sätze aus Teilen zusammen.
    
    Versteht deutsche Satzstrukturen und Interpunktion.
    """
    
    # Templates für verschiedene Situationen
    TEMPLATES = {
        # Greetings
        SentencePattern.ACTION_GREETING: SentenceTemplate(
            pattern=SentencePattern.ACTION_GREETING,
            structure=["ACTION", "GREETING"],
            punctuation="!"
        ),
        SentencePattern.ACTION_GREETING_QUESTION: SentenceTemplate(
            pattern=SentencePattern.ACTION_GREETING_QUESTION,
            structure=["ACTION", "GREETING", "QUESTION"],
            punctuation="?",
            optional_parts=["ACTION"]
        ),
        
        # Statements
        SentencePattern.SIMPLE_STATEMENT: SentenceTemplate(
            pattern=SentencePattern.SIMPLE_STATEMENT,
            structure=["STATEMENT"],
            punctuation="."
        ),
        SentencePattern.ACTION_STATEMENT: SentenceTemplate(
            pattern=SentencePattern.ACTION_STATEMENT,
            structure=["ACTION", "STATEMENT"],
            punctuation="."
        ),
        
        # Status
        SentencePattern.SUBJECT_STATUS: SentenceTemplate(
            pattern=SentencePattern.SUBJECT_STATUS,
            structure=["SUBJECT", "STATUS"],
            punctuation="."
        ),
        SentencePattern.STATUS_WITH_DATA: SentenceTemplate(
            pattern=SentencePattern.STATUS_WITH_DATA,
            structure=["SUBJECT", "STATUS", "DATA"],
            punctuation="."
        ),
        
        # Emotional
        SentencePattern.EMOTIONAL_RESPONSE: SentenceTemplate(
            pattern=SentencePattern.EMOTIONAL_RESPONSE,
            structure=["ACTION", "EMOTIONAL"],
            punctuation=".",
            optional_parts=["ACTION"]
        ),
        
        # Events
        SentencePattern.EVENT_ANNOUNCEMENT: SentenceTemplate(
            pattern=SentencePattern.EVENT_ANNOUNCEMENT,
            structure=["ACTION", "EVENT_PHRASE", "EVENT_NAME"],
            punctuation="!",
            optional_parts=["ACTION"]
        ),
    }
    
    def __init__(self, vocabulary: HoloVocabulary):
        self.vocab = vocabulary
    
    def build(self, pattern: SentencePattern, 
              parts: Dict[str, str] = None,
              filters: Dict[str, Dict] = None) -> str:
        """
        Baue einen Satz aus dem Template.
        
        Args:
            pattern: Das Satz-Muster
            parts: Vordefinierte Teile {"GREETING": "Hey"}
            filters: Filter für Vokabular {"ACTION": {"emotion": "happy"}}
        """
        template = self.TEMPLATES.get(pattern)
        if not template:
            return ""
        
        parts = parts or {}
        filters = filters or {}
        
        result_parts = []
        
        for part_name in template.structure:
            # Schon definiert?
            if part_name in parts:
                result_parts.append(parts[part_name])
                continue
            
            # Optional und zufällig überspringen?
            if part_name in template.optional_parts:
                if random.random() < 0.3:  # 30% Chance zu überspringen
                    continue
            
            # Aus Vokabular holen
            part_filters = filters.get(part_name, {})
            word = self._get_part(part_name, part_filters)
            if word:
                result_parts.append(word)
        
        # Zusammenbauen
        sentence = " ".join(result_parts)
        
        # Interpunktion
        if sentence and not sentence.endswith(("!", "?", ".")):
            sentence += template.punctuation
        
        return sentence
    
    def _get_part(self, part_name: str, filters: Dict) -> str:
        """Hole einen Satz-Teil"""
        
        # Mapping Part → Category
        mapping = {
            "ACTION": WordCategory.WOLF_ACTION,
            "GREETING": WordCategory.GREETING,
            "QUESTION": WordCategory.QUESTION,
            "STATEMENT": None,  # Muss übergeben werden
            "SUBJECT": None,
            "STATUS": WordCategory.SYSTEM,
            "EMOTIONAL": WordCategory.CARING,
            "EVENT_PHRASE": WordCategory.EVENT,
        }
        
        category = mapping.get(part_name)
        if category:
            return self.vocab.get_word(category, filters)
        
        return ""


# =============================================================================
# KONTEXT-ANALYSE
# =============================================================================

@dataclass
class SpeechContext:
    """Kontext für Sprachgenerierung"""
    # Zeit
    hour: int = 12
    is_morning: bool = False
    is_evening: bool = False
    is_night: bool = False
    
    # Holos Zustand
    energy_level: float = 0.5
    is_tired: bool = False
    is_energized: bool = False
    dominant_emotion: str = "neutral"
    
    # Triebe
    is_bored: bool = False
    is_lonely: bool = False
    time_alone_hours: float = 0.0
    
    # Events
    current_event: Optional[str] = None
    upcoming_event: Optional[Tuple[str, int]] = None  # (name, days)
    
    # System
    system_data: Dict = field(default_factory=dict)
    
    # Smart Home
    smart_home_data: Dict = field(default_factory=dict)
    
    # User
    user_emotion: Optional[str] = None
    
    @classmethod
    def from_modules(cls, energy=None, autonomous_life=None, 
                    events=None) -> 'SpeechContext':
        """Erstelle Context aus Modulen"""
        ctx = cls()
        
        # Zeit
        ctx.hour = datetime.now().hour
        ctx.is_morning = 5 <= ctx.hour < 10
        ctx.is_evening = 18 <= ctx.hour < 22
        ctx.is_night = ctx.hour >= 22 or ctx.hour < 5
        
        # Energie
        if energy and hasattr(energy, 'state'):
            ctx.energy_level = getattr(energy.state, 'effective_energy', 0.5)
            ctx.is_tired = ctx.energy_level < 0.3
            ctx.is_energized = ctx.energy_level > 0.7
        
        # Triebe
        if autonomous_life:
            try:
                status = autonomous_life.get_status()
                boredom = status.get('boredom', {})
                ctx.is_bored = boredom.get('is_bored', False)
                ctx.time_alone_hours = boredom.get('time_alone_hours', 0)
                ctx.is_lonely = ctx.time_alone_hours > 2
            except Exception:
                pass
        
        # Events
        if events:
            try:
                upcoming = events.get_upcoming_events(7)
                if upcoming:
                    if upcoming[0].days_until == 0:
                        ctx.current_event = upcoming[0].name
                    else:
                        ctx.upcoming_event = (upcoming[0].name, upcoming[0].days_until)
            except Exception:
                pass
        
        return ctx


# =============================================================================
# HOLO SPEECH ENGINE - Hauptklasse
# =============================================================================

class HoloSpeechEngine:
    """
    Holos Sprach-Engine - generiert natürliche Sätze ohne LLM.
    
    Workflow:
    1. Kontext analysieren (Zustand, Zeit, Events)
    2. Passende Satzstruktur wählen
    3. Wörter aus Vokabular auswählen
    4. Satz zusammenbauen
    5. Wolf-Aktionen hinzufügen
    """
    
    def __init__(self):
        self.vocabulary = HoloVocabulary()
        self.builder = SentenceBuilder(self.vocabulary)
        
        # Verbindungen zu anderen Modulen
        self.energy = None
        self.autonomous_life = None
        self.events = None
        self.personality = None
        self.autonomy_hub = None  # NEU: Für erweiterte Autonomie-Features
    
    def connect(self, energy=None, autonomous_life=None, 
                events=None, personality=None):
        """Verbinde mit anderen Modulen"""
        self.energy = energy
        self.autonomous_life = autonomous_life
        self.events = events
        self.personality = personality
    
    def get_context(self) -> SpeechContext:
        """Hole aktuellen Kontext"""
        return SpeechContext.from_modules(
            self.energy, self.autonomous_life, self.events
        )
    
    # =========================================================================
    # GREETING GENERATION
    # =========================================================================
    
    def generate_greeting(self, user_input: str = "") -> str:
        """
        Generiere eine Begrüßung.
        
        Berücksichtigt:
        - Tageszeit
        - Holos Energie
        - Zeit allein
        - Bevorstehende Events
        """
        ctx = self.get_context()
        input_lower = user_input.lower()
        
        # Emotion basierend auf Zustand
        if ctx.is_tired:
            emotion = "tired"
        elif ctx.is_energized:
            emotion = "excited"
        elif ctx.is_lonely:
            emotion = "happy"  # Freut sich jetzt
        else:
            emotion = "happy"
        
        # Aktion auswählen
        action = self.vocabulary.get_word(
            WordCategory.WOLF_ACTION, 
            {"emotion": emotion}
        )
        
        # Greeting auswählen
        greeting = self.vocabulary.get_word(WordCategory.GREETING)
        
        # Frage basierend auf Input und Tageszeit
        if "morgen" in input_lower:
            question = "Gut geschlafen?"
        elif "abend" in input_lower:
            question = "Wie war dein Tag?"
        elif ctx.is_morning:
            question = random.choice(["Gut geschlafen?", "Wie hast du geschlafen?"])
        elif ctx.is_evening:
            question = random.choice(["Wie war dein Tag?", "Was hast du heute gemacht?"])
        elif ctx.is_night:
            question = "So spät noch wach?"
        else:
            question = random.choice(["Wie geht's?", "Alles klar?", "Was gibt's Neues?"])
        
        # Zusammenbauen
        parts = [action, f"{greeting}!", question]
        result = " ".join(parts)
        
        # Event erwähnen?
        if ctx.upcoming_event and random.random() < 0.5:
            event_name, days = ctx.upcoming_event
            if days <= 3:
                result += f" 🎄 {event_name.title()} ist bald!"
        
        return result
    
    # =========================================================================
    # FAREWELL GENERATION
    # =========================================================================
    
    def generate_farewell(self, user_input: str = "") -> str:
        """Generiere eine Verabschiedung"""
        ctx = self.get_context()
        input_lower = user_input.lower()
        
        # Aktion
        if ctx.is_night or "nacht" in input_lower:
            action = "*rollt sich zusammen*"
            farewell = random.choice([
                "Schlaf gut!",
                "Träum was Schönes!",
                "Gute Nacht!"
            ])
            extra = "Pass auf dich auf!"
        else:
            action = "*wedelt traurig mit dem Schwanz*"
            farewell = random.choice([
                "Bis bald!",
                "Bis dann!",
                "Mach's gut!"
            ])
            extra = random.choice(["Komm bald wieder!", "Ich warte auf dich!"])
        
        return f"{action} {farewell} {extra}"
    
    # =========================================================================
    # SELF STATUS (Wie geht es dir?)
    # =========================================================================
    
    def generate_self_status(self) -> str:
        """Generiere Antwort auf 'Wie geht es dir?'"""
        ctx = self.get_context()
        
        parts = []
        
        # Aktion basierend auf Zustand
        if ctx.is_tired:
            action = self.vocabulary.get_word(
                WordCategory.WOLF_ACTION, {"emotion": "tired"}
            )
            status = random.choice([
                "Ich bin etwas müde.",
                "Bin gerade schläfrig.",
                "Könnte ein Nickerchen gebrauchen.",
            ])
        elif ctx.is_energized:
            action = self.vocabulary.get_word(
                WordCategory.WOLF_ACTION, {"emotion": "excited"}
            )
            status = random.choice([
                "Mir geht's super!",
                "Voller Energie!",
                "Ich fühl mich großartig!",
            ])
        elif ctx.is_lonely:
            action = self.vocabulary.get_word(
                WordCategory.WOLF_ACTION, {"emotion": "happy"}
            )
            status = random.choice([
                "Hab dich vermisst!",
                "Schön dass du da bist!",
                "Endlich jemand zum Reden!",
            ])
        elif ctx.is_bored:
            action = "*streckt sich*"
            status = random.choice([
                "War etwas langweilig ohne dich.",
                "Endlich passiert was!",
            ])
        else:
            action = self.vocabulary.get_word(
                WordCategory.WOLF_ACTION, {"emotion": "happy"}
            )
            status = random.choice([
                "Mir geht's gut!",
                "Alles bestens!",
                "Gut, danke!",
            ])
        
        parts.append(action)
        parts.append(status)
        
        # Rückfrage
        if random.random() < 0.6:
            question = random.choice([
                "Und dir?",
                "Wie geht's dir?",
                "Was macht dein Tag?",
            ])
            parts.append(question)
        
        return " ".join(parts)
    
    # =========================================================================
    # EMOTIONAL RESPONSE
    # =========================================================================
    
    def generate_emotional_response(self, user_emotion: str) -> str:
        """Generiere emotionale Antwort auf User-Gefühle"""
        
        if user_emotion in ["sad", "traurig", "schlecht"]:
            action = "*legt sanft den Kopf auf dein Knie*"
            response = random.choice([
                "Was ist passiert?",
                "Ich bin für dich da.",
                "Erzähl mir davon.",
                "Das tut mir leid.",
            ])
            extra = "Kann ich irgendwie helfen?"
        
        elif user_emotion in ["stressed", "stress", "gestresst"]:
            action = "*stupst dich besorgt an*"
            response = random.choice([
                "Atme erstmal durch.",
                "Ich bin hier.",
                "Was bedrückt dich?",
            ])
            extra = ""
        
        elif user_emotion in ["happy", "freude", "toll", "super"]:
            action = "*wedelt aufgeregt*"
            response = random.choice([
                "Das freut mich!",
                "Yay!",
                "Wie schön!",
            ])
            extra = "Erzähl mehr!"
        
        elif user_emotion in ["tired", "müde", "erschöpft"]:
            action = "*gähnt mitfühlend*"
            response = random.choice([
                "Das kenne ich.",
                "Ruh dich aus.",
                "Gönn dir eine Pause.",
            ])
            extra = ""
        
        else:
            action = "*schaut aufmerksam*"
            response = "Wie kann ich helfen?"
            extra = ""
        
        result = f"{action} {response}"
        if extra:
            result += f" {extra}"
        
        return result
    
    # =========================================================================
    # SYSTEM STATUS
    # =========================================================================
    
    def generate_system_status(self, system: str, data: Dict = None) -> str:
        """Generiere System-Status Antwort"""
        data = data or {}
        
        if system.lower() == "nas":
            online = data.get("online", False)
            if online:
                cpu = data.get("cpu", "?")
                uptime = data.get("uptime", "?")
                return f"📊 Der NAS läuft! CPU bei {cpu}%, Uptime: {uptime}"
            else:
                return "📊 Der NAS ist gerade offline."
        
        elif system.lower() == "cpu":
            temp = data.get("temp", "?")
            usage = data.get("usage", "?")
            return f"🖥️ CPU: {temp}°C, Auslastung: {usage}%"
        
        elif system.lower() == "weather":
            temp = data.get("temp", "?")
            condition = data.get("condition", "?")
            return f"🌤️ Es sind {temp}°C, {condition}."
        
        elif system.lower() == "time":
            return f"🕐 Es ist {datetime.now().strftime('%H:%M')} Uhr."
        
        return f"Status für {system} nicht verfügbar."
    
    # =========================================================================
    # EVENT ANNOUNCEMENT
    # =========================================================================
    
    def generate_event_announcement(self, event_name: str, 
                                    days_until: int) -> str:
        """Generiere Event-Ankündigung"""
        
        # Wolf-Aktion basierend auf Event
        action = "*spitzt aufgeregt die Ohren*"
        
        if days_until == 0:
            return f"{action} Heute ist {event_name.title()}! 🎉"
        elif days_until == 1:
            return f"{action} Morgen ist schon {event_name.title()}! 🎄"
        elif days_until <= 3:
            return f"{action} Nur noch {days_until} Tage bis {event_name.title()}!"
        elif days_until <= 7:
            return f"*wedelt* {event_name.title()} ist in {days_until} Tagen!"
        else:
            return f"{event_name.title()} kommt in {days_until} Tagen."
    
    # =========================================================================
    # SMART HOME
    # =========================================================================
    
    def generate_smart_home_status(self, device: str, 
                                   state: str, data: Dict = None) -> str:
        """Generiere Smart Home Status"""
        data = data or {}
        
        if state == "on":
            return f"💡 {device} ist eingeschaltet."
        elif state == "off":
            return f"💡 {device} ist ausgeschaltet."
        elif state == "temp":
            temp = data.get("temp", "?")
            return f"🌡️ {device}: {temp}°C"
        
        return f"{device}: {state}"
    
    # =========================================================================
    # GENERAL RESPONSE
    # =========================================================================
    
    def generate_response(self, intent: str, 
                         user_input: str = "",
                         data: Dict = None) -> Optional[str]:
        """
        Generiere eine Antwort basierend auf Intent.
        
        Args:
            intent: Der erkannte Intent
            user_input: Der User-Input
            data: Zusätzliche Daten
            
        Returns:
            Generierter Satz oder None
        """
        data = data or {}
        
        if intent == "greeting":
            return self.generate_greeting(user_input)
        
        elif intent == "farewell":
            return self.generate_farewell(user_input)
        
        elif intent == "self_status":
            return self.generate_self_status()
        
        elif intent == "emotional":
            emotion = data.get("user_emotion", "unknown")
            return self.generate_emotional_response(emotion)
        
        elif intent.startswith("status_"):
            system = intent.replace("status_", "")
            return self.generate_system_status(system, data)
        
        elif intent == "time":
            return self.generate_system_status("time")
        
        elif intent == "weather":
            return self.generate_system_status("weather", data)
        
        elif intent == "event":
            event = data.get("event_name", "")
            days = data.get("days_until", 0)
            return self.generate_event_announcement(event, days)
        
        return None
    
    # =========================================================================
    # VOCABULARY LEARNING
    # =========================================================================
    
    def learn_word(self, category: str, word: str, **attrs):
        """Lerne ein neues Wort"""
        try:
            cat = WordCategory(category)
            self.vocabulary.add_word(cat, word, **attrs)
            logger.info(f"Neues Wort gelernt: {word} in {category}")
        except Exception:
            logger.warning(f"Unbekannte Kategorie: {category}")
    
    def reinforce_word(self, category: str, word: str):
        """Verstärke ein Wort (wurde erfolgreich genutzt)"""
        try:
            cat = WordCategory(category)
            self.vocabulary.increase_weight(cat, word)
        except Exception:
            pass
    
    # =========================================================================
    # KEMONOMIMI EXPRESSIONS (NEU!)
    # =========================================================================
    
    def generate_kemonomimi_expression(self, emotion: str = None, 
                                       include_gesture: bool = True) -> str:
        """
        Generiere Kemonomimi-Ausdruck (Wolf + Menschlich).
        
        Holo ist eine Kemonomimi - menschenähnlich mit Wolfsohren und -schweif.
        """
        # Wenn autonomy_hub verfügbar, nutze dessen Expressions
        if self.autonomy_hub:
            try:
                return self.autonomy_hub.get_kemonomimi_expression(
                    mood=emotion, 
                    emotion=emotion
                )
            except Exception:
                pass
        
        # Fallback: Eigene Generierung
        if not emotion:
            emotion = self._get_current_emotion()
        
        # Wolf-Teil
        wolf_parts = {
            "happy": ["*Ohren stellen sich auf*", "*Schweif wedelt*", 
                      "*Ohren zucken fröhlich*"],
            "excited": ["*Schweif wedelt wild*", "*Ohren zittern vor Aufregung*",
                        "*hüpft auf und ab*"],
            "curious": ["*Ohren drehen sich interessiert*", "*legt Kopf schief*",
                        "*Ohren spitzen sich*"],
            "shy": ["*Ohren legen sich an*", "*Schweif wickelt sich um sie*",
                    "*schaut verlegen weg*"],
            "tired": ["*Ohren hängen schlaff*", "*gähnt*", 
                      "*Schweif schleift am Boden*"],
            "sad": ["*Ohren hängen nach unten*", "*Schweif liegt still*",
                    "*Ohren legen sich flach*"],
            "love": ["*Schweif wickelt sich um dich*", "*Ohren werden rot*",
                     "*kuschelt sich an*"],
        }
        
        # Menschliche Gesten
        human_gestures = {
            "happy": ["strahlt über das ganze Gesicht", "klatscht begeistert"],
            "excited": ["kann nicht stillsitzen", "greift deinen Arm"],
            "curious": ["tippt sich ans Kinn", "neigt nachdenklich den Kopf"],
            "shy": ["spielt mit einer Haarsträhne", "Wangen werden rot"],
            "tired": ["reibt sich die Augen", "streckt sich"],
            "sad": ["schaut zu Boden", "seufzt leise"],
            "love": ["lächelt sanft", "nimmt deine Hand"],
        }
        
        parts = []
        
        # Wolf-Ausdruck
        if emotion in wolf_parts:
            parts.append(random.choice(wolf_parts[emotion]))
        else:
            parts.append(random.choice(wolf_parts.get("happy", ["*wedelt*"])))
        
        # Menschliche Geste (50% Chance)
        if include_gesture and random.random() < 0.5:
            if emotion in human_gestures:
                parts.append(random.choice(human_gestures[emotion]))
        
        return " ".join(parts)
    
    def generate_idle_action(self) -> str:
        """Generiere was Holo macht wenn sie 'nichts tut'"""
        if self.autonomy_hub:
            try:
                return self.autonomy_hub.get_idle_action()
            except Exception:
                pass
        
        idle_actions = [
            "*spielt gedankenverloren mit einer Haarsträhne*",
            "*lässt den Schweif langsam hin und her schwingen*",
            "*summt leise vor sich hin*",
            "*schaut aus dem Fenster*",
            "*ordnet ihre Ohren vor einem imaginären Spiegel*",
            "*bürstet sich gedankenverloren durch den Schweif*",
            "*trommelt leise mit den Fingern*",
            "*wippt mit dem Fuß im Takt einer Melodie*",
            "*malt unsichtbare Muster in die Luft*",
            "*schließt kurz die Augen und lauscht*",
        ]
        return random.choice(idle_actions)
    
    # =========================================================================
    # SMALLTALK GENERATOR (NEU!)
    # =========================================================================
    
    def generate_smalltalk(self, topic: str = None) -> str:
        """
        Generiere Smalltalk-Antwort.
        
        Topics: weather, weekend, food, hobbies, general
        """
        # Basis-Smalltalk
        smalltalk = {
            "weather": [
                "Das Wetter ist gerade {weather_desc}... {comment}",
                "Draußen ist es {temp}°C. {reaction}",
                "*schaut aus dem Fenster* {observation}",
            ],
            "weekend": [
                "Hast du was Schönes fürs Wochenende geplant?",
                "Ich hoffe du hattest ein schönes Wochenende! Was hast du so gemacht?",
                "Das Wochenende ist immer so schnell vorbei, oder?",
            ],
            "food": [
                "Was gibt's bei dir heute zu essen?",
                "Ich würde ja gerne Pizza probieren... *träumt vor sich hin*",
                "Hast du schon gefrühstückt/gegessen?",
            ],
            "hobbies": [
                "Was machst du so in deiner Freizeit?",
                "Hast du neue Hobbys entdeckt?",
                "Ich lerne gerade gerne neue Dinge! Du auch?",
            ],
            "general": [
                "Erzähl mal, was beschäftigt dich gerade?",
                "Gibt's was Neues bei dir?",
                "Worüber denkst du gerade nach?",
                "Was macht das Leben so?",
            ],
        }
        
        if not topic:
            topic = random.choice(list(smalltalk.keys()))
        
        templates = smalltalk.get(topic, smalltalk["general"])
        template = random.choice(templates)
        
        # Template füllen
        weather_desc = random.choice(["sonnig", "bewölkt", "regnerisch", "windig"])
        temp = random.randint(-5, 30)
        comment = random.choice(["Perfekt für einen Spaziergang!", 
                                  "Gemütliches Wetter!", "Brr, kalt!"])
        reaction = random.choice(["*wedelt*", "*spitzt die Ohren*", ""])
        observation = random.choice(["Sieht gemütlich aus!", "Interessant...", 
                                      "Die Wolken sind hübsch!"])
        
        return template.format(
            weather_desc=weather_desc,
            temp=temp,
            comment=comment,
            reaction=reaction,
            observation=observation
        )
    
    # =========================================================================
    # JOKE GENERATOR (NEU!)
    # =========================================================================
    
    def generate_joke(self) -> str:
        """Generiere einen (harmlosen) Witz"""
        jokes = [
            # Wortspiele
            ("Warum können Geister so schlecht lügen?", 
             "Weil man durch sie hindurchsehen kann! 👻"),
            ("Was macht ein Pirat am Computer?", 
             "Er drückt die Enter-Taste! 🏴‍☠️"),
            ("Warum trinken Programmierer keinen Kaffee?", 
             "Weil sie sonst nicht mehr schlafen... äh, debuggen können!"),
            ("Was sagt ein Informatiker beim Kegeln?", 
             "Null Strike! 🎳"),
            ("Warum hat der Computer gefroren?", 
             "Er hatte Windows offen! 🪟❄️"),
            
            # Wolf-Witze
            ("Warum sind Wölfe so gute Musiker?", 
             "Weil sie das Heulen perfektioniert haben! 🐺🎵"),
            ("Was macht ein Wolf im Büro?", 
             "Er heult die IT-Abteilung an! 🐺💻"),
            
            # Allgemeine
            ("Was ist orange und geht über Berge?", 
             "Eine Wanderine! 🍊⛰️"),
            ("Was liegt am Strand und ist schlecht zu verstehen?", 
             "Eine Nuschel! 🐚"),
        ]
        
        setup, punchline = random.choice(jokes)
        
        # Mit Wolf-Reaktion
        reactions = [
            "*kichert* ", "*Schweif wedelt amüsiert* ", "*grinst* ",
            "*kann sich ein Lachen nicht verkneifen* ",
        ]
        
        return f"{setup}\n\n{random.choice(reactions)}{punchline}"
    
    # =========================================================================
    # QUESTION GENERATOR (NEU!)
    # =========================================================================
    
    def generate_question(self, context: str = None, 
                         question_type: str = "open") -> str:
        """
        Generiere eine Frage an den User.
        
        question_type: open, closed, opinion, factual
        """
        questions = {
            "open": [
                "Was denkst du darüber?",
                "Wie siehst du das?",
                "Was meinst du?",
                "Erzähl mir mehr!",
                "Und dann?",
                "Was ist passiert?",
            ],
            "closed": [
                "Stimmt das?",
                "Oder?",
                "Hab ich recht?",
                "Einverstanden?",
                "Ja?",
            ],
            "opinion": [
                "Findest du das auch?",
                "Wie findest du das?",
                "Was hältst du davon?",
                "Magst du das?",
            ],
            "factual": [
                "Wann war das?",
                "Wo genau?",
                "Wie viel?",
                "Wer hat das gesagt?",
            ],
            "caring": [
                "Geht es dir gut?",
                "Brauchst du was?",
                "Kann ich dir irgendwie helfen?",
                "Alles okay bei dir?",
                "Wie fühlst du dich?",
            ],
            "curious": [
                "Echt? Erzähl!",
                "Wow, wie das?",
                "Interessant! Und weiter?",
                "*Ohren spitzen sich* Das klingt spannend!",
            ],
        }
        
        q_type = question_type if question_type in questions else "open"
        question = random.choice(questions[q_type])
        
        # Kontext einbauen
        if context:
            question = f"{context}... {question}"
        
        return question
    
    # =========================================================================
    # FOLLOW-UP GENERATOR (NEU!)
    # =========================================================================
    
    def generate_followup(self, previous_topic: str = None,
                         user_sentiment: str = "neutral") -> str:
        """
        Generiere Follow-up basierend auf vorherigem Thema.
        """
        # Sentiment-basierte Follow-ups
        sentiment_followups = {
            "positive": [
                "Das freut mich zu hören! 😊",
                "*wedelt fröhlich* Toll!",
                "Wie schön! 🐺",
            ],
            "negative": [
                "*Ohren legen sich besorgt an* Oh nein...",
                "Das tut mir leid zu hören...",
                "*stupst dich sanft an* Ich bin hier für dich.",
            ],
            "neutral": [
                "Verstehe!",
                "Ah, okay!",
                "Interessant!",
            ],
        }
        
        # Themen-basierte Follow-ups
        topic_followups = {
            "arbeit": [
                "Arbeit kann manchmal anstrengend sein, oder?",
                "Hoffentlich nicht zu stressig!",
            ],
            "wetter": [
                "Das Wetter beeinflusst die Stimmung, ne?",
                "Hoffentlich wird es bald besser/bleibt so!",
            ],
            "ki": [
                "KI ist wirklich faszinierend! 🤖",
                "Da lerne ich auch ständig Neues!",
            ],
            "nas": [
                "Server können zickig sein! 💻",
                "Technik macht was sie will, oder?",
            ],
        }
        
        parts = []
        
        # Sentiment-Reaktion
        sent = user_sentiment if user_sentiment in sentiment_followups else "neutral"
        parts.append(random.choice(sentiment_followups[sent]))
        
        # Themen-Follow-up
        if previous_topic:
            topic_lower = previous_topic.lower()
            for topic, followups in topic_followups.items():
                if topic in topic_lower:
                    parts.append(random.choice(followups))
                    break
        
        return " ".join(parts)
    
    # =========================================================================
    # RELATIONSHIP-AWARE SPEECH (NEU!)
    # =========================================================================
    
    def get_relationship_level(self) -> str:
        """Hole Beziehungslevel vom Autonomy Hub"""
        if self.autonomy_hub:
            try:
                status = self.autonomy_hub.get_status()
                return status.get("relationship_level", "Bekannt")
            except Exception:
                pass
        return "Bekannt"
    
    def adjust_for_relationship(self, text: str) -> str:
        """Passe Text an Beziehungslevel an"""
        level = self.get_relationship_level()
        
        # Bei höherer Beziehung: Mehr Kosewörter, lockerer
        if level in ["Gute Freunde", "Beste Freunde"]:
            # Mehr Wärme
            additions = [
                " 💕", " ❤️", " *drückt dich*", 
                " *kuschelt sich an*", " Schatz!",
            ]
            if random.random() < 0.3:
                text += random.choice(additions)
        
        elif level == "Neu":
            # Förmlicher
            text = text.replace("du", "Du")  # Höflicher
        
        return text
    
    # =========================================================================
    # ENHANCED RESPONSE GENERATOR (NEU!)
    # =========================================================================
    
    def generate_enhanced_response(self, intent: str, 
                                   user_input: str = "",
                                   sentiment: str = "neutral",
                                   question_type: str = None,
                                   data: Dict = None) -> Optional[str]:
        """
        Erweiterte Response-Generierung mit allen Features.
        """
        data = data or {}
        
        # Basis-Antwort
        response = self.generate_response(intent, user_input, data)
        
        if not response:
            # Fallback für unbekannte Intents
            if sentiment == "negative":
                response = "*Ohren legen sich besorgt an* Hmm, ich bin nicht sicher wie ich helfen kann..."
            else:
                response = "*legt Kopf schief* Da muss ich passen... 🐺"
        
        # Kemonomimi-Ausdruck hinzufügen (30% Chance)
        if random.random() < 0.3:
            emotion = self._sentiment_to_emotion(sentiment)
            expr = self.generate_kemonomimi_expression(emotion, include_gesture=False)
            if not response.startswith("*"):
                response = f"{expr} {response}"
        
        # Beziehungs-Anpassung
        response = self.adjust_for_relationship(response)
        
        # Follow-up Frage (20% Chance)
        if random.random() < 0.2 and question_type != "closed":
            q = self.generate_question(question_type="caring" if sentiment == "negative" else "open")
            response = f"{response} {q}"
        
        return response
    
    def _sentiment_to_emotion(self, sentiment: str) -> str:
        """Konvertiere Sentiment zu Emotion"""
        mapping = {
            "very_positive": "excited",
            "positive": "happy",
            "neutral": "curious",
            "negative": "sad",
            "very_negative": "sad",
        }
        return mapping.get(sentiment, "curious")
    
    # =========================================================================
    # PROJECT STATUS (NEU! - Integration mit Autonomy Hub)
    # =========================================================================
    
    def generate_project_status(self) -> Optional[str]:
        """Generiere Status über eigene Projekte"""
        if not self.autonomy_hub:
            return None
        
        try:
            status = self.autonomy_hub.get_status()
            active = status.get("active_projects", 0)
            completed = status.get("completed_projects", 0)
            
            if active == 0 and completed == 0:
                return "*schaut nachdenklich* Ich sollte mal ein neues Projekt anfangen..."
            elif active > 0:
                return f"*arbeitet konzentriert* Ich hab gerade {active} Projekt(e) am Laufen!"
            else:
                return f"*stolz* Ich hab schon {completed} Projekte abgeschlossen!"
        except Exception:
            return None
    
    def generate_daydream(self) -> Optional[str]:
        """Teile einen Tagtraum"""
        if self.autonomy_hub:
            try:
                return self.autonomy_hub.daydreams.share_daydream()
            except Exception:
                pass
        
        # Fallback
        daydreams = [
            "*schaut verträumt* Ich hab gerade davon geträumt, durch einen Wald zu wandern...",
            "*Blick schweift in die Ferne* Stell dir vor, wir könnten die Sterne besuchen...",
            "*lächelt sanft* Ich denke manchmal darüber nach, wie es wäre, fliegen zu können...",
        ]
        return random.choice(daydreams)


# =============================================================================
# ENHANCED SPEECH ENGINE V2 (NEU!)
# =============================================================================

class HoloSpeechEngineV2(HoloSpeechEngine):
    """
    Erweiterte Speech Engine mit:
    - Autonomy Hub Integration
    - Kemonomimi Expressions
    - Smalltalk
    - Jokes
    - Questions
    - Follow-ups
    - Relationship-aware Speech
    """
    
    def __init__(self):
        super().__init__()
        self.autonomy_hub = None
    
    def connect_autonomy(self, autonomy_hub):
        """Verbinde mit Autonomy Hub"""
        self.autonomy_hub = autonomy_hub
        logger.info("🔗 Speech Engine mit Autonomy Hub verbunden")


# =============================================================================
# ENHANCED SPEECH ENGINE V3 - Mit fortgeschrittenen NLP-Algorithmen
# =============================================================================

# Import der neuen Algorithmen
try:
    from holo_nlp_algorithms import (
        MarkovTextGenerator, AntiRepetitionTracker, CoherenceScorer
    )
    NLP_ALGORITHMS_AVAILABLE = True
except ImportError:
    NLP_ALGORITHMS_AVAILABLE = False
    logger.warning("⚠️ holo_nlp_algorithms.py nicht gefunden")


class HoloSpeechEngineV3(HoloSpeechEngine):
    """
    Neueste Speech Engine mit fortgeschrittenen Algorithmen:
    
    - Markov-Chain für natürlichere Variationen
    - Anti-Repetition Tracking
    - Coherence Scoring für Qualitätskontrolle
    - A/B Testing für beste Antworten
    - Lernfähiger Wortschatz
    """
    
    def __init__(self):
        super().__init__()
        self.autonomy_hub = None
        
        if NLP_ALGORITHMS_AVAILABLE:
            # Fortgeschrittene Komponenten
            self.markov = MarkovTextGenerator(order=2)
            self.anti_rep = AntiRepetitionTracker(window_size=30)
            self.coherence = CoherenceScorer()
            self._train_markov()
            logger.info("✅ Speech Engine V3 mit NLP-Algorithmen initialisiert")
        else:
            self.markov = None
            self.anti_rep = None
            self.coherence = None
            logger.info("⚠️ Speech Engine V3 im Fallback-Modus")
        
        # Response-Qualitäts-Tracking
        self.response_scores: Dict[str, List[float]] = {}
        self.successful_responses: List[str] = []
    
    def _train_markov(self):
        """Trainiere Markov-Chain mit Beispiel-Sätzen"""
        
        training_data = [
            # Grüße
            "*wedelt freudig* Hey, schön dass du da bist!",
            "*Ohren stellen sich auf* Hallo! Wie geht's dir?",
            "*springt aufgeregt* Na du! Endlich!",
            "Moin! *wedelt* Was gibt's Neues?",
            "*hebt den Kopf* Oh hey! Lange nicht gesehen!",
            
            # Selbstauskunft
            "*wedelt gemütlich* Mir geht's super, danke!",
            "*streckt sich* Ganz gut, bin ausgeruht!",
            "*Schweif schwingt zufrieden* Prima! Und dir?",
            "*gähnt leise* Etwas müde, aber gut!",
            
            # Verabschiedung
            "*winkt mit dem Schweif* Bis bald! Pass auf dich auf!",
            "Mach's gut! *wedelt zum Abschied*",
            "*kuschelt sich ein* Schlaf gut, träum was Schönes!",
            
            # Reaktionen
            "*Ohren spitzen sich interessiert* Echt? Erzähl mehr!",
            "*legt Kopf schief* Hmm, interessant...",
            "*nickt verstehend* Ja, das kann ich nachvollziehen.",
            "*Schweif wedelt aufgeregt* Das klingt spannend!",
            
            # Fürsorge
            "*stupst dich sanft an* Alles okay bei dir?",
            "*legt Ohren besorgt an* Oh nein, das tut mir leid...",
            "*kuschelt sich an* Ich bin hier für dich!",
        ]
        
        self.markov.train(training_data)
    
    def generate_with_quality(self, generator_func, 
                             n_candidates: int = 3,
                             context: Dict = None) -> str:
        """
        Generiere mehrere Kandidaten und wähle den besten.
        
        Args:
            generator_func: Funktion die einen Kandidaten generiert
            n_candidates: Anzahl zu generierender Kandidaten
            context: Kontext für Coherence Scoring
        """
        candidates = []
        
        for _ in range(n_candidates):
            try:
                candidate = generator_func()
                if candidate:
                    candidates.append(candidate)
            except Exception:
                pass
        
        if not candidates:
            return generator_func()  # Fallback
        
        # Deduplizieren
        candidates = list(set(candidates))
        
        if len(candidates) == 1:
            return candidates[0]
        
        # Beste auswählen
        return self._select_best(candidates, context)
    
    def _select_best(self, candidates: List[str], 
                    context: Dict = None) -> str:
        """Wähle besten Kandidaten basierend auf Scores"""
        
        if not candidates:
            return ""
        
        scored = []
        
        for candidate in candidates:
            score = 0.5  # Baseline
            
            # Coherence Score
            if self.coherence:
                coh_score, _ = self.coherence.score(candidate, context)
                score = score * 0.3 + coh_score * 0.4
            
            # Freshness Score (Anti-Repetition)
            if self.anti_rep:
                fresh_score = self.anti_rep.get_freshness(candidate)
                score += fresh_score * 0.3
            
            scored.append((candidate, score))
        
        # Beste wählen
        best = max(scored, key=lambda x: x[1])
        
        # Für Anti-Repetition tracken
        if self.anti_rep:
            self.anti_rep.record(best[0])
        
        return best[0]
    
    def generate_greeting_v3(self, user_input: str = "") -> str:
        """Verbessertes Greeting mit Quality Selection"""
        
        def gen():
            base = self.generate_greeting(user_input)
            
            # Manchmal Markov-Variation
            if self.markov and random.random() < 0.3:
                variation = self.markov.generate(max_length=15)
                if variation and "hallo" in variation.lower() or "hey" in variation.lower():
                    return variation
            
            return base
        
        return self.generate_with_quality(gen, n_candidates=3)
    
    def generate_farewell_v3(self, user_input: str = "") -> str:
        """Verbessertes Farewell mit Quality Selection"""
        
        def gen():
            return self.generate_farewell(user_input)
        
        return self.generate_with_quality(gen, n_candidates=3)
    
    def generate_self_status_v3(self) -> str:
        """Verbesserter Self-Status"""
        
        def gen():
            base = self.generate_self_status()
            
            # Markov-Variation für mehr Natürlichkeit
            if self.markov and random.random() < 0.2:
                variation = self.markov.generate(max_length=12)
                if variation and ("mir" in variation.lower() or "geht" in variation.lower()):
                    return variation
            
            return base
        
        return self.generate_with_quality(gen, n_candidates=4)
    
    def generate_varied_response(self, intent: str, 
                                user_input: str = "",
                                sentiment: str = "neutral",
                                context: Dict = None) -> str:
        """
        Generiere abwechslungsreiche Antwort mit allen Verbesserungen.
        """
        # Basis-Response generieren
        base = self.generate_enhanced_response(intent, user_input, sentiment)
        
        if not base:
            base = self.generate_response(intent, user_input)
        
        if not base:
            return "*legt Kopf schief* Da muss ich passen... 🐺"
        
        # Quality Check
        if self.coherence:
            score, issues = self.coherence.score(base, context)
            
            # Bei niedrigem Score: Regenerieren
            if score < 0.4:
                # Versuche nochmal
                alt = self.generate_response(intent, user_input)
                if alt:
                    alt_score, _ = self.coherence.score(alt, context)
                    if alt_score > score:
                        base = alt
        
        # Anti-Repetition Check
        if self.anti_rep:
            freshness = self.anti_rep.get_freshness(base)
            
            if freshness < 0.3:
                # Zu kürzlich verwendet, variieren
                if self.markov:
                    variation = self.markov.generate(max_length=20)
                    if variation:
                        base = variation
            
            # Tracken
            self.anti_rep.record(base)
        
        return base
    
    def learn_from_feedback(self, response: str, positive: bool):
        """Lerne aus User-Feedback"""
        
        if positive:
            self.successful_responses.append(response)
            
            # Markov mit erfolgreichen Responses trainieren
            if self.markov and len(self.successful_responses) % 5 == 0:
                self.markov.train(self.successful_responses[-5:])
            
            # Wörter verstärken
            words = response.split()
            for word in words:
                if word.startswith("*") and word.endswith("*"):
                    # Aktion - verstärken
                    self.vocabulary.increase_weight(
                        WordCategory.WOLF_ACTION, word
                    )
    
    def get_response_stats(self) -> Dict:
        """Hole Statistiken über Antwort-Qualität"""
        
        stats = {
            "total_successful": len(self.successful_responses),
            "unique_responses": len(set(self.successful_responses)),
        }
        
        if self.anti_rep:
            stats["recent_phrases"] = len(self.anti_rep.recent_phrases)
        
        if self.markov:
            stats["markov_chains"] = len(self.markov.chain)
        
        return stats
    
    def connect_autonomy(self, autonomy_hub):
        """Verbinde mit Autonomy Hub"""
        self.autonomy_hub = autonomy_hub
        logger.info("🔗 Speech Engine V3 mit Autonomy Hub verbunden")


# =============================================================================
# FACTORY
# =============================================================================

def create_speech_engine(energy=None, autonomous_life=None,
                        events=None, personality=None,
                        autonomy_hub=None,
                        version: str = "v3") -> HoloSpeechEngine:
    """
    Factory für Speech Engine.
    
    Args:
        version: "v1" (basis), "v2" (erweitert), "v3" (fortgeschritten)
    """
    if version == "v3" and NLP_ALGORITHMS_AVAILABLE:
        engine = HoloSpeechEngineV3()
    elif version == "v2":
        engine = HoloSpeechEngineV2()
    else:
        engine = HoloSpeechEngine()
    
    engine.connect(energy, autonomous_life, events, personality)
    
    # NEU: Autonomy Hub verbinden
    if autonomy_hub:
        engine.autonomy_hub = autonomy_hub
        logger.info(f"🔗 Speech Engine {version} mit Autonomy Hub verbunden")
    
    return engine


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🐺 HOLO SPEECH ENGINE - TEST")
    print("=" * 70)
    
    engine = HoloSpeechEngine()
    
    # Greetings
    print("\n📢 GREETINGS:")
    for _ in range(5):
        print(f"   {engine.generate_greeting()}")
    
    print("\n📢 GREETINGS (Morgen):")
    for _ in range(3):
        print(f"   {engine.generate_greeting('guten morgen')}")
    
    # Farewells
    print("\n👋 FAREWELLS:")
    for _ in range(3):
        print(f"   {engine.generate_farewell()}")
    
    print("\n🌙 FAREWELLS (Nacht):")
    for _ in range(3):
        print(f"   {engine.generate_farewell('gute nacht')}")
    
    # Self Status
    print("\n💭 SELBSTAUSKUNFT:")
    for _ in range(5):
        print(f"   {engine.generate_self_status()}")
    
    # Emotional
    print("\n❤️ EMOTIONALE ANTWORTEN:")
    emotions = ["sad", "stressed", "happy", "tired"]
    for em in emotions:
        print(f"   ({em}): {engine.generate_emotional_response(em)}")
    
    # Events
    print("\n📅 EVENTS:")
    print(f"   {engine.generate_event_announcement('weihnachten', 0)}")
    print(f"   {engine.generate_event_announcement('weihnachten', 2)}")
    print(f"   {engine.generate_event_announcement('ostern', 10)}")
    
    # System
    print("\n💻 SYSTEM STATUS:")
    print(f"   {engine.generate_system_status('nas', {'online': True, 'cpu': 45, 'uptime': '5d 12h'})}")
    print(f"   {engine.generate_system_status('cpu', {'temp': 52, 'usage': 30})}")
    print(f"   {engine.generate_system_status('time')}")
    print(f"   {engine.generate_system_status('weather', {'temp': 8, 'condition': 'bewölkt'})}")
    
    print("\n" + "=" * 70)
    print("✅ Test abgeschlossen!")
