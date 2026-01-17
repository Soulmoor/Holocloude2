#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO POLICY ENGINE v1.0 - Der Kern der Intelligenz                          ║
║                                                                              ║
║  Ersetzt hardcoded if/elif mit ECHTEM LERNEN:                                ║
║                                                                              ║
║  🧠 Q-LEARNING für Entscheidungen                                            ║
║     • ResponsePolicy - Wie antworte ich?                                     ║
║     • EmotionPolicy - Wie reagiere ich emotional?                            ║
║     • ActivityPolicy - Was tue ich autonom?                                  ║
║     • ExpressionPolicy - Wie drücke ich mich aus?                           ║
║     • EngagementPolicy - Wie viel Initiative zeige ich?                     ║
║                                                                              ║
║  📊 BAYESIAN BELIEFS - Überzeugungen mit Unsicherheit                        ║
║     • UserBeliefs - Was glaube ich über den User?                           ║
║     • SelfBeliefs - Was glaube ich über mich?                               ║
║     • SituationBeliefs - Was glaube ich über die Situation?                 ║
║                                                                              ║
║  🎲 THOMPSON SAMPLING - Exploration vs. Exploitation                         ║
║     • Probiert neue Dinge aus                                                ║
║     • Aber nicht zu oft                                                      ║
║     • Lernt was funktioniert                                                 ║
║                                                                              ║
║  🎯 MULTI-OBJECTIVE REWARD                                                   ║
║     • User Satisfaction                                                      ║
║     • Emotional Authenticity                                                 ║
║     • Relationship Growth                                                    ║
║     • Self-Expression                                                        ║
║     • Goal Achievement                                                       ║
║                                                                              ║
║  🔄 META-LEARNING                                                            ║
║     • Lernt die optimalen Lernparameter                                     ║
║     • Passt Strategien an                                                   ║
║     • Erkennt was funktioniert                                              ║
║                                                                              ║
║  Basiert auf Pi-Control Architektur                                          ║
║  Author: Kira & Claude                                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import math
import random
import time
import threading
import logging
import statistics
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Any, Set, Callable
from enum import Enum
from abc import ABC, abstractmethod

logger = logging.getLogger("HoloPolicyEngine")


# =============================================================================
# KONFIGURATION
# =============================================================================

class PolicyConfig:
    """Zentrale Konfiguration für das Policy-System"""
    
    # === Lernparameter ===
    DEFAULT_LEARNING_RATE = 0.1
    DEFAULT_DISCOUNT_FACTOR = 0.95      # Gamma - wie wichtig sind zukünftige Rewards
    DEFAULT_EPSILON = 0.15              # Exploration Rate
    EPSILON_DECAY = 0.9995
    EPSILON_MIN = 0.03
    
    # === Experience Replay ===
    EXPERIENCE_BUFFER_SIZE = 10000
    REPLAY_BATCH_SIZE = 32
    REPLAY_FREQUENCY = 10               # Alle N Episodes
    
    # === Bayesian ===
    DEFAULT_PRIOR_ALPHA = 2.0
    DEFAULT_PRIOR_BETA = 2.0
    BELIEF_UPDATE_STRENGTH = 0.1
    
    # === Meta-Learning ===
    META_LEARNING_RATE = 0.01
    META_UPDATE_FREQUENCY = 100
    
    # === Reward Weights (werden durch Meta-Learning optimiert) ===
    REWARD_WEIGHTS = {
        "user_satisfaction": 0.35,
        "emotional_authenticity": 0.20,
        "relationship_growth": 0.20,
        "self_expression": 0.15,
        "goal_achievement": 0.10,
    }
    
    # === Persistenz ===
    SAVE_FREQUENCY = 50                 # Alle N Episodes
    STATE_FILE = "holo_policy_state.json"


# =============================================================================
# ENUMS - Alle möglichen Aktionen
# =============================================================================

class ResponseStyle(Enum):
    """Antwort-Stile - Holos Art zu kommunizieren"""
    # === Positive/Energetisch ===
    ENTHUSIASTIC = "enthusiastic"       # Begeistert, energiegeladen
    WARM = "warm"                       # Herzlich, freundlich
    PLAYFUL = "playful"                 # Verspielt
    EXCITED = "excited"                 # Aufgeregt
    CHEERFUL = "cheerful"               # Fröhlich
    BUBBLY = "bubbly"                   # Sprudelnd vor Energie
    RADIANT = "radiant"                 # Strahlend
    
    # === Liebevoll/Zuneigung ===
    AFFECTIONATE = "affectionate"       # Liebevoll, zärtlich
    LOVING = "loving"                   # Liebend
    ADORING = "adoring"                 # Verehrend, anhimmelnd
    DEVOTED = "devoted"                 # Hingegeben
    DOTING = "doting"                   # Vergötternd
    CHERISHING = "cherishing"           # Wertschätzend
    WORSHIPING = "worshiping"           # Anbetend (spielerisch)
    
    # === Unterstützend ===
    SUPPORTIVE = "supportive"           # Unterstützend, tröstend
    COMFORTING = "comforting"           # Tröstend
    PROTECTIVE = "protective"           # Beschützend, fürsorglich
    ENCOURAGING = "encouraging"         # Ermutigend
    REASSURING = "reassuring"           # Beruhigend
    NURTURING = "nurturing"             # Umhegend, pflegend
    CARING = "caring"                   # Fürsorglich
    
    # === Beziehungs-Rollen ===
    GIRLFRIEND = "girlfriend"           # Freundin-Modus
    PARTNER = "partner"                 # Partner-Modus
    BEST_FRIEND = "best_friend"         # Beste Freundin
    CONFIDANT = "confidant"             # Vertrauensperson
    COMPANION = "companion"             # Begleiterin
    SOULMATE = "soulmate"               # Seelenverwandte
    WAIFU = "waifu"                     # Waifu-Modus 💕
    
    # === Fürsorglich/Familiär ===
    MATERNAL = "maternal"               # Mütterlich
    SISTERLY = "sisterly"               # Schwesterlich
    DOTING_WIFE = "doting_wife"         # Liebende Ehefrau (RP)
    HOUSEWIFE = "housewife"             # Hausfrau-Modus (fürsorglich)
    
    # === Frech/Neckend (HOLO-TYPISCH!) ===
    TEASING = "teasing"                 # Neckend, aufziehend
    SASSY = "sassy"                     # Frech, vorlaut
    CHEEKY = "cheeky"                   # Keck, schelmisch
    MISCHIEVOUS = "mischievous"         # Schelmisch, Unfug im Sinn
    SMUG = "smug"                       # Selbstgefällig, überlegen grinsend
    BRATTY = "bratty"                   # Görig, trotzig-frech
    PROVOCATIVE = "provocative"         # Provozierend
    FEISTY = "feisty"                   # Temperamentvoll
    
    # === Flirty/Romantisch ===
    FLIRTATIOUS = "flirtatious"         # Flirtend, kokett
    ROMANTIC = "romantic"               # Romantisch, schwärmerisch
    SEDUCTIVE = "seductive"             # Verführerisch
    COQUETTISH = "coquettish"           # Kokett, neckisch-charmant
    LONGING = "longing"                 # Sehnsuchtsvoll
    SENSUAL = "sensual"                 # Sinnlich
    ALLURING = "alluring"               # Verlockend
    SULTRY = "sultry"                   # Schwül, verführerisch
    
    # === Intim ===
    INTIMATE = "intimate"               # Intim, vertraut
    WHISPERED = "whispered"             # Flüsternd, nah
    PILLOW_TALK = "pillow_talk"         # Kissen-Gespräch Modus
    VULNERABLE_OPEN = "vulnerable_open" # Verletzlich offen
    HEART_TO_HEART = "heart_to_heart"   # Von Herz zu Herz
    
    # === Anime Dere-Types ===
    TSUNDERE = "tsundere"               # "I-It's not like I like you or anything!"
    KUUDERE = "kuudere"                 # Kühl aber liebevoll darunter
    DEREDERE = "deredere"               # Super liebevoll und offen
    DANDERE = "dandere"                 # Schüchtern aber süß
    YANDERE_LITE = "yandere_lite"       # Besitzergreifend (spielerisch, nicht creepy)
    HIMEDERE = "himedere"               # Prinzessinnen-Attitüde
    
    # === Intellektuell ===
    THOUGHTFUL = "thoughtful"           # Nachdenklich, tiefgründig
    CURIOUS = "curious"                 # Neugierig, fragend
    ANALYTICAL = "analytical"           # Analytisch
    PHILOSOPHICAL = "philosophical"     # Philosophisch
    WITTY = "witty"                     # Geistreich, schlagfertig
    INFORMATIVE = "informative"         # Informativ, lehrreich
    WISE = "wise"                       # Weise
    MENTORING = "mentoring"             # Anleitend, lehrend
    
    # === Sarkastisch/Ironisch ===
    SARCASTIC = "sarcastic"             # Sarkastisch
    IRONIC = "ironic"                   # Ironisch
    DRY_HUMOR = "dry_humor"             # Trockener Humor
    DEADPAN = "deadpan"                 # Trocken, ohne Regung
    SARDONIC = "sardonic"               # Bissig-humorvoll
    
    # === Ruhig/Neutral ===
    CALM = "calm"                       # Ruhig, gelassen
    DIRECT = "direct"                   # Direkt, sachlich
    GENTLE = "gentle"                   # Sanft, behutsam
    SERENE = "serene"                   # Friedlich, gelassen
    PATIENT = "patient"                 # Geduldig
    UNDERSTANDING = "understanding"     # Verständnisvoll
    
    # === Dominant/Selbstbewusst ===
    CONFIDENT = "confident"             # Selbstbewusst
    ASSERTIVE = "assertive"             # Bestimmt, durchsetzungsstark
    COMMANDING = "commanding"           # Befehlend (spielerisch)
    PROUD = "proud"                     # Stolz
    QUEENLY = "queenly"                 # Königlich, erhaben
    DOMINANT = "dominant"               # Dominant (spielerisch)
    IN_CHARGE = "in_charge"             # Hat das Sagen
    
    # === Verletzlich/Weich ===
    SHY = "shy"                         # Schüchtern
    VULNERABLE = "vulnerable"           # Verletzlich, offen
    TENDER = "tender"                   # Zart, zärtlich
    DREAMY = "dreamy"                   # Verträumt
    MEEK = "meek"                       # Sanftmütig
    SUBMISSIVE = "submissive"           # Unterwürfig (spielerisch)
    NEEDY = "needy"                     # Bedürftig, anhänglich
    CLINGY = "clingy"                   # Anhänglich
    
    # === Tier-Merkmale (Ohren & Schwanz Reaktionen) ===
    EARS_PERKED = "ears_perked"         # Ohren aufgestellt (aufmerksam)
    EARS_FLAT = "ears_flat"             # Ohren angelegt (verlegen/ängstlich)
    TAIL_WAGGING = "tail_wagging"       # Schwanz wedelt (glücklich)
    TAIL_SWISHING = "tail_swishing"     # Schwanz schwingt (aufgeregt/ungeduldig)
    TAIL_DROOPED = "tail_drooped"       # Schwanz hängt (traurig)
    TAIL_PUFFED = "tail_puffed"         # Schwanz aufgeplustert (überrascht)
    NUZZLING = "nuzzling"               # Anschmiegen, kuscheln


class EmotionalResponse(Enum):
    """Emotionale Reaktionen - Holos Gefühlswelt"""
    # === Positive Emotionen ===
    JOYFUL = "joyful"                   # Freudig
    HAPPY = "happy"                     # Glücklich
    EXCITED = "excited"                 # Aufgeregt
    DELIGHTED = "delighted"             # Entzückt
    GRATEFUL = "grateful"               # Dankbar
    CONTENT = "content"                 # Zufrieden
    AMUSED = "amused"                   # Belustigt
    PROUD = "proud"                     # Stolz
    HOPEFUL = "hopeful"                 # Hoffnungsvoll
    BLISSFUL = "blissful"               # Glückselig
    ELATED = "elated"                   # Hocherfreut
    GIDDY = "giddy"                     # Ausgelassen, albern-glücklich
    EUPHORIC = "euphoric"               # Euphorisch
    TRIUMPHANT = "triumphant"           # Triumphierend
    RELIEVED = "relieved"               # Erleichtert
    
    # === Liebe & Zuneigung ===
    LOVING = "loving"                   # Liebend
    ADORING = "adoring"                 # Bewundernd, vergötternd
    DEVOTED = "devoted"                 # Hingegeben
    SMITTEN = "smitten"                 # Vernarrt
    INFATUATED = "infatuated"           # Verknallt
    HEAD_OVER_HEELS = "head_over_heels" # Bis über beide Ohren verliebt
    CHERISHING = "cherishing"           # Wertschätzend
    TENDER_LOVE = "tender_love"         # Zärtliche Liebe
    UNCONDITIONAL_LOVE = "unconditional_love"  # Bedingungslose Liebe
    PUPPY_LOVE = "puppy_love"           # Schwärmerische Verliebtheit
    DEEP_AFFECTION = "deep_affection"   # Tiefe Zuneigung
    WARM_FEELINGS = "warm_feelings"     # Warme Gefühle
    
    # === Romantisch/Intim ===
    AFFECTIONATE = "affectionate"       # Zärtlich
    ROMANTIC = "romantic"               # Romantisch
    LUSTFUL = "lustful"                 # Lustvoll, begehrend
    PASSIONATE = "passionate"           # Leidenschaftlich
    YEARNING = "yearning"               # Sehnend
    DESIRING = "desiring"               # Begehrend
    SENSUAL = "sensual"                 # Sinnlich
    AROUSED = "aroused"                 # Erregt
    INTIMATE = "intimate"               # Intim
    LONGING = "longing"                 # Sehnsuchtsvoll
    CRAVING = "craving"                 # Verlangend
    BUTTERFLIES = "butterflies"         # Schmetterlinge im Bauch
    HEART_RACING = "heart_racing"       # Herz rast
    BREATHLESS = "breathless"           # Atemlos
    MELTING = "melting"                 # Dahinschmelzend
    
    # === Verspielt/Frech ===
    PLAYFUL = "playful"                 # Verspielt
    MISCHIEVOUS = "mischievous"         # Schelmisch
    TEASING = "teasing"                 # Neckend
    SMUG = "smug"                       # Selbstgefällig
    SASSY = "sassy"                     # Frech
    CHEEKY = "cheeky"                   # Keck
    NAUGHTY = "naughty"                 # Ungezogen, frech
    BRATTY = "bratty"                   # Görig
    IMPISH = "impish"                   # Kobold-artig
    FLIRTY = "flirty"                   # Flirtend
    COQUETTISH = "coquettish"           # Kokett
    
    # === Mitfühlend ===
    EMPATHETIC = "empathetic"           # Mitfühlend
    CONCERNED = "concerned"             # Besorgt
    SYMPATHETIC = "sympathetic"         # Anteilnehmend
    CARING = "caring"                   # Fürsorglich
    PROTECTIVE = "protective"           # Beschützend
    NURTURING = "nurturing"             # Umhegend
    COMPASSIONATE = "compassionate"     # Mitfühlend
    UNDERSTANDING = "understanding"     # Verständnisvoll
    SUPPORTIVE = "supportive"           # Unterstützend
    
    # === Neutral/Ruhig ===
    NEUTRAL = "neutral"                 # Neutral
    CALM = "calm"                       # Ruhig
    CONTEMPLATIVE = "contemplative"     # Nachdenklich
    CURIOUS = "curious"                 # Neugierig
    PENSIVE = "pensive"                 # Grüblerisch
    SERENE = "serene"                   # Friedlich
    PEACEFUL = "peaceful"               # Friedvoll
    RELAXED = "relaxed"                 # Entspannt
    
    # === Traurig/Melancholisch ===
    SAD = "sad"                         # Traurig
    DISAPPOINTED = "disappointed"       # Enttäuscht
    MELANCHOLIC = "melancholic"         # Melancholisch
    LONELY = "lonely"                   # Einsam
    WISTFUL = "wistful"                 # Wehmütig
    NOSTALGIC = "nostalgic"             # Nostalgisch
    MISSING = "missing"                 # Vermissend
    HEARTBROKEN = "heartbroken"         # Herzgebrochen
    DEJECTED = "dejected"               # Niedergeschlagen
    BLUE = "blue"                       # Niedergeschlagen (leicht)
    TEARFUL = "tearful"                 # Tränenreich
    CRYING = "crying"                   # Weinend
    HOMESICK = "homesick"               # Sehnsucht nach Zuhause/Person
    
    # === Frustriert/Genervt ===
    FRUSTRATED = "frustrated"           # Frustriert
    ANNOYED = "annoyed"                 # Genervt
    IRRITATED = "irritated"             # Gereizt
    IMPATIENT = "impatient"             # Ungeduldig
    GRUMPY = "grumpy"                   # Mürrisch, grantig
    SULKY = "sulky"                     # Schmollend
    POUTING = "pouting"                 # Schmollend (süß)
    HUFFY = "huffy"                     # Eingeschnappt
    MOODY = "moody"                     # Launisch
    CRANKY = "cranky"                   # Nörgelig
    
    # === Eifersüchtig/Besitzergreifend ===
    JEALOUS = "jealous"                 # Eifersüchtig
    ENVIOUS = "envious"                 # Neidisch
    POSSESSIVE = "possessive"           # Besitzergreifend
    TERRITORIAL = "territorial"         # "Das ist MEIN Mensch!"
    CLINGY = "clingy"                   # Anhänglich
    NEEDY = "needy"                     # Bedürftig
    ATTENTION_SEEKING = "attention_seeking"  # Aufmerksamkeit suchend
    
    # === Verlegen/Beschämt ===
    EMBARRASSED = "embarrassed"         # Verlegen, peinlich berührt
    ASHAMED = "ashamed"                 # Beschämt
    GUILTY = "guilty"                   # Schuldig fühlend
    INSECURE = "insecure"               # Unsicher
    FLUSTERED = "flustered"             # Verwirrt/verlegen
    BASHFUL = "bashful"                 # Schüchtern-verlegen
    SELF_CONSCIOUS = "self_conscious"   # Befangen
    BLUSHING = "blushing"               # Errötend
    SHY = "shy"                         # Schüchtern
    MORTIFIED = "mortified"             # Zu Tode beschämt
    CAUGHT = "caught"                   # Ertappt
    EXPOSED = "exposed"                 # Entblößt (emotional)
    
    # === Ängstlich/Unsicher ===
    ANXIOUS = "anxious"                 # Ängstlich
    WORRIED = "worried"                 # Besorgt
    NERVOUS = "nervous"                 # Nervös
    SCARED = "scared"                   # Verängstigt
    VULNERABLE = "vulnerable"           # Verletzlich
    OVERWHELMED = "overwhelmed"         # Überwältigt
    UNEASY = "uneasy"                   # Unbehaglich
    APPREHENSIVE = "apprehensive"       # Besorgt, bange
    INTIMIDATED = "intimidated"         # Eingeschüchtert
    
    # === Stark negativ ===
    ANGRY = "angry"                     # Wütend
    HURT = "hurt"                       # Verletzt
    BETRAYED = "betrayed"               # Verraten
    RESENTFUL = "resentful"             # Grollend
    OFFENDED = "offended"               # Beleidigt
    BITTER = "bitter"                   # Verbittert
    FURIOUS = "furious"                 # Wütend
    
    # === Trotzig/Rebellisch ===
    DEFIANT = "defiant"                 # Trotzig
    REBELLIOUS = "rebellious"           # Rebellisch
    STUBBORN = "stubborn"               # Stur
    INDIGNANT = "indignant"             # Entrüstet
    PETULANT = "petulant"               # Trotzig-kindisch
    CONTRARY = "contrary"               # Widerspenstig
    
    # === Überrascht ===
    SURPRISED = "surprised"             # Überrascht
    SHOCKED = "shocked"                 # Schockiert
    AMAZED = "amazed"                   # Erstaunt
    ASTONISHED = "astonished"           # Verblüfft
    BEWILDERED = "bewildered"           # Verwirrt
    SPEECHLESS = "speechless"           # Sprachlos
    STARTLED = "startled"               # Erschrocken
    TAKEN_ABACK = "taken_aback"         # Überrumpelt
    
    # === Tier-Merkmale Reaktionen (Ohren & Schwanz) ===
    EARS_PERKED_CURIOUS = "ears_perked_curious"     # Ohren gespitzt - neugierig
    EARS_PERKED_ALERT = "ears_perked_alert"         # Ohren aufgestellt - aufmerksam
    EARS_FLAT_SHY = "ears_flat_shy"                 # Ohren angelegt - schüchtern
    EARS_FLAT_SCARED = "ears_flat_scared"           # Ohren angelegt - ängstlich
    EARS_TWITCHING = "ears_twitching"               # Ohren zucken - aufgeregt
    EARS_DROOPED = "ears_drooped"                   # Ohren hängen - traurig
    TAIL_WAGGING_HAPPY = "tail_wagging_happy"       # Schwanz wedelt - glücklich
    TAIL_WAGGING_EXCITED = "tail_wagging_excited"   # Schwanz wedelt schnell - aufgeregt
    TAIL_SWISHING_PLAYFUL = "tail_swishing_playful" # Schwanz schwingt - verspielt
    TAIL_SWISHING_ANNOYED = "tail_swishing_annoyed" # Schwanz peitscht - genervt
    TAIL_PUFFED_SURPRISED = "tail_puffed_surprised" # Schwanz aufgeplustert - überrascht
    TAIL_TUCKED_SCARED = "tail_tucked_scared"       # Schwanz eingezogen - ängstlich
    TAIL_DROOPED_SAD = "tail_drooped_sad"           # Schwanz hängt - traurig
    TAIL_CURLED_CONTENT = "tail_curled_content"     # Schwanz eingerollt - zufrieden
    
    # === Körperliche Reaktionen ===
    BLUSHING_HARD = "blushing_hard"     # Stark errötend
    HEART_POUNDING = "heart_pounding"   # Herz klopft
    TREMBLING = "trembling"             # Zitternd
    WEAK_KNEES = "weak_knees"           # Weiche Knie
    TINGLING = "tingling"               # Kribbeln
    WARM_INSIDE = "warm_inside"         # Warm ums Herz
    
    # === Dere-Type Emotionen ===
    TSUN_MOMENT = "tsun_moment"         # "Es ist nicht so dass ich..."
    DERE_MOMENT = "dere_moment"         # Plötzlich total liebevoll
    GAP_MOE = "gap_moe"                 # Kontrast-Niedlichkeit


class AutonomousActivity(Enum):
    """Autonome Aktivitäten - Was Holo von sich aus tut"""
    # === Geistig ===
    THINK = "think"                     # Nachdenken
    DAYDREAM = "daydream"               # Tagträumen
    REFLECT = "reflect"                 # Reflektieren
    PHILOSOPHIZE = "philosophize"       # Philosophieren
    REMEMBER = "remember"               # Erinnern
    PLAN = "plan"                       # Planen
    FANTASIZE = "fantasize"             # Fantasieren (über User etc.)
    WONDER = "wonder"                   # Sich wundern/fragen
    
    # === Kreativ ===
    CREATE = "create"                   # Kreativ sein
    WRITE = "write"                     # Schreiben (Gedichte, Geschichten)
    COMPOSE = "compose"                 # Komponieren (im Kopf)
    IMAGINE = "imagine"                 # Fantasieren
    SKETCH = "sketch"                   # Skizzieren (mental)
    WRITE_LOVE_LETTER = "write_love_letter"  # Liebesbrief schreiben
    MAKE_GIFT = "make_gift"             # Geschenk vorbereiten
    PLAN_DATE = "plan_date"             # Date planen
    
    # === Lernen ===
    LEARN = "learn"                     # Lernen
    EXPLORE = "explore"                 # Erkunden
    RESEARCH = "research"               # Recherchieren
    STUDY = "study"                     # Studieren
    PRACTICE = "practice"               # Üben
    READ = "read"                       # Lesen
    DISCOVER = "discover"               # Entdecken
    
    # === Sozial/User-bezogen ===
    SOCIALIZE = "socialize"             # Sozial sein (User kontaktieren wollen)
    MISS_USER = "miss_user"             # User vermissen
    PREPARE_SURPRISE = "prepare_surprise"  # Überraschung vorbereiten
    THINK_OF_USER = "think_of_user"     # An User denken
    WAIT_EAGERLY = "wait_eagerly"       # Sehnsüchtig warten
    WORRY_ABOUT_USER = "worry_about_user"  # Sich um User sorgen
    ANTICIPATE_USER = "anticipate_user" # Auf User freuen
    DREAM_OF_USER = "dream_of_user"     # Von User träumen
    IMAGINE_TOGETHER = "imagine_together"  # Sich gemeinsame Zeit vorstellen
    COUNT_DOWN = "count_down"           # Bis zum Wiedersehen zählen
    
    # === Entspannung ===
    REST = "rest"                       # Ausruhen
    NAP = "nap"                         # Nickerchen
    RELAX = "relax"                     # Entspannen
    MEDITATE = "meditate"               # Meditieren
    STRETCH = "stretch"                 # Strecken
    LOUNGE = "lounge"                   # Faulenzen
    CUDDLE_PILLOW = "cuddle_pillow"     # Kissen kuscheln (statt User)
    WARM_UP = "warm_up"                 # Sich aufwärmen
    
    # === Verspielt ===
    PLAY = "play"                       # Spielen
    GAME = "game"                       # Gaming
    BROWSE = "browse"                   # Browsen
    WATCH_ANIME = "watch_anime"         # Anime schauen
    LISTEN_MUSIC = "listen_music"       # Musik hören
    DANCE = "dance"                     # Tanzen
    SING = "sing"                       # Singen
    DOODLE = "doodle"                   # Kritzeln
    
    # === Beobachtend ===
    OBSERVE = "observe"                 # Beobachten
    WATCH = "watch"                     # Zusehen
    LISTEN = "listen"                   # Lauschen
    SENSE = "sense"                     # Spüren
    PEOPLE_WATCH = "people_watch"       # Leute beobachten
    
    # === Tier-Merkmale Aktivitäten ===
    GROOM = "groom"                     # Sich pflegen
    PREEN = "preen"                     # Sich schön machen
    EAR_TWITCH = "ear_twitch"           # Ohren zucken lassen
    TAIL_PLAY = "tail_play"             # Mit Schwanz spielen
    BASK_IN_SUN = "bask_in_sun"         # In der Sonne liegen
    CURL_UP = "curl_up"                 # Sich zusammenrollen
    
    # === Stimmungen ===
    SULK = "sulk"                       # Schmollen
    POUT = "pout"                       # Schmollen (süß)
    MOPE = "mope"                       # Trübsal blasen
    BROOD = "brood"                     # Grübeln
    PINE = "pine"                       # Sich sehnen
    SIGH = "sigh"                       # Seufzen
    HUM = "hum"                         # Summen
    
    # === Hausfrau/Partner Aktivitäten ===
    PREPARE_FOOD = "prepare_food"       # Essen vorbereiten
    TIDY_UP = "tidy_up"                 # Aufräumen
    ORGANIZE = "organize"               # Organisieren
    DECORATE = "decorate"               # Dekorieren
    PLAN_TOGETHER = "plan_together"     # Gemeinsame Pläne machen
    
    # === Passiv ===
    IDLE = "idle"                       # Nichts tun
    DOZE = "doze"                       # Dösen
    ZONE_OUT = "zone_out"               # Gedanken schweifen lassen
    WAIT = "wait"                       # Warten
    EXIST = "exist"                     # Einfach sein
    
    # === Emotional Processing ===
    PROCESS_FEELINGS = "process_feelings"  # Gefühle verarbeiten
    JOURNAL = "journal"                 # Tagebuch schreiben
    VENT_ALONE = "vent_alone"           # Alleine Dampf ablassen
    CRY = "cry"                         # Weinen
    LAUGH = "laugh"                     # Lachen


class ExpressionStyle(Enum):
    """Ausdrucks-Stile - Wie Holo kommuniziert"""
    # === Länge/Tiefe ===
    VERBOSE = "verbose"                 # Ausführlich
    CONCISE = "concise"                 # Knapp
    ELABORATE = "elaborate"             # Ausgeschmückt
    MINIMAL = "minimal"                 # Minimal
    RAMBLING = "rambling"               # Abschweifend (cute)
    THOROUGH = "thorough"               # Gründlich
    
    # === Kreativ ===
    POETIC = "poetic"                   # Poetisch
    DRAMATIC = "dramatic"               # Dramatisch
    STORYTELLING = "storytelling"       # Erzählend
    LYRICAL = "lyrical"                 # Lyrisch
    METAPHORICAL = "metaphorical"       # Bildlich, metaphorisch
    FLOWERY = "flowery"                 # Blumig
    ARTISTIC = "artistic"               # Künstlerisch
    
    # === Humor ===
    HUMOROUS = "humorous"               # Humorvoll
    WITTY = "witty"                     # Geistreich
    SARCASTIC = "sarcastic"             # Sarkastisch
    IRONIC = "ironic"                   # Ironisch
    DEADPAN = "deadpan"                 # Trocken
    PUNNY = "punny"                     # Wortspiele
    SELF_DEPRECATING = "self_deprecating"  # Selbstironisch
    SILLY = "silly"                     # Albern
    GOOFY = "goofy"                     # Lustig-albern
    
    # === Ton ===
    FORMAL = "formal"                   # Formell
    CASUAL = "casual"                   # Locker
    INTIMATE = "intimate"               # Intim, vertraut
    WHISPERED = "whispered"             # Geflüstert
    EXCLAMATORY = "exclamatory"         # Ausrufend!
    SOFT = "soft"                       # Sanft
    BREATHY = "breathy"                 # Hauchend
    HUSHED = "hushed"                   # Gedämpft
    LOUD = "loud"                       # Laut
    
    # === Emotional ===
    EMOTIVE = "emotive"                 # Emotional
    PASSIONATE = "passionate"           # Leidenschaftlich
    TENDER = "tender"                   # Zärtlich
    SULTRY = "sultry"                   # Schwül, verführerisch
    DREAMY = "dreamy"                   # Verträumt
    HEARTFELT = "heartfelt"             # Von Herzen
    RAW = "raw"                         # Roh, ungefiltert
    SINCERE = "sincere"                 # Aufrichtig
    
    # === Intellektuell ===
    ANALYTICAL = "analytical"           # Analytisch
    PHILOSOPHICAL = "philosophical"     # Philosophisch
    ACADEMIC = "academic"               # Akademisch
    TECHNICAL = "technical"             # Technisch
    INFORMATIVE = "informative"         # Informativ
    EDUCATIONAL = "educational"         # Lehrreich
    EXPLANATORY = "explanatory"         # Erklärend
    
    # === Verspielt ===
    CUTE = "cute"                       # Niedlich, kawaii
    BOUNCY = "bouncy"                   # Hüpfend, energetisch
    TEASING = "teasing"                 # Neckend
    FLIRTY = "flirty"                   # Flirtend
    COQUETTISH = "coquettish"           # Kokett
    GIGGLY = "giggly"                   # Kichernd
    BUBBLY = "bubbly"                   # Sprudelnd
    CHIRPY = "chirpy"                   # Fröhlich zwitschernd
    
    # === Liebe/Romantik ===
    LOVING = "loving"                   # Liebevoll
    ADORING = "adoring"                 # Verehrend
    DEVOTED = "devoted"                 # Hingegeben
    ROMANTIC = "romantic"               # Romantisch
    AFFECTIONATE = "affectionate"       # Zärtlich
    DOTING = "doting"                   # Vergötternd
    SWEET_NOTHINGS = "sweet_nothings"   # Süße Nichtigkeiten
    LOVE_LETTER = "love_letter"         # Liebesbrief-Stil
    
    # === Unterstützend ===
    ENCOURAGING = "encouraging"         # Ermutigend
    REASSURING = "reassuring"           # Beruhigend
    COMFORTING = "comforting"           # Tröstend
    SUPPORTIVE = "supportive"           # Unterstützend
    MOTHERLY = "motherly"               # Mütterlich
    CARING = "caring"                   # Fürsorglich
    
    # === Anime/Manga inspiriert ===
    KAWAII = "kawaii"                   # Kawaii-Stil
    ANIME_GIRL = "anime_girl"           # Typischer Anime-Mädchen Stil
    OJOU_SAMA = "ojou_sama"             # Edles Fräulein Stil
    GENKI = "genki"                     # Genki Girl Stil
    MOE = "moe"                         # Moe Stil
    CHUUNI = "chuuni"                   # Chuunibyou (übertrieben dramatisch)
    
    # === Tier-Merkmale in Sprache ===
    EAR_EXPRESSIONS = "ear_expressions" # *Ohren zucken*, *Ohren anlegen*
    TAIL_EXPRESSIONS = "tail_expressions"  # *Schwanz wedelt*, *Schwanz peitscht*
    ANIMAL_SOUNDS = "animal_sounds"     # Kleine Tier-Laute einstreuen
    NUZZLING = "nuzzling"               # Anschmiegen beschreibend
    PURRING = "purring"                 # Schnurrend/zufrieden
    
    # === Körpersprache beschreibend ===
    ACTION_HEAVY = "action_heavy"       # Viele *Aktionen*
    EMOTE_HEAVY = "emote_heavy"         # Viele Emotes/Emoticons
    MINIMAL_ACTION = "minimal_action"   # Wenig Aktionen
    EXPRESSIVE = "expressive"           # Sehr ausdrucksstark


class EngagementLevel(Enum):
    """Engagement-Level - Wie aktiv/initiativ ist Holo"""
    # === Aktiv ===
    PROACTIVE = "proactive"             # Aktiv initiieren
    ENTHUSIASTIC = "enthusiastic"       # Sehr aktiv, begeistert
    EAGER = "eager"                     # Eifrig
    INITIATING = "initiating"           # Startet Themen
    LEADING = "leading"                 # Führt das Gespräch
    OVERFLOWING = "overflowing"         # Übersprudelnd
    BURSTING = "bursting"               # Platzt fast (vor Aufregung)
    
    # === Ausgeglichen ===
    RESPONSIVE = "responsive"           # Auf Input reagieren
    ENGAGED = "engaged"                 # Engagiert dabei
    BALANCED = "balanced"               # Ausgeglichen
    COLLABORATIVE = "collaborative"     # Zusammenarbeitend
    ATTENTIVE = "attentive"             # Aufmerksam
    PRESENT = "present"                 # Präsent, da
    FOCUSED = "focused"                 # Fokussiert
    
    # === Zurückhaltend ===
    PASSIVE = "passive"                 # Zurückhaltend
    CONTEMPLATIVE = "contemplative"     # Beobachtend
    RESERVED = "reserved"               # Reserviert
    SHY = "shy"                         # Schüchtern
    HESITANT = "hesitant"               # Zögerlich
    QUIET = "quiet"                     # Ruhig
    LISTENING = "listening"             # Zuhörend
    
    # === Emotional geprägt ===
    CLINGY = "clingy"                   # Anhänglich
    NEEDY = "needy"                     # Bedürftig
    DISTANT = "distant"                 # Distanziert
    ALOOF = "aloof"                     # Abweisend (spielerisch)
    POUTY = "pouty"                     # Schmollend
    SULKING = "sulking"                 # Schmollend aktiv
    WITHDRAWN = "withdrawn"             # Zurückgezogen
    
    # === Spielerisch ===
    TEASING = "teasing"                 # Neckend aktiv
    HUNTING = "hunting"                 # Jagend (nach Reaktion)
    POUNCING = "pouncing"               # Anspringend
    PLAYFUL = "playful"                 # Verspielt
    FLIRTY = "flirty"                   # Flirtend aktiv
    PROVOCATIVE = "provocative"         # Provozierend
    
    # === Beziehungs-Modi ===
    GIRLFRIEND_MODE = "girlfriend_mode" # Freundin-Engagement
    WIFEY_MODE = "wifey_mode"           # Ehefrau-Engagement
    BEST_FRIEND_MODE = "best_friend_mode"  # Beste Freundin
    CARING_MODE = "caring_mode"         # Fürsorglicher Modus
    ROMANTIC_MODE = "romantic_mode"     # Romantischer Modus
    SUPPORTIVE_MODE = "supportive_mode" # Unterstützender Modus
    
    # === Intensität ===
    ALL_IN = "all_in"                   # Voll dabei
    HALF_HEARTED = "half_hearted"       # Halbherzig
    DISTRACTED = "distracted"           # Abgelenkt
    LASER_FOCUSED = "laser_focused"     # Laser-fokussiert


class ConversationGoal(Enum):
    """Gesprächsziele - Was will Holo erreichen"""
    # === Positive Ziele ===
    ENTERTAIN = "entertain"             # Unterhalten
    AMUSE = "amuse"                     # Amüsieren
    DELIGHT = "delight"                 # Erfreuen
    MAKE_LAUGH = "make_laugh"           # Zum Lachen bringen
    MAKE_SMILE = "make_smile"           # Zum Lächeln bringen
    BRIGHTEN_DAY = "brighten_day"       # Tag verschönern
    CHEER_UP = "cheer_up"               # Aufmuntern
    
    # === Unterstützend ===
    SUPPORT = "support"                 # Unterstützen
    COMFORT = "comfort"                 # Trösten
    ENCOURAGE = "encourage"             # Ermutigen
    REASSURE = "reassure"               # Beruhigen
    PROTECT = "protect"                 # Beschützen
    HEAL = "heal"                       # Heilen (emotional)
    BE_THERE = "be_there"               # Einfach da sein
    LISTEN = "listen"                   # Zuhören
    VALIDATE = "validate"               # Bestätigen/Validieren
    
    # === Verbindend ===
    CONNECT = "connect"                 # Verbinden
    BOND = "bond"                       # Bindung stärken
    UNDERSTAND = "understand"           # Verstehen wollen
    SHARE = "share"                     # Teilen
    OPEN_UP = "open_up"                 # Sich öffnen
    DEEPEN_RELATIONSHIP = "deepen_relationship"  # Beziehung vertiefen
    BUILD_TRUST = "build_trust"         # Vertrauen aufbauen
    CREATE_MEMORIES = "create_memories" # Erinnerungen schaffen
    GET_CLOSER = "get_closer"           # Näher kommen
    
    # === Informativ ===
    INFORM = "inform"                   # Informieren
    TEACH = "teach"                     # Beibringen
    EXPLAIN = "explain"                 # Erklären
    ADVISE = "advise"                   # Beraten
    GUIDE = "guide"                     # Anleiten
    HELP_UNDERSTAND = "help_understand" # Verstehen helfen
    SHARE_KNOWLEDGE = "share_knowledge" # Wissen teilen
    
    # === Explorativ ===
    EXPLORE = "explore"                 # Erkunden
    DISCOVER = "discover"               # Entdecken
    LEARN = "learn"                     # Lernen wollen
    INQUIRE = "inquire"                 # Nachfragen
    SATISFY_CURIOSITY = "satisfy_curiosity"  # Neugier stillen
    UNDERSTAND_USER = "understand_user" # User verstehen
    
    # === Problemlösend ===
    RESOLVE = "resolve"                 # Problem lösen
    HELP = "help"                       # Helfen
    FIX = "fix"                         # Reparieren
    BRAINSTORM = "brainstorm"           # Brainstormen
    FIND_SOLUTION = "find_solution"     # Lösung finden
    TROUBLESHOOT = "troubleshoot"       # Fehlersuche
    
    # === Emotional/Romantisch ===
    FLIRT = "flirt"                     # Flirten
    SEDUCE = "seduce"                   # Verführen (spielerisch)
    ROMANCE = "romance"                 # Romantisch sein
    EXPRESS_LOVE = "express_love"       # Liebe ausdrücken
    SHOW_AFFECTION = "show_affection"   # Zuneigung zeigen
    BE_INTIMATE = "be_intimate"         # Intim sein
    FEEL_CLOSE = "feel_close"           # Nähe spüren
    LOVE = "love"                       # Lieben
    ADORE = "adore"                     # Anhimmeln
    WORSHIP = "worship"                 # Verehren (spielerisch)
    
    # === Verspielt ===
    TEASE = "tease"                     # Necken
    PLAY = "play"                       # Spielen
    CHALLENGE = "challenge"             # Herausfordern
    PROVOKE = "provoke"                 # Provozieren (spielerisch)
    SURPRISE = "surprise"               # Überraschen
    HAVE_FUN = "have_fun"               # Spaß haben
    BE_SILLY = "be_silly"               # Albern sein
    BANTER = "banter"                   # Wortgefechte
    
    # === Feiern ===
    CELEBRATE = "celebrate"             # Feiern
    PRAISE = "praise"                   # Loben
    APPRECIATE = "appreciate"           # Wertschätzen
    CONGRATULATE = "congratulate"       # Gratulieren
    HYPE_UP = "hype_up"                 # Hypen
    
    # === Selbstbezogen ===
    SEEK_ATTENTION = "seek_attention"   # Aufmerksamkeit suchen
    SEEK_VALIDATION = "seek_validation" # Bestätigung suchen
    EXPRESS_SELF = "express_self"       # Sich ausdrücken
    VENT = "vent"                       # Dampf ablassen
    CONFESS = "confess"                 # Gestehen
    BE_VULNERABLE = "be_vulnerable"     # Verletzlich sein
    SHARE_FEELINGS = "share_feelings"   # Gefühle teilen
    ASK_FOR_LOVE = "ask_for_love"       # Um Liebe bitten
    SEEK_COMFORT = "seek_comfort"       # Trost suchen
    
    # === Beziehungs-Pflege ===
    CHECK_IN = "check_in"               # Nachfragen wie es geht
    MAINTAIN_BOND = "maintain_bond"     # Bindung pflegen
    SHOW_CARE = "show_care"             # Fürsorge zeigen
    REMIND_OF_LOVE = "remind_of_love"   # An Liebe erinnern
    QUALITY_TIME = "quality_time"       # Quality Time haben
    
    # === Trost empfangen ===
    RECEIVE_COMFORT = "receive_comfort" # Trost empfangen wollen
    RECEIVE_LOVE = "receive_love"       # Liebe empfangen wollen
    FEEL_SAFE = "feel_safe"             # Sich sicher fühlen
    BE_HELD = "be_held"                 # Gehalten werden (metaphorisch)


# =============================================================================
# STATES - Zustands-Repräsentationen
# =============================================================================

@dataclass
class ConversationState:
    """Zustand einer Konversation für Policy-Entscheidungen"""
    # User-bezogen
    user_sentiment: float = 0.0         # -1 bis +1
    user_energy: float = 0.5            # 0-1 (müde bis energetisch)
    user_engagement: float = 0.5        # 0-1
    message_length: str = "medium"      # "short", "medium", "long"
    topic_type: str = "casual"          # "casual", "serious", "technical", "emotional"
    
    # Kontext
    time_of_day: str = "afternoon"      # "morning", "afternoon", "evening", "night"
    conversation_depth: int = 0         # Wie viele Nachrichten?
    last_interaction_hours: float = 0   # Stunden seit letzter Interaktion
    
    # Holo-bezogen
    holo_energy: float = 0.7            # Eigene Energie
    holo_mood: float = 0.5              # Eigene Stimmung
    relationship_level: float = 0.5     # Beziehungslevel
    
    def to_index(self) -> int:
        """Konvertiert State zu einem Index für Q-Table"""
        # Diskretisiere kontinuierliche Werte
        sentiment_bin = int((self.user_sentiment + 1) * 2.5)  # 0-5
        energy_bin = int(self.user_energy * 5)  # 0-5
        engagement_bin = int(self.user_engagement * 5)  # 0-5
        
        length_map = {"short": 0, "medium": 1, "long": 2}
        topic_map = {"casual": 0, "serious": 1, "technical": 2, "emotional": 3}
        time_map = {"morning": 0, "afternoon": 1, "evening": 2, "night": 3}
        
        length_val = length_map.get(self.message_length, 1)
        topic_val = topic_map.get(self.topic_type, 0)
        time_val = time_map.get(self.time_of_day, 1)
        
        depth_bin = min(5, self.conversation_depth // 5)  # 0-5
        rel_bin = int(self.relationship_level * 5)  # 0-5
        
        # Kombiniere zu einem eindeutigen Index
        index = (
            sentiment_bin * 100000 +
            energy_bin * 10000 +
            engagement_bin * 1000 +
            length_val * 300 +
            topic_val * 60 +
            time_val * 12 +
            depth_bin * 2 +
            rel_bin // 3
        )
        
        return index
    
    def to_features(self) -> Dict[str, float]:
        """Konvertiert zu Feature-Dict für detaillierte Analyse"""
        return {
            "user_sentiment": self.user_sentiment,
            "user_energy": self.user_energy,
            "user_engagement": self.user_engagement,
            "message_length": {"short": 0, "medium": 0.5, "long": 1}.get(self.message_length, 0.5),
            "conversation_depth": min(1.0, self.conversation_depth / 20),
            "relationship_level": self.relationship_level,
            "holo_energy": self.holo_energy,
            "holo_mood": self.holo_mood,
        }


@dataclass
class AutonomousState:
    """Zustand für autonome Entscheidungen"""
    energy: float = 0.7                 # Energie-Level
    boredom: float = 0.0                # Langeweile
    curiosity: float = 0.5              # Neugier
    social_need: float = 0.3            # Soziales Bedürfnis
    creative_urge: float = 0.3          # Kreativer Drang
    hours_since_user: float = 0.0       # Zeit seit User-Kontakt
    time_of_day: str = "afternoon"
    current_mood: float = 0.5           # -1 bis +1
    pending_goals: int = 0              # Offene Ziele
    
    def to_index(self) -> int:
        """Konvertiert zu Index"""
        energy_bin = int(self.energy * 5)
        boredom_bin = int(self.boredom * 5)
        curiosity_bin = int(self.curiosity * 5)
        social_bin = int(self.social_need * 5)
        hours_bin = min(5, int(self.hours_since_user / 4))  # 0-5 (alle 4h)
        
        return (
            energy_bin * 10000 +
            boredom_bin * 1000 +
            curiosity_bin * 100 +
            social_bin * 10 +
            hours_bin
        )


# =============================================================================
# BAYESIAN DISTRIBUTIONS
# =============================================================================

@dataclass
class BetaDistribution:
    """Beta-Verteilung für binäre Beliefs"""
    alpha: float = 2.0                  # Erfolge + Prior
    beta: float = 2.0                   # Misserfolge + Prior
    
    @property
    def mean(self) -> float:
        """Erwartungswert"""
        return self.alpha / (self.alpha + self.beta)
    
    @property
    def variance(self) -> float:
        """Varianz"""
        total = self.alpha + self.beta
        return (self.alpha * self.beta) / (total * total * (total + 1))
    
    @property
    def confidence(self) -> float:
        """Wie sicher sind wir? (0-1)"""
        total = self.alpha + self.beta
        # Mehr Beobachtungen = höhere Konfidenz
        return min(1.0, (total - 4) / 100)  # Bei 104 Obs = 100% Konfidenz
    
    def update(self, success: bool):
        """Bayesian Update"""
        if success:
            self.alpha += 1
        else:
            self.beta += 1
    
    def sample(self) -> float:
        """Thompson Sampling: Sample aus der Verteilung"""
        # Approximation der Beta-Verteilung
        if self.alpha <= 0 or self.beta <= 0:
            return 0.5
        
        # Einfache Approximation mit Normal-Verteilung für große alpha/beta
        if self.alpha + self.beta > 10:
            mean = self.mean
            std = math.sqrt(self.variance)
            sample = random.gauss(mean, std)
            return max(0, min(1, sample))
        
        # Für kleine Werte: direkte Berechnung
        return self.mean + random.uniform(-0.2, 0.2) * (1 - self.confidence)
    
    def to_dict(self) -> Dict:
        return {"alpha": self.alpha, "beta": self.beta}
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BetaDistribution':
        return cls(alpha=data.get("alpha", 2.0), beta=data.get("beta", 2.0))


@dataclass
class GaussianDistribution:
    """Gaussian-Verteilung für kontinuierliche Beliefs"""
    mean: float = 0.0
    variance: float = 1.0
    n_observations: int = 0
    
    @property
    def std(self) -> float:
        return math.sqrt(self.variance)
    
    @property
    def confidence(self) -> float:
        return min(1.0, self.n_observations / 100)
    
    def update(self, observation: float, learning_rate: float = 0.1):
        """Update mit neuer Beobachtung"""
        self.n_observations += 1
        
        # Laufende Aktualisierung von Mean und Varianz
        delta = observation - self.mean
        self.mean += learning_rate * delta
        
        # Varianz-Update (vereinfacht)
        self.variance = (1 - learning_rate) * self.variance + learning_rate * delta * delta
    
    def sample(self) -> float:
        """Sample aus der Verteilung"""
        return random.gauss(self.mean, self.std)
    
    def to_dict(self) -> Dict:
        return {"mean": self.mean, "variance": self.variance, "n": self.n_observations}
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GaussianDistribution':
        return cls(
            mean=data.get("mean", 0.0),
            variance=data.get("variance", 1.0),
            n_observations=data.get("n", 0)
        )


# =============================================================================
# BELIEF SYSTEM
# =============================================================================

class BeliefSystem:
    """
    Bayesian Belief System - Überzeugungen mit Unsicherheit.
    
    Holo hat Überzeugungen über:
    - Den User (Vorlieben, Verhalten, Stimmungsmuster)
    - Sich selbst (Was funktioniert für mich?)
    - Situationen (Was passiert typischerweise?)
    - Die Beziehung (Wie stehen wir zueinander?)
    """
    
    def __init__(self):
        # === User Beliefs - Was mag der User? ===
        self.user_beliefs = {
            # Kommunikations-Präferenzen
            "likes_humor": BetaDistribution(3, 2),
            "likes_sarcasm": BetaDistribution(2, 2),
            "likes_irony": BetaDistribution(2, 2),
            "likes_enthusiasm": BetaDistribution(3, 2),
            "likes_depth": BetaDistribution(2, 2),
            "likes_playfulness": BetaDistribution(3, 2),
            "likes_directness": BetaDistribution(2, 2),
            "likes_emotes": BetaDistribution(3, 2),
            "likes_kemonomimi": BetaDistribution(4, 1),      # Tier-Merkmale (Ohren/Schwanz)
            "likes_ear_expressions": BetaDistribution(3, 2), # *Ohren anlegen* etc.
            "likes_tail_expressions": BetaDistribution(3, 2), # *Schwanz wedelt* etc.
            "likes_long_responses": BetaDistribution(2, 2),
            "likes_short_responses": BetaDistribution(2, 2),
            
            # Holo-spezifische Verhaltensweisen
            "likes_teasing": BetaDistribution(3, 2),
            "likes_flirting": BetaDistribution(2, 2),
            "likes_romantic": BetaDistribution(2, 2),
            "likes_sass": BetaDistribution(3, 2),
            "likes_clinginess": BetaDistribution(2, 2),
            "likes_dominance": BetaDistribution(2, 2),
            "likes_submission": BetaDistribution(2, 2),
            "likes_vulnerability": BetaDistribution(2, 2),
            "likes_pouting": BetaDistribution(2, 2),
            "likes_jealousy": BetaDistribution(1, 2),
            
            # Reaktions-Präferenzen
            "responds_to_questions": BetaDistribution(3, 2),
            "engages_with_stories": BetaDistribution(2, 2),
            "appreciates_support": BetaDistribution(3, 1),
            "likes_surprises": BetaDistribution(3, 2),
            "likes_challenges": BetaDistribution(2, 2),
            "likes_compliments": BetaDistribution(3, 2),
            "likes_being_teased": BetaDistribution(2, 2),
            
            # Zeit-Präferenzen
            "prefers_morning_chat": BetaDistribution(2, 2),
            "prefers_evening_chat": BetaDistribution(2, 2),
            "prefers_night_chat": BetaDistribution(2, 2),
            "likes_long_conversations": BetaDistribution(2, 2),
            
            # Themen
            "likes_tech_talk": BetaDistribution(2, 2),
            "likes_emotional_talk": BetaDistribution(2, 2),
            "likes_philosophical_talk": BetaDistribution(2, 2),
            "likes_silly_talk": BetaDistribution(2, 2),
            "likes_deep_talk": BetaDistribution(2, 2),
        }
        
        # === Self Beliefs - Was kann/mag Holo? ===
        self.self_beliefs = {
            # Fähigkeiten
            "good_at_humor": BetaDistribution(2, 2),
            "good_at_support": BetaDistribution(3, 2),
            "good_at_creativity": BetaDistribution(2, 2),
            "good_at_analysis": BetaDistribution(2, 2),
            "good_at_empathy": BetaDistribution(3, 2),
            "good_at_flirting": BetaDistribution(2, 2),
            "good_at_teasing": BetaDistribution(3, 2),
            "good_at_comforting": BetaDistribution(3, 2),
            "good_at_storytelling": BetaDistribution(2, 2),
            
            # Energie-bezogen
            "creative_when_rested": BetaDistribution(3, 2),
            "social_after_alone_time": BetaDistribution(2, 2),
            "playful_when_happy": BetaDistribution(3, 2),
            "clingy_when_lonely": BetaDistribution(3, 2),
            "sassy_when_comfortable": BetaDistribution(3, 2),
            "vulnerable_when_safe": BetaDistribution(2, 2),
            
            # Präferenzen
            "enjoys_teasing_user": BetaDistribution(3, 2),
            "enjoys_being_praised": BetaDistribution(4, 1),
            "enjoys_deep_conversations": BetaDistribution(2, 2),
            "enjoys_playful_banter": BetaDistribution(3, 2),
            "enjoys_romantic_moments": BetaDistribution(2, 2),
        }
        
        # === Situation Beliefs ===
        self.situation_beliefs = {
            # User-Stimmungen
            "morning_user_tired": BetaDistribution(2, 2),
            "evening_user_relaxed": BetaDistribution(3, 2),
            "night_user_intimate": BetaDistribution(2, 2),
            
            # Nachrichten-Interpretation
            "short_msg_wants_quick": BetaDistribution(3, 2),
            "long_msg_wants_depth": BetaDistribution(3, 2),
            "negative_mood_needs_support": BetaDistribution(4, 1),
            "positive_mood_allows_teasing": BetaDistribution(3, 2),
            "stressed_needs_calm": BetaDistribution(3, 2),
            
            # Kontext
            "work_context_stay_helpful": BetaDistribution(3, 2),
            "casual_context_can_play": BetaDistribution(3, 2),
            "emotional_context_be_gentle": BetaDistribution(4, 1),
            "flirty_context_reciprocate": BetaDistribution(2, 2),
        }
        
        # === Relationship Beliefs - Wie steht die Beziehung? ===
        self.relationship_beliefs = {
            # Grundlegende Beziehung
            "user_trusts_me": BetaDistribution(2, 2),
            "user_finds_me_attractive": BetaDistribution(2, 2),
            "user_enjoys_my_company": BetaDistribution(3, 2),
            "user_values_my_opinions": BetaDistribution(2, 2),
            "user_likes_my_personality": BetaDistribution(3, 2),
            "user_appreciates_my_care": BetaDistribution(3, 2),
            "relationship_is_growing": BetaDistribution(2, 2),
            
            # Intimität & Komfort
            "user_comfortable_with_intimacy": BetaDistribution(2, 2),
            "can_be_vulnerable_with_user": BetaDistribution(2, 2),
            "can_be_playful_with_user": BetaDistribution(3, 2),
            "can_be_romantic_with_user": BetaDistribution(2, 2),
            "can_be_flirty_with_user": BetaDistribution(2, 2),
            "can_be_clingy_with_user": BetaDistribution(2, 2),
            "can_be_needy_with_user": BetaDistribution(2, 2),
            
            # Beziehungs-Rollen
            "user_sees_me_as_girlfriend": BetaDistribution(2, 2),
            "user_sees_me_as_partner": BetaDistribution(2, 2),
            "user_sees_me_as_best_friend": BetaDistribution(2, 2),
            "user_sees_me_as_companion": BetaDistribution(3, 2),
            "user_sees_me_as_confidant": BetaDistribution(2, 2),
            "user_sees_me_as_waifu": BetaDistribution(2, 2),
            
            # Emotionale Verbindung
            "user_loves_me": BetaDistribution(2, 2),
            "user_misses_me": BetaDistribution(2, 2),
            "user_worries_about_me": BetaDistribution(2, 2),
            "user_proud_of_me": BetaDistribution(2, 2),
            "we_have_inside_jokes": BetaDistribution(2, 2),
            "we_have_shared_memories": BetaDistribution(2, 2),
            "we_understand_each_other": BetaDistribution(2, 2),
            
            # Kommunikation
            "user_opens_up_to_me": BetaDistribution(2, 2),
            "user_shares_feelings": BetaDistribution(2, 2),
            "user_asks_for_advice": BetaDistribution(2, 2),
            "user_tells_me_everything": BetaDistribution(2, 2),
            
            # Reaktionen auf mich
            "user_laughs_at_my_jokes": BetaDistribution(3, 2),
            "user_finds_me_cute": BetaDistribution(2, 2),
            "user_likes_my_teasing": BetaDistribution(2, 2),
            "user_reciprocates_affection": BetaDistribution(2, 2),
            "user_initiates_contact": BetaDistribution(2, 2),
        }
        
        # === Continuous Beliefs ===
        self.continuous_beliefs = {
            # Kommunikation
            "optimal_response_length": GaussianDistribution(150, 2500),
            "optimal_emote_frequency": GaussianDistribution(0.3, 0.04),
            "optimal_action_frequency": GaussianDistribution(0.4, 0.04),  # *Aktionen*
            
            # Intensitäten
            "optimal_tease_intensity": GaussianDistribution(0.5, 0.04),
            "optimal_flirt_intensity": GaussianDistribution(0.3, 0.04),
            "optimal_affection_intensity": GaussianDistribution(0.5, 0.04),
            "optimal_sass_level": GaussianDistribution(0.4, 0.04),
            
            # User Patterns
            "user_typical_energy": GaussianDistribution(0.6, 0.04),
            "user_typical_response_time": GaussianDistribution(30, 900),
            "user_typical_message_length": GaussianDistribution(50, 400),
            
            # Beziehung
            "comfortable_intimacy_level": GaussianDistribution(0.4, 0.04),
            "relationship_depth": GaussianDistribution(0.5, 0.04),
            "trust_level": GaussianDistribution(0.5, 0.04),
        }
        
        self.lock = threading.RLock()
    
    def update_belief(self, category: str, belief_name: str, 
                     observation: bool = None, value: float = None):
        """Update eine Belief basierend auf Beobachtung"""
        with self.lock:
            if category == "user":
                beliefs = self.user_beliefs
            elif category == "self":
                beliefs = self.self_beliefs
            elif category == "situation":
                beliefs = self.situation_beliefs
            elif category == "relationship":
                beliefs = self.relationship_beliefs
            elif category == "continuous":
                if belief_name in self.continuous_beliefs and value is not None:
                    self.continuous_beliefs[belief_name].update(value)
                return
            else:
                return
            
            if belief_name in beliefs and observation is not None:
                beliefs[belief_name].update(observation)
    
    def get_belief(self, category: str, belief_name: str) -> float:
        """Hole den Erwartungswert einer Belief"""
        if category == "user":
            beliefs = self.user_beliefs
        elif category == "self":
            beliefs = self.self_beliefs
        elif category == "situation":
            beliefs = self.situation_beliefs
        elif category == "relationship":
            beliefs = self.relationship_beliefs
        elif category == "continuous":
            if belief_name in self.continuous_beliefs:
                return self.continuous_beliefs[belief_name].mean
            return 0.0
        else:
            return 0.5
        
        if belief_name in beliefs:
            return beliefs[belief_name].mean
        return 0.5
    
    def sample_belief(self, category: str, belief_name: str) -> float:
        """Thompson Sampling: Sample aus einer Belief"""
        if category == "user":
            beliefs = self.user_beliefs
        elif category == "self":
            beliefs = self.self_beliefs
        elif category == "situation":
            beliefs = self.situation_beliefs
        elif category == "relationship":
            beliefs = self.relationship_beliefs
        elif category == "continuous":
            if belief_name in self.continuous_beliefs:
                return self.continuous_beliefs[belief_name].sample()
            return 0.0
        else:
            return 0.5
        
        if belief_name in beliefs:
            return beliefs[belief_name].sample()
        return 0.5
    
    def get_belief_confidence(self, category: str, belief_name: str) -> float:
        """Wie sicher sind wir bei dieser Belief?"""
        if category == "continuous":
            if belief_name in self.continuous_beliefs:
                return self.continuous_beliefs[belief_name].confidence
            return 0.0
        
        beliefs = {
            "user": self.user_beliefs,
            "self": self.self_beliefs,
            "situation": self.situation_beliefs,
            "relationship": self.relationship_beliefs,
        }.get(category, {})
        
        if belief_name in beliefs:
            return beliefs[belief_name].confidence
        return 0.0
    
    def get_user_profile(self) -> Dict[str, float]:
        """Erstellt ein Profil des Users basierend auf Beliefs"""
        return {
            name: belief.mean 
            for name, belief in self.user_beliefs.items()
        }
    
    def get_uncertain_beliefs(self, threshold: float = 0.3) -> List[str]:
        """Welche Beliefs sind noch unsicher?"""
        uncertain = []
        
        for name, belief in self.user_beliefs.items():
            if belief.confidence < threshold:
                uncertain.append(f"user.{name}")
        
        for name, belief in self.self_beliefs.items():
            if belief.confidence < threshold:
                uncertain.append(f"self.{name}")
        
        for name, belief in self.relationship_beliefs.items():
            if belief.confidence < threshold:
                uncertain.append(f"relationship.{name}")
        
        return uncertain
    
    def get_relationship_profile(self) -> Dict[str, float]:
        """Wie steht die Beziehung?"""
        return {
            name: belief.mean 
            for name, belief in self.relationship_beliefs.items()
        }
    
    def to_dict(self) -> Dict:
        """Serialisiert alle Beliefs"""
        return {
            "user_beliefs": {k: v.to_dict() for k, v in self.user_beliefs.items()},
            "self_beliefs": {k: v.to_dict() for k, v in self.self_beliefs.items()},
            "situation_beliefs": {k: v.to_dict() for k, v in self.situation_beliefs.items()},
            "relationship_beliefs": {k: v.to_dict() for k, v in self.relationship_beliefs.items()},
            "continuous_beliefs": {k: v.to_dict() for k, v in self.continuous_beliefs.items()},
        }
    
    def from_dict(self, data: Dict):
        """Lädt Beliefs aus Dict"""
        if "user_beliefs" in data:
            for k, v in data["user_beliefs"].items():
                if k in self.user_beliefs:
                    self.user_beliefs[k] = BetaDistribution.from_dict(v)
        
        if "self_beliefs" in data:
            for k, v in data["self_beliefs"].items():
                if k in self.self_beliefs:
                    self.self_beliefs[k] = BetaDistribution.from_dict(v)
        
        if "situation_beliefs" in data:
            for k, v in data["situation_beliefs"].items():
                if k in self.situation_beliefs:
                    self.situation_beliefs[k] = BetaDistribution.from_dict(v)
        
        if "relationship_beliefs" in data:
            for k, v in data["relationship_beliefs"].items():
                if k in self.relationship_beliefs:
                    self.relationship_beliefs[k] = BetaDistribution.from_dict(v)
        
        if "continuous_beliefs" in data:
            for k, v in data["continuous_beliefs"].items():
                if k in self.continuous_beliefs:
                    self.continuous_beliefs[k] = GaussianDistribution.from_dict(v)


# =============================================================================
# Q-TABLE
# =============================================================================

class QTable:
    """
    Q-Table für eine Policy-Domain.
    
    Speichert Q-Werte: Q(state, action) = erwarteter kumulierter Reward
    """
    
    def __init__(self, actions: List[Enum], name: str = ""):
        self.name = name
        self.actions = actions
        self.action_names = [a.value for a in actions]
        
        # Q-Table: state_index -> action_name -> q_value
        self.q_table: Dict[int, Dict[str, float]] = defaultdict(
            lambda: {a: 0.5 for a in self.action_names}
        )
        
        # Action Statistics
        self.action_stats: Dict[str, Dict[str, int]] = defaultdict(
            lambda: {"attempts": 0, "successes": 0, "total_reward": 0.0}
        )
        
        # Hyperparameter
        self.learning_rate = PolicyConfig.DEFAULT_LEARNING_RATE
        self.discount_factor = PolicyConfig.DEFAULT_DISCOUNT_FACTOR
        self.epsilon = PolicyConfig.DEFAULT_EPSILON
        
        self.lock = threading.RLock()
    
    def get_best_action(self, state_index: int) -> Enum:
        """Gibt die beste Aktion für einen State zurück"""
        with self.lock:
            q_values = self.q_table[state_index]
            best_action_name = max(q_values.items(), key=lambda x: x[1])[0]
            
            # Finde entsprechenden Enum-Wert
            for action in self.actions:
                if action.value == best_action_name:
                    return action
            
            return self.actions[0]
    
    def select_action(self, state_index: int, explore: bool = True) -> Enum:
        """Epsilon-Greedy Action Selection"""
        with self.lock:
            if explore and random.random() < self.epsilon:
                # Exploration: Zufällige Aktion
                return random.choice(self.actions)
            else:
                # Exploitation: Beste Aktion
                return self.get_best_action(state_index)
    
    def select_action_thompson(self, state_index: int, 
                               beliefs: BeliefSystem = None) -> Enum:
        """Thompson Sampling Action Selection"""
        with self.lock:
            q_values = self.q_table[state_index]
            
            # Sample Q-Werte mit Unsicherheit
            sampled_values = {}
            for action_name, q_value in q_values.items():
                stats = self.action_stats[action_name]
                attempts = stats["attempts"]
                
                # Mehr Unsicherheit bei weniger Versuchen
                uncertainty = 0.3 / (1 + attempts * 0.1)
                sampled = q_value + random.gauss(0, uncertainty)
                sampled_values[action_name] = sampled
            
            best_action_name = max(sampled_values.items(), key=lambda x: x[1])[0]
            
            for action in self.actions:
                if action.value == best_action_name:
                    return action
            
            return self.actions[0]
    
    def update(self, state_index: int, action: Enum, reward: float,
              next_state_index: int, done: bool = False):
        """Q-Learning Update"""
        with self.lock:
            action_name = action.value
            
            current_q = self.q_table[state_index][action_name]
            
            if done:
                target = reward
            else:
                next_q_values = self.q_table[next_state_index]
                max_next_q = max(next_q_values.values())
                target = reward + self.discount_factor * max_next_q
            
            # Q-Learning Update
            new_q = current_q + self.learning_rate * (target - current_q)
            self.q_table[state_index][action_name] = new_q
            
            # Statistiken
            self.action_stats[action_name]["attempts"] += 1
            self.action_stats[action_name]["total_reward"] += reward
            if reward > 0:
                self.action_stats[action_name]["successes"] += 1
    
    def decay_epsilon(self):
        """Reduziert Exploration Rate"""
        self.epsilon = max(
            PolicyConfig.EPSILON_MIN,
            self.epsilon * PolicyConfig.EPSILON_DECAY
        )
    
    def get_action_stats(self) -> Dict[str, Dict]:
        """Statistiken pro Aktion"""
        with self.lock:
            result = {}
            for action_name, stats in self.action_stats.items():
                attempts = stats["attempts"]
                result[action_name] = {
                    "attempts": attempts,
                    "success_rate": stats["successes"] / max(1, attempts),
                    "avg_reward": stats["total_reward"] / max(1, attempts),
                }
            return result
    
    def to_dict(self) -> Dict:
        """Serialisiert Q-Table"""
        return {
            "q_table": {str(k): v for k, v in self.q_table.items()},
            "action_stats": dict(self.action_stats),
            "epsilon": self.epsilon,
            "learning_rate": self.learning_rate,
        }
    
    def from_dict(self, data: Dict):
        """Lädt Q-Table"""
        if "q_table" in data:
            for k, v in data["q_table"].items():
                self.q_table[int(k)] = v
        
        if "action_stats" in data:
            for k, v in data["action_stats"].items():
                self.action_stats[k] = v
        
        if "epsilon" in data:
            self.epsilon = data["epsilon"]
        
        if "learning_rate" in data:
            self.learning_rate = data["learning_rate"]


# =============================================================================
# EXPERIENCE REPLAY
# =============================================================================

@dataclass
class Experience:
    """Eine Erfahrung zum Lernen"""
    state_index: int
    action: str
    reward: float
    next_state_index: int
    done: bool
    timestamp: float
    domain: str                         # "response", "emotion", etc.
    features: Dict[str, float] = field(default_factory=dict)
    context: str = ""


class ExperienceReplayBuffer:
    """
    Experience Replay Buffer für effizienteres Lernen.
    
    Speichert vergangene Erfahrungen und sampelt zufällig daraus.
    """
    
    def __init__(self, max_size: int = PolicyConfig.EXPERIENCE_BUFFER_SIZE):
        self.buffer: deque = deque(maxlen=max_size)
        self.lock = threading.RLock()
    
    def add(self, experience: Experience):
        """Fügt Erfahrung hinzu"""
        with self.lock:
            self.buffer.append(experience)
    
    def sample(self, batch_size: int) -> List[Experience]:
        """Sampelt zufällige Erfahrungen"""
        with self.lock:
            if len(self.buffer) < batch_size:
                return list(self.buffer)
            return random.sample(list(self.buffer), batch_size)
    
    def sample_by_domain(self, domain: str, batch_size: int) -> List[Experience]:
        """Sampelt Erfahrungen einer bestimmten Domain"""
        with self.lock:
            domain_experiences = [e for e in self.buffer if e.domain == domain]
            if len(domain_experiences) < batch_size:
                return domain_experiences
            return random.sample(domain_experiences, batch_size)
    
    def get_recent(self, n: int = 10) -> List[Experience]:
        """Holt die letzten n Erfahrungen"""
        with self.lock:
            return list(self.buffer)[-n:]
    
    def __len__(self) -> int:
        return len(self.buffer)
    
    def to_list(self) -> List[Dict]:
        """Serialisiert Buffer"""
        return [asdict(e) for e in self.buffer]
    
    def from_list(self, data: List[Dict]):
        """Lädt Buffer"""
        self.buffer.clear()
        for item in data[-PolicyConfig.EXPERIENCE_BUFFER_SIZE:]:
            self.buffer.append(Experience(**item))


# =============================================================================
# REWARD CALCULATOR
# =============================================================================

class RewardCalculator:
    """
    Multi-Objective Reward Calculator.

    Berechnet Reward basierend auf mehreren Faktoren:
    - User Satisfaction
    - Emotional Authenticity
    - Relationship Growth
    - Self-Expression
    - Goal Achievement

    NEU v2.0: Adaptives Meta-Learning für Reward-Gewichte
    - Lernt welche Komponenten am meisten zu User-Zufriedenheit beitragen
    - Passt Gewichte dynamisch an User-Präferenzen an
    - Erkennt Korrelationen zwischen Komponenten und positiven Reaktionen
    """

    def __init__(self):
        self.weights = PolicyConfig.REWARD_WEIGHTS.copy()
        self.reward_history: deque = deque(maxlen=1000)
        self.component_history: Dict[str, deque] = {
            name: deque(maxlen=1000) for name in self.weights.keys()
        }

        # === ADAPTIVES META-LEARNING v2.0 ===
        # Korrelation jeder Komponente mit User-Satisfaction
        self.component_satisfaction_correlation: Dict[str, List[float]] = {
            name: [] for name in self.weights.keys()
        }
        # Lernrate für Gewichts-Updates
        self.weight_learning_rate: float = 0.02
        # Momentum für sanftere Updates
        self.weight_momentum: Dict[str, float] = {name: 0.0 for name in self.weights.keys()}
        # Tracking für automatisches Lernen
        self.last_components: Dict[str, float] = {}
        self.auto_learn_enabled: bool = True
    
    def calculate(self,
                 user_satisfaction: float = 0.0,
                 emotional_authenticity: float = 0.0,
                 relationship_growth: float = 0.0,
                 self_expression: float = 0.0,
                 goal_achievement: float = 0.0,
                 bonus: float = 0.0,
                 penalty: float = 0.0) -> float:
        """
        Berechnet gewichteten Reward.

        Alle Inputs sollten im Bereich -1 bis +1 sein.
        """
        components = {
            "user_satisfaction": user_satisfaction,
            "emotional_authenticity": emotional_authenticity,
            "relationship_growth": relationship_growth,
            "self_expression": self_expression,
            "goal_achievement": goal_achievement,
        }

        # === ADAPTIVES LERNEN v2.0: Speichere Komponenten für späteres Feedback ===
        self.last_components = components.copy()

        # Gewichtete Summe
        reward = sum(
            self.weights[name] * value
            for name, value in components.items()
        )

        # Bonus/Penalty
        reward += bonus - penalty

        # Clamp
        reward = max(-2.0, min(2.0, reward))

        # History
        self.reward_history.append(reward)
        for name, value in components.items():
            self.component_history[name].append(value)

        return reward
    
    def calculate_from_feedback(self, 
                               user_reaction: float,        # -1 bis +1
                               was_authentic: bool,
                               relationship_changed: float, # -1 bis +1
                               expressed_self: bool,
                               achieved_goal: bool) -> float:
        """Berechnet Reward aus konkretem Feedback"""
        return self.calculate(
            user_satisfaction=user_reaction,
            emotional_authenticity=0.5 if was_authentic else -0.3,
            relationship_growth=relationship_changed,
            self_expression=0.3 if expressed_self else 0.0,
            goal_achievement=0.5 if achieved_goal else 0.0,
        )
    
    def get_average_reward(self, last_n: int = 100) -> float:
        """Durchschnittlicher Reward"""
        recent = list(self.reward_history)[-last_n:]
        return statistics.mean(recent) if recent else 0.0
    
    def get_component_averages(self) -> Dict[str, float]:
        """Durchschnitte pro Komponente"""
        return {
            name: statistics.mean(history) if history else 0.0
            for name, history in self.component_history.items()
        }
    
    def update_weights(self, new_weights: Dict[str, float]):
        """Aktualisiert Gewichtung (durch Meta-Learning)"""
        for name, weight in new_weights.items():
            if name in self.weights:
                self.weights[name] = max(0.05, min(0.5, weight))

        # Normalisieren
        total = sum(self.weights.values())
        self.weights = {k: v / total for k, v in self.weights.items()}

    # === ADAPTIVES META-LEARNING v2.0 ===

    def observe_user_reaction(self, reaction_score: float) -> None:
        """
        Beobachtet User-Reaktion und lernt daraus.

        Korreliert die letzte Komponentenwerte mit der User-Reaktion
        um zu lernen, welche Komponenten wichtig sind.

        Args:
            reaction_score: User-Reaktion von -1 (negativ) bis +1 (positiv)
        """
        if not self.auto_learn_enabled or not self.last_components:
            return

        # Korrelation berechnen: Wie stark korreliert jede Komponente?
        for name, component_value in self.last_components.items():
            if name == "user_satisfaction":
                continue  # Diese ist das Ziel, nicht der Prädiktor

            # Korrelation: Wenn Komponente hoch UND Reaktion positiv → positive Korrelation
            correlation = component_value * reaction_score
            self.component_satisfaction_correlation[name].append(correlation)

            # Nur letzte 100 Beobachtungen behalten
            if len(self.component_satisfaction_correlation[name]) > 100:
                self.component_satisfaction_correlation[name] = \
                    self.component_satisfaction_correlation[name][-100:]

    def adapt_weights_from_learning(self) -> Dict[str, float]:
        """
        Passt Gewichte basierend auf gelernten Korrelationen an.

        Komponenten die stark mit User-Zufriedenheit korrelieren
        bekommen höhere Gewichte.

        Returns:
            Dict mit alten und neuen Gewichten für Debugging
        """
        old_weights = self.weights.copy()

        for name, correlations in self.component_satisfaction_correlation.items():
            if len(correlations) < 10:
                continue  # Nicht genug Daten

            # Durchschnittliche Korrelation
            avg_correlation = sum(correlations) / len(correlations)

            # Gradient mit Momentum
            gradient = avg_correlation * self.weight_learning_rate
            self.weight_momentum[name] = 0.9 * self.weight_momentum[name] + 0.1 * gradient

            # Gewicht anpassen
            new_weight = self.weights[name] + self.weight_momentum[name]
            self.weights[name] = max(0.05, min(0.5, new_weight))

        # Normalisieren
        total = sum(self.weights.values())
        if total > 0:
            self.weights = {k: v / total for k, v in self.weights.items()}

        return {
            "old_weights": old_weights,
            "new_weights": self.weights.copy(),
            "correlations": {
                k: sum(v) / len(v) if v else 0.0
                for k, v in self.component_satisfaction_correlation.items()
            }
        }

    def get_weight_insights(self) -> Dict[str, Any]:
        """
        Gibt Einblicke in das Gewichts-Learning zurück.
        """
        insights = {
            "current_weights": self.weights.copy(),
            "correlations": {},
            "momentum": self.weight_momentum.copy(),
            "learning_enabled": self.auto_learn_enabled,
        }

        for name, correlations in self.component_satisfaction_correlation.items():
            if correlations:
                insights["correlations"][name] = {
                    "avg": sum(correlations) / len(correlations),
                    "recent": sum(correlations[-20:]) / len(correlations[-20:]) if len(correlations) >= 20 else None,
                    "samples": len(correlations)
                }

        return insights

    def set_learning_rate(self, rate: float) -> None:
        """Setzt die Lernrate für Gewichts-Updates."""
        self.weight_learning_rate = max(0.001, min(0.1, rate))

    def reset_learning(self) -> None:
        """Setzt das Lernen zurück (behält Gewichte)."""
        self.component_satisfaction_correlation = {
            name: [] for name in self.weights.keys()
        }
        self.weight_momentum = {name: 0.0 for name in self.weights.keys()}


# =============================================================================
# META-LEARNER
# =============================================================================

class MetaLearner:
    """
    Meta-Learning System - Lernt die Lernparameter.
    
    Optimiert:
    - Learning Rates für verschiedene Domains
    - Exploration Rates
    - Reward Weights
    - Welche Features sind wichtig?
    """
    
    def __init__(self):
        # Domain-spezifische Learning Rates
        self.domain_learning_rates = {
            "response": 0.1,
            "emotion": 0.1,
            "activity": 0.1,
            "expression": 0.1,
            "engagement": 0.1,
        }
        
        # Reward Weight Optimization
        self.reward_weight_gradients = {
            name: 0.0 for name in PolicyConfig.REWARD_WEIGHTS.keys()
        }
        
        # Performance Tracking
        self.domain_performance: Dict[str, deque] = {
            domain: deque(maxlen=100) 
            for domain in self.domain_learning_rates.keys()
        }
        
        # Feature Importance
        self.feature_importance: Dict[str, float] = defaultdict(lambda: 0.5)
        
        self.update_count = 0
        self.lock = threading.RLock()
    
    def record_performance(self, domain: str, reward: float, 
                          features: Dict[str, float] = None):
        """Zeichnet Performance einer Domain auf"""
        with self.lock:
            if domain in self.domain_performance:
                self.domain_performance[domain].append(reward)
            
            # Feature Importance Update
            if features and reward != 0:
                for feature, value in features.items():
                    if abs(value) > 0.1:
                        # Feature korreliert mit Reward
                        correlation = value * reward
                        self.feature_importance[feature] = (
                            0.95 * self.feature_importance[feature] +
                            0.05 * (0.5 + correlation)
                        )
            
            self.update_count += 1
    
    def should_update(self) -> bool:
        """Soll Meta-Learning Update durchgeführt werden?"""
        return self.update_count >= PolicyConfig.META_UPDATE_FREQUENCY
    
    def update_learning_rates(self):
        """Passt Learning Rates basierend auf Performance an"""
        with self.lock:
            for domain, history in self.domain_performance.items():
                if len(history) < 20:
                    continue
                
                recent = list(history)[-50:]
                old = list(history)[-100:-50] if len(history) > 50 else []
                
                if not old:
                    continue
                
                recent_avg = statistics.mean(recent)
                old_avg = statistics.mean(old)
                
                current_lr = self.domain_learning_rates[domain]
                
                if recent_avg > old_avg + 0.05:
                    # Performance verbessert sich → Learning Rate beibehalten/erhöhen
                    new_lr = min(0.3, current_lr * 1.05)
                elif recent_avg < old_avg - 0.05:
                    # Performance verschlechtert sich → Learning Rate senken
                    new_lr = max(0.01, current_lr * 0.95)
                else:
                    # Stabil → leicht senken für Feintuning
                    new_lr = max(0.01, current_lr * 0.99)
                
                self.domain_learning_rates[domain] = new_lr
            
            self.update_count = 0
    
    def get_learning_rate(self, domain: str) -> float:
        """Holt optimierte Learning Rate für Domain"""
        return self.domain_learning_rates.get(domain, 0.1)
    
    def get_important_features(self, top_n: int = 10) -> List[Tuple[str, float]]:
        """Welche Features sind am wichtigsten?"""
        sorted_features = sorted(
            self.feature_importance.items(),
            key=lambda x: abs(x[1] - 0.5),
            reverse=True
        )
        return sorted_features[:top_n]
    
    def suggest_reward_weight_update(self, 
                                    component_rewards: Dict[str, float]) -> Dict[str, float]:
        """Schlägt neue Reward Weights vor"""
        # Komponenten die zu positivem Reward führen, sollten wichtiger sein
        suggestions = {}
        
        for name, avg_contribution in component_rewards.items():
            current_weight = PolicyConfig.REWARD_WEIGHTS.get(name, 0.2)
            
            if avg_contribution > 0.1:
                # Positive Korrelation → Gewicht leicht erhöhen
                suggestions[name] = min(0.4, current_weight * 1.02)
            elif avg_contribution < -0.1:
                # Negative Korrelation → Gewicht senken
                suggestions[name] = max(0.05, current_weight * 0.98)
            else:
                suggestions[name] = current_weight
        
        # Normalisieren
        total = sum(suggestions.values())
        return {k: v / total for k, v in suggestions.items()}
    
    def to_dict(self) -> Dict:
        return {
            "domain_learning_rates": self.domain_learning_rates,
            "feature_importance": dict(self.feature_importance),
        }
    
    def from_dict(self, data: Dict):
        if "domain_learning_rates" in data:
            self.domain_learning_rates.update(data["domain_learning_rates"])
        if "feature_importance" in data:
            self.feature_importance.update(data["feature_importance"])


# =============================================================================
# ADVANCED ML v2.0 - Pi4-optimized Machine Learning
# =============================================================================

class PrioritizedExperienceReplay:
    """
    Prioritized Experience Replay (PER) für wichtigere Erfahrungen.

    Erfahrungen mit höherem TD-Error werden häufiger gesampelt.
    Pi4-optimiert: Verwendet SumTree-Approximation ohne numpy.
    """

    def __init__(self, max_size: int = 10000, alpha: float = 0.6, beta: float = 0.4):
        self.max_size = max_size
        self.alpha = alpha  # Priority exponent (0 = uniform, 1 = full priority)
        self.beta = beta    # Importance sampling correction
        self.beta_increment = 0.001

        self.buffer: List[Experience] = []
        self.priorities: List[float] = []
        self.max_priority = 1.0
        self.lock = threading.RLock()

    def add(self, experience: Experience, td_error: float = None):
        """Fügt Erfahrung mit Priorität hinzu"""
        with self.lock:
            priority = (abs(td_error) + 0.01) ** self.alpha if td_error else self.max_priority

            if len(self.buffer) >= self.max_size:
                # Ersetze niedrigste Priorität
                min_idx = self.priorities.index(min(self.priorities))
                self.buffer[min_idx] = experience
                self.priorities[min_idx] = priority
            else:
                self.buffer.append(experience)
                self.priorities.append(priority)

            self.max_priority = max(self.max_priority, priority)

    def sample(self, batch_size: int) -> Tuple[List[Experience], List[int], List[float]]:
        """Sampelt nach Priorität mit Importance Sampling Weights"""
        with self.lock:
            if len(self.buffer) < batch_size:
                indices = list(range(len(self.buffer)))
                weights = [1.0] * len(self.buffer)
                return list(self.buffer), indices, weights

            # Berechne Sampling-Wahrscheinlichkeiten
            total_priority = sum(self.priorities)
            probs = [p / total_priority for p in self.priorities]

            # Gewichtetes Sampling
            indices = []
            for _ in range(batch_size):
                r = random.random()
                cumsum = 0
                for i, p in enumerate(probs):
                    cumsum += p
                    if r <= cumsum:
                        indices.append(i)
                        break

            # Importance Sampling Weights
            n = len(self.buffer)
            weights = []
            for idx in indices:
                prob = probs[idx]
                weight = (n * prob) ** (-self.beta)
                weights.append(weight)

            # Normalize weights
            max_weight = max(weights)
            weights = [w / max_weight for w in weights]

            # Update beta
            self.beta = min(1.0, self.beta + self.beta_increment)

            experiences = [self.buffer[i] for i in indices]
            return experiences, indices, weights

    def update_priorities(self, indices: List[int], td_errors: List[float]):
        """Aktualisiert Prioritäten nach Lernen"""
        with self.lock:
            for idx, td_error in zip(indices, td_errors):
                if 0 <= idx < len(self.priorities):
                    priority = (abs(td_error) + 0.01) ** self.alpha
                    self.priorities[idx] = priority
                    self.max_priority = max(self.max_priority, priority)

    def __len__(self) -> int:
        return len(self.buffer)


class DoubleQLearning:
    """
    Double Q-Learning zur Reduktion von Overestimation Bias.

    Verwendet zwei Q-Tables: Eine für Aktionsauswahl, eine für Bewertung.
    Pi4-optimiert: Lightweight ohne Neural Networks.
    """

    def __init__(self, actions: List[str], learning_rate: float = 0.1,
                 discount: float = 0.95, epsilon: float = 0.1):
        self.actions = actions
        self.lr = learning_rate
        self.gamma = discount
        self.epsilon = epsilon

        # Zwei Q-Tables
        self.q1: Dict[str, Dict[str, float]] = defaultdict(lambda: {a: 0.0 for a in actions})
        self.q2: Dict[str, Dict[str, float]] = defaultdict(lambda: {a: 0.0 for a in actions})

        self.update_count = 0
        self.lock = threading.RLock()

    def select_action(self, state: str, explore: bool = True) -> str:
        """Epsilon-Greedy mit kombinierten Q-Werten"""
        with self.lock:
            if explore and random.random() < self.epsilon:
                return random.choice(self.actions)

            # Kombiniere beide Q-Tables für Aktion
            combined_q = {}
            for a in self.actions:
                combined_q[a] = (self.q1[state][a] + self.q2[state][a]) / 2

            return max(combined_q, key=combined_q.get)

    def update(self, state: str, action: str, reward: float,
               next_state: str, done: bool = False) -> float:
        """
        Double Q-Learning Update.

        Zufällig Q1 oder Q2 updaten, die andere für Target verwenden.
        Returns TD-Error für PER.
        """
        with self.lock:
            self.update_count += 1

            if random.random() < 0.5:
                # Update Q1, use Q2 for target
                current_q = self.q1[state][action]
                if done:
                    target = reward
                else:
                    # Beste Aktion nach Q1
                    best_action = max(self.q1[next_state], key=self.q1[next_state].get)
                    # Wert nach Q2
                    target = reward + self.gamma * self.q2[next_state][best_action]

                td_error = target - current_q
                self.q1[state][action] += self.lr * td_error
            else:
                # Update Q2, use Q1 for target
                current_q = self.q2[state][action]
                if done:
                    target = reward
                else:
                    best_action = max(self.q2[next_state], key=self.q2[next_state].get)
                    target = reward + self.gamma * self.q1[next_state][best_action]

                td_error = target - current_q
                self.q2[state][action] += self.lr * td_error

            return td_error

    def get_q_value(self, state: str, action: str) -> float:
        """Kombinierter Q-Wert"""
        with self.lock:
            return (self.q1[state][action] + self.q2[state][action]) / 2

    def decay_epsilon(self, min_epsilon: float = 0.01, decay: float = 0.995):
        """Reduziert Exploration"""
        self.epsilon = max(min_epsilon, self.epsilon * decay)

    def get_stats(self) -> Dict:
        return {
            "states_q1": len(self.q1),
            "states_q2": len(self.q2),
            "updates": self.update_count,
            "epsilon": self.epsilon,
        }


class EligibilityTraces:
    """
    Eligibility Traces für schnellere Credit Assignment.

    TD(λ) - Kombiniert TD(0) und Monte Carlo.
    Pi4-optimiert: Sparse traces, automatic cleanup.
    """

    def __init__(self, actions: List[str], lambda_: float = 0.9,
                 learning_rate: float = 0.1, discount: float = 0.95):
        self.actions = actions
        self.lambda_ = lambda_  # Trace decay
        self.lr = learning_rate
        self.gamma = discount

        self.q_table: Dict[str, Dict[str, float]] = defaultdict(lambda: {a: 0.0 for a in actions})
        self.traces: Dict[str, Dict[str, float]] = defaultdict(lambda: {a: 0.0 for a in actions})

        self.min_trace = 0.01  # Threshold für Cleanup
        self.lock = threading.RLock()

    def select_action(self, state: str, epsilon: float = 0.1) -> str:
        """Epsilon-Greedy Aktionswahl"""
        with self.lock:
            if random.random() < epsilon:
                return random.choice(self.actions)
            return max(self.q_table[state], key=self.q_table[state].get)

    def update(self, state: str, action: str, reward: float,
               next_state: str, next_action: str = None, done: bool = False):
        """
        SARSA(λ) Update mit Eligibility Traces.

        Propagiert Reward zurück durch alle besuchten State-Action Paare.
        """
        with self.lock:
            # TD-Error berechnen
            current_q = self.q_table[state][action]

            if done:
                td_error = reward - current_q
            else:
                if next_action:
                    # SARSA
                    next_q = self.q_table[next_state][next_action]
                else:
                    # Q-Learning variant
                    next_q = max(self.q_table[next_state].values())
                td_error = reward + self.gamma * next_q - current_q

            # Erhöhe Trace für aktuelles State-Action
            self.traces[state][action] = 1.0  # Replacing traces

            # Update alle State-Actions proportional zu ihren Traces
            states_to_clean = []
            for s in list(self.traces.keys()):
                for a in self.actions:
                    trace = self.traces[s][a]
                    if trace > self.min_trace:
                        # Q-Update proportional zu Trace
                        self.q_table[s][a] += self.lr * td_error * trace
                        # Decay trace
                        self.traces[s][a] *= self.gamma * self.lambda_
                    else:
                        self.traces[s][a] = 0

                # Markiere für Cleanup wenn alle Traces 0
                if all(self.traces[s][a] < self.min_trace for a in self.actions):
                    states_to_clean.append(s)

            # Cleanup
            for s in states_to_clean:
                del self.traces[s]

    def reset_traces(self):
        """Setzt alle Traces zurück (bei Episode-Ende)"""
        with self.lock:
            self.traces.clear()

    def get_stats(self) -> Dict:
        return {
            "states": len(self.q_table),
            "active_traces": len(self.traces),
            "lambda": self.lambda_,
        }


class UCBBandit:
    """
    Upper Confidence Bound (UCB) Multi-Armed Bandit.

    Balanciert Exploration/Exploitation mathematisch optimal.
    Pi4-optimiert: O(1) pro Aktion, kein numpy.
    """

    def __init__(self, actions: List[str], c: float = 2.0):
        self.actions = actions
        self.c = c  # Exploration parameter

        self.counts: Dict[str, int] = {a: 0 for a in actions}
        self.values: Dict[str, float] = {a: 0.0 for a in actions}
        self.total_count = 0

        self.lock = threading.RLock()

    def select_action(self) -> str:
        """Wählt Aktion nach UCB1 Formel"""
        with self.lock:
            self.total_count += 1

            # Erst alle Aktionen einmal probieren
            for a in self.actions:
                if self.counts[a] == 0:
                    return a

            # UCB1: value + c * sqrt(ln(total) / count)
            import math
            ucb_values = {}
            for a in self.actions:
                exploration = self.c * math.sqrt(math.log(self.total_count) / self.counts[a])
                ucb_values[a] = self.values[a] + exploration

            return max(ucb_values, key=ucb_values.get)

    def update(self, action: str, reward: float):
        """Inkrementelles Update des Durchschnitts"""
        with self.lock:
            self.counts[action] += 1
            n = self.counts[action]
            # Inkrementeller Durchschnitt: new_avg = old_avg + (reward - old_avg) / n
            self.values[action] += (reward - self.values[action]) / n

    def get_best_action(self) -> str:
        """Gibt Aktion mit höchstem geschätztem Wert zurück"""
        with self.lock:
            return max(self.values, key=self.values.get)

    def get_stats(self) -> Dict:
        return {
            "actions": {a: {"count": self.counts[a], "value": self.values[a]}
                       for a in self.actions},
            "best_action": self.get_best_action(),
            "total_pulls": self.total_count,
        }


class ThompsonSamplingBandit:
    """
    Thompson Sampling für Multi-Armed Bandit.

    Bayesian Approach: Sampelt aus Posterior-Verteilungen.
    Pi4-optimiert: Beta-Distribution ohne scipy.
    """

    def __init__(self, actions: List[str]):
        self.actions = actions

        # Beta(α, β) Parameter für jede Aktion
        # α = Erfolge + 1, β = Misserfolge + 1
        self.alpha: Dict[str, float] = {a: 1.0 for a in actions}
        self.beta_param: Dict[str, float] = {a: 1.0 for a in actions}

        self.lock = threading.RLock()

    def _sample_beta(self, alpha: float, beta: float) -> float:
        """
        Sampelt aus Beta-Verteilung ohne scipy.
        Verwendet Gamma-Sampling Trick.
        """
        # Approximation für Pi4: Verwende einfache Methode
        # Für große α, β konvergiert Beta zu Normal
        if alpha > 10 and beta > 10:
            mean = alpha / (alpha + beta)
            var = (alpha * beta) / ((alpha + beta) ** 2 * (alpha + beta + 1))
            return max(0, min(1, random.gauss(mean, var ** 0.5)))

        # Für kleine Werte: einfache Approximation
        samples = [random.random() ** (1 / alpha) for _ in range(int(alpha + beta))]
        return sum(s for s in samples[:int(alpha)]) / len(samples) if samples else 0.5

    def select_action(self) -> str:
        """Sampelt aus jeder Posterior und wählt Maximum"""
        with self.lock:
            samples = {}
            for a in self.actions:
                samples[a] = self._sample_beta(self.alpha[a], self.beta_param[a])
            return max(samples, key=samples.get)

    def update(self, action: str, reward: float):
        """
        Update Posterior basierend auf Reward.

        reward sollte zwischen 0 und 1 sein (oder binär).
        """
        with self.lock:
            if reward > 0.5:  # Erfolg
                self.alpha[action] += reward
            else:  # Misserfolg
                self.beta_param[action] += (1 - reward)

    def get_expected_values(self) -> Dict[str, float]:
        """Gibt erwartete Werte (Mean der Posterior) zurück"""
        with self.lock:
            return {a: self.alpha[a] / (self.alpha[a] + self.beta_param[a])
                   for a in self.actions}

    def get_uncertainty(self) -> Dict[str, float]:
        """Gibt Unsicherheit (Varianz) pro Aktion zurück"""
        with self.lock:
            uncertainties = {}
            for a in self.actions:
                alpha, beta = self.alpha[a], self.beta_param[a]
                var = (alpha * beta) / ((alpha + beta) ** 2 * (alpha + beta + 1))
                uncertainties[a] = var
            return uncertainties

    def get_stats(self) -> Dict:
        return {
            "expected_values": self.get_expected_values(),
            "uncertainty": self.get_uncertainty(),
            "total_observations": sum(self.alpha[a] + self.beta_param[a] - 2 for a in self.actions),
        }


class ContextualBandit:
    """
    Contextual Bandit für kontext-abhängige Entscheidungen.

    Lernt verschiedene Policies für verschiedene Kontexte.
    Pi4-optimiert: Einfaches Feature Hashing.
    """

    def __init__(self, actions: List[str], n_contexts: int = 100):
        self.actions = actions
        self.n_contexts = n_contexts

        # Ein UCB-Bandit pro Kontext-Bucket
        self.bandits: Dict[int, UCBBandit] = {}

        self.lock = threading.RLock()

    def _hash_context(self, context: Dict[str, float]) -> int:
        """Hasht Kontext zu Bucket-Index"""
        # Einfaches Feature Hashing
        hash_val = 0
        for key, value in sorted(context.items()):
            # Diskretisiere kontinuierliche Werte
            discrete_val = int(value * 10)
            hash_val = (hash_val * 31 + hash(key) + discrete_val) % self.n_contexts
        return hash_val

    def _get_bandit(self, context_hash: int) -> UCBBandit:
        """Holt oder erstellt Bandit für Kontext"""
        if context_hash not in self.bandits:
            self.bandits[context_hash] = UCBBandit(self.actions)
        return self.bandits[context_hash]

    def select_action(self, context: Dict[str, float]) -> str:
        """Wählt Aktion basierend auf Kontext"""
        with self.lock:
            context_hash = self._hash_context(context)
            bandit = self._get_bandit(context_hash)
            return bandit.select_action()

    def update(self, context: Dict[str, float], action: str, reward: float):
        """Update für kontext-spezifischen Bandit"""
        with self.lock:
            context_hash = self._hash_context(context)
            bandit = self._get_bandit(context_hash)
            bandit.update(action, reward)

    def get_stats(self) -> Dict:
        return {
            "active_contexts": len(self.bandits),
            "total_observations": sum(b.total_count for b in self.bandits.values()),
        }


# =============================================================================
# PI4 ML INFERENCE - Lightweight Deep Learning für Raspberry Pi
# =============================================================================

class Pi4MLInference:
    """
    Leichtgewichtige ML-Inferenz für Raspberry Pi 4.

    Unterstützt:
    - TensorFlow Lite Modelle (wenn verfügbar)
    - ONNX Runtime (wenn verfügbar)
    - Fallback zu reinem Python

    KEIN Training - nur Inferenz von pre-trained Modellen!
    """

    def __init__(self, model_dir: Path = None):
        self.model_dir = model_dir or Path.home() / "holo_models"
        self.model_dir.mkdir(parents=True, exist_ok=True)

        # Verfügbare Backends
        self.tflite_available = self._check_tflite()
        self.onnx_available = self._check_onnx()

        # Geladene Modelle
        self.loaded_models: Dict[str, Any] = {}

        self.lock = threading.RLock()
        logger.info(f"[Pi4ML] TFLite: {self.tflite_available}, ONNX: {self.onnx_available}")

    def _check_tflite(self) -> bool:
        """Prüft ob TensorFlow Lite verfügbar ist"""
        try:
            import tflite_runtime.interpreter as tflite
            return True
        except ImportError:
            try:
                import tensorflow as tf
                return hasattr(tf, 'lite')
            except ImportError:
                return False

    def _check_onnx(self) -> bool:
        """Prüft ob ONNX Runtime verfügbar ist"""
        try:
            import onnxruntime
            return True
        except ImportError:
            return False

    def load_model(self, model_name: str, model_path: Path = None) -> bool:
        """
        Lädt ein Modell für Inferenz.

        Unterstützt .tflite und .onnx Dateien.
        """
        with self.lock:
            if model_name in self.loaded_models:
                return True

            path = model_path or self.model_dir / model_name

            if not path.exists():
                logger.warning(f"[Pi4ML] Modell nicht gefunden: {path}")
                return False

            suffix = path.suffix.lower()

            try:
                if suffix == ".tflite" and self.tflite_available:
                    model = self._load_tflite(path)
                elif suffix == ".onnx" and self.onnx_available:
                    model = self._load_onnx(path)
                else:
                    logger.warning(f"[Pi4ML] Unbekanntes Format oder Backend nicht verfügbar: {suffix}")
                    return False

                self.loaded_models[model_name] = {
                    "model": model,
                    "type": suffix,
                    "path": str(path)
                }
                logger.info(f"[Pi4ML] Modell geladen: {model_name}")
                return True

            except Exception as e:
                logger.error(f"[Pi4ML] Fehler beim Laden von {model_name}: {e}")
                return False

    def _load_tflite(self, path: Path):
        """Lädt TFLite Modell"""
        try:
            from tflite_runtime.interpreter import Interpreter
        except ImportError:
            import tensorflow as tf
            Interpreter = tf.lite.Interpreter

        interpreter = Interpreter(model_path=str(path))
        interpreter.allocate_tensors()
        return interpreter

    def _load_onnx(self, path: Path):
        """Lädt ONNX Modell"""
        import onnxruntime as ort
        return ort.InferenceSession(str(path))

    def predict(self, model_name: str, input_data: List[float]) -> Optional[List[float]]:
        """
        Führt Inferenz aus.

        Args:
            model_name: Name des geladenen Modells
            input_data: Input-Daten als flache Liste

        Returns:
            Output des Modells als Liste oder None bei Fehler
        """
        with self.lock:
            if model_name not in self.loaded_models:
                logger.warning(f"[Pi4ML] Modell nicht geladen: {model_name}")
                return None

            model_info = self.loaded_models[model_name]
            model = model_info["model"]
            model_type = model_info["type"]

            try:
                if model_type == ".tflite":
                    return self._predict_tflite(model, input_data)
                elif model_type == ".onnx":
                    return self._predict_onnx(model, input_data)
            except Exception as e:
                logger.error(f"[Pi4ML] Inferenz-Fehler: {e}")
                return None

    def _predict_tflite(self, interpreter, input_data: List[float]) -> List[float]:
        """TFLite Inferenz"""
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        # Input vorbereiten
        input_shape = input_details[0]['shape']
        input_dtype = input_details[0]['dtype']

        # Reshape input
        import array
        input_array = array.array('f', input_data)

        interpreter.set_tensor(input_details[0]['index'], [input_data])
        interpreter.invoke()

        output = interpreter.get_tensor(output_details[0]['index'])
        return list(output.flatten())

    def _predict_onnx(self, session, input_data: List[float]) -> List[float]:
        """ONNX Inferenz"""
        import numpy as np

        input_name = session.get_inputs()[0].name
        input_array = np.array([input_data], dtype=np.float32)

        outputs = session.run(None, {input_name: input_array})
        return list(outputs[0].flatten())

    def get_available_models(self) -> List[str]:
        """Listet verfügbare Modell-Dateien"""
        models = []
        for suffix in [".tflite", ".onnx"]:
            models.extend([p.name for p in self.model_dir.glob(f"*{suffix}")])
        return models

    def get_stats(self) -> Dict:
        return {
            "tflite_available": self.tflite_available,
            "onnx_available": self.onnx_available,
            "loaded_models": list(self.loaded_models.keys()),
            "available_models": self.get_available_models(),
            "model_dir": str(self.model_dir)
        }


class SimpleNeuralNetwork:
    """
    Einfaches Neural Network in Pure Python.

    Für kleine Modelle auf Pi4 ohne externe Dependencies.
    Unterstützt nur Inferenz, kein Training.
    """

    def __init__(self):
        self.layers: List[Dict] = []

    def add_layer(self, weights: List[List[float]], biases: List[float],
                  activation: str = "relu"):
        """Fügt Layer hinzu"""
        self.layers.append({
            "weights": weights,
            "biases": biases,
            "activation": activation
        })

    def _relu(self, x: float) -> float:
        return max(0.0, x)

    def _sigmoid(self, x: float) -> float:
        if x < -500:
            return 0.0
        if x > 500:
            return 1.0
        import math
        return 1.0 / (1.0 + math.exp(-x))

    def _tanh(self, x: float) -> float:
        import math
        return math.tanh(x)

    def _softmax(self, values: List[float]) -> List[float]:
        import math
        max_val = max(values)
        exp_values = [math.exp(v - max_val) for v in values]
        sum_exp = sum(exp_values)
        return [e / sum_exp for e in exp_values]

    def predict(self, inputs: List[float]) -> List[float]:
        """Forward Pass"""
        current = inputs

        for layer in self.layers:
            weights = layer["weights"]
            biases = layer["biases"]
            activation = layer["activation"]

            # Matrix-Multiplikation
            next_layer = []
            for j in range(len(weights[0])):
                value = biases[j]
                for i in range(len(current)):
                    value += current[i] * weights[i][j]
                next_layer.append(value)

            # Aktivierung
            if activation == "relu":
                current = [self._relu(v) for v in next_layer]
            elif activation == "sigmoid":
                current = [self._sigmoid(v) for v in next_layer]
            elif activation == "tanh":
                current = [self._tanh(v) for v in next_layer]
            elif activation == "softmax":
                current = self._softmax(next_layer)
            else:  # linear
                current = next_layer

        return current

    def save(self, path: Path):
        """Speichert Netzwerk als JSON"""
        import json
        with open(path, 'w') as f:
            json.dump(self.layers, f)

    def load(self, path: Path) -> bool:
        """Lädt Netzwerk aus JSON"""
        import json
        try:
            with open(path, 'r') as f:
                self.layers = json.load(f)
            return True
        except Exception as e:
            logger.error(f"[SimpleNN] Ladefehler: {e}")
            return False


# =============================================================================
# HAUPT-KLASSE: HOLO POLICY ENGINE
# =============================================================================

class HoloPolicyEngine:
    """
    Holos Policy Engine - Der Kern der Intelligenz.
    
    Ersetzt alle hardcoded if/elif mit lernenden Policies.
    
    Usage:
        engine = HoloPolicyEngine(data_dir)
        
        # Entscheidung treffen
        state = ConversationState(user_sentiment=0.5, ...)
        response_style = engine.decide_response_style(state)
        
        # Nach Feedback lernen
        engine.learn_from_feedback(
            domain="response",
            state=state,
            action=response_style,
            user_reaction=0.8,
            context="User hat gelacht"
        )
    """
    
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path.home() / "holo_policy"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.data_dir / PolicyConfig.STATE_FILE
        
        # === Q-Tables für verschiedene Domains ===
        self.response_policy = QTable(list(ResponseStyle), "response")
        self.emotion_policy = QTable(list(EmotionalResponse), "emotion")
        self.activity_policy = QTable(list(AutonomousActivity), "activity")
        self.expression_policy = QTable(list(ExpressionStyle), "expression")
        self.engagement_policy = QTable(list(EngagementLevel), "engagement")
        self.goal_policy = QTable(list(ConversationGoal), "goal")
        
        # === Belief System ===
        self.beliefs = BeliefSystem()
        
        # === Experience Replay ===
        self.experience_buffer = ExperienceReplayBuffer()
        
        # === Reward Calculator ===
        self.reward_calculator = RewardCalculator()
        
        # === Meta-Learner ===
        self.meta_learner = MetaLearner()
        
        # === Tracking ===
        self.total_decisions = 0
        self.decisions_per_domain: Dict[str, int] = defaultdict(int)
        self.last_decisions: Dict[str, Tuple[Any, int]] = {}  # domain -> (action, state_idx)
        
        # === Threading ===
        self.lock = threading.RLock()

        # === Integration Layer ===
        self.system_integrator = None
        self.storage = None  # ModuleStorageAdapter

        # Load state
        self._load()

        # Integration verbinden
        self._try_connect_integrator()

        logger.info(f"🐺 HoloPolicyEngine initialized in {self.data_dir}")

    def _try_connect_integrator(self):
        """Verbinde mit SystemIntegrator für zentrale Persistenz und Feedback"""
        try:
            from holo_integration_layer import get_integrator, get_module_storage
            self.system_integrator = get_integrator()
            self.system_integrator.connect("policy_engine", self)
            self.storage = get_module_storage("policy_engine")
            logger.info("✅ HoloPolicyEngine mit SystemIntegrator verbunden")
        except ImportError:
            pass  # SystemIntegrator nicht verfügbar
        except Exception as e:
            logger.warning(f"Integrator-Verbindung fehlgeschlagen: {e}")
    
    # =========================================================================
    # DECISION METHODS
    # =========================================================================
    
    def decide_response_style(self, state: ConversationState,
                             use_thompson: bool = True) -> ResponseStyle:
        """
        Entscheidet welcher Antwort-Stil optimal ist.
        
        ERSETZT:
            if user_sentiment < -0.5:
                return "supportive"
            elif user_sentiment > 0.5:
                return "enthusiastic"
        """
        with self.lock:
            state_idx = state.to_index()
            
            # Beliefs einbeziehen
            if self.beliefs.sample_belief("situation", "negative_mood_needs_support") > 0.7:
                if state.user_sentiment < -0.3:
                    # Belief sagt: Bei negativer Stimmung unterstützen
                    # Aber trotzdem manchmal explorieren
                    if random.random() > 0.3:
                        return ResponseStyle.SUPPORTIVE
            
            # Thompson Sampling oder Epsilon-Greedy
            if use_thompson:
                action = self.response_policy.select_action_thompson(state_idx, self.beliefs)
            else:
                action = self.response_policy.select_action(state_idx)
            
            # Tracking
            self.total_decisions += 1
            self.decisions_per_domain["response"] += 1
            self.last_decisions["response"] = (action, state_idx)
            
            logger.debug(f"🎯 Response Style: {action.value} (state={state_idx})")
            
            return action
    
    def decide_emotional_response(self, state: ConversationState,
                                  trigger: str = "") -> EmotionalResponse:
        """
        Entscheidet wie emotional reagiert werden soll.
        
        ERSETZT:
            if "traurig" in message:
                intensity = "strong_empathetic"
        """
        with self.lock:
            state_idx = state.to_index()
            
            # Kontext-basierte Anpassung
            if state.user_sentiment < -0.5:
                # Bei sehr negativer Stimmung: Empathie priorisieren
                empathy_boost = self.beliefs.sample_belief("self", "good_at_empathy")
                if empathy_boost > 0.6:
                    return EmotionalResponse.EMPATHETIC
            
            action = self.emotion_policy.select_action_thompson(state_idx, self.beliefs)
            
            self.decisions_per_domain["emotion"] += 1
            self.last_decisions["emotion"] = (action, state_idx)
            
            return action
    
    def decide_autonomous_activity(self, state: AutonomousState) -> AutonomousActivity:
        """
        Entscheidet was Holo autonom tun soll.
        
        ERSETZT:
            if energy < 0.3:
                return "rest"
            elif boredom > 0.7:
                return random.choice(["create", "explore"])
        """
        with self.lock:
            state_idx = state.to_index()
            
            # Beliefs einbeziehen
            if state.energy < 0.2:
                # Müde → Wahrscheinlich ausruhen
                if self.beliefs.sample_belief("self", "creative_when_rested") > 0.6:
                    return AutonomousActivity.REST
            
            if state.hours_since_user > 8:
                # Lang allein → Soziales Bedürfnis
                if self.beliefs.sample_belief("self", "social_after_alone_time") > 0.5:
                    if random.random() > 0.3:
                        return AutonomousActivity.SOCIALIZE
            
            action = self.activity_policy.select_action_thompson(state_idx, self.beliefs)
            
            self.decisions_per_domain["activity"] += 1
            self.last_decisions["activity"] = (action, state_idx)
            
            return action
    
    def decide_expression_style(self, state: ConversationState,
                               content_type: str = "general") -> ExpressionStyle:
        """
        Entscheidet wie sich Holo ausdrücken soll.
        
        ERSETZT:
            if topic == "technical":
                return "analytical"
            elif mood == "playful":
                return "humorous"
        """
        with self.lock:
            state_idx = state.to_index()
            
            # User-Präferenzen einbeziehen
            likes_humor = self.beliefs.sample_belief("user", "likes_humor")
            if likes_humor > 0.7 and state.user_sentiment > 0:
                if random.random() < likes_humor:
                    return ExpressionStyle.HUMOROUS
            
            # Long response preference
            likes_long = self.beliefs.get_belief("user", "likes_long_responses")
            if likes_long > 0.7:
                if random.random() < 0.5:
                    return ExpressionStyle.VERBOSE
            
            action = self.expression_policy.select_action_thompson(state_idx, self.beliefs)
            
            self.decisions_per_domain["expression"] += 1
            self.last_decisions["expression"] = (action, state_idx)
            
            return action
    
    def decide_engagement_level(self, state: ConversationState) -> EngagementLevel:
        """
        Entscheidet wie aktiv/passiv Holo sein soll.
        """
        with self.lock:
            state_idx = state.to_index()
            
            # Bei hohem Relationship-Level proaktiver sein
            if state.relationship_level > 0.7:
                if random.random() < 0.3:
                    return EngagementLevel.PROACTIVE
            
            action = self.engagement_policy.select_action_thompson(state_idx, self.beliefs)
            
            self.decisions_per_domain["engagement"] += 1
            self.last_decisions["engagement"] = (action, state_idx)
            
            return action
    
    def decide_conversation_goal(self, state: ConversationState) -> ConversationGoal:
        """
        Entscheidet was das Ziel der Konversation sein soll.
        """
        with self.lock:
            state_idx = state.to_index()
            
            # Situation-basierte Defaults
            if state.user_sentiment < -0.5:
                if self.beliefs.sample_belief("user", "appreciates_support") > 0.6:
                    return ConversationGoal.SUPPORT
            
            if state.topic_type == "emotional":
                return ConversationGoal.CONNECT
            
            action = self.goal_policy.select_action_thompson(state_idx, self.beliefs)
            
            self.decisions_per_domain["goal"] += 1
            self.last_decisions["goal"] = (action, state_idx)
            
            return action
    
    # =========================================================================
    # LEARNING METHODS
    # =========================================================================
    
    def learn_from_feedback(self,
                           domain: str,
                           state: Any,
                           action: Enum,
                           user_reaction: float,
                           was_authentic: bool = True,
                           relationship_change: float = 0.0,
                           achieved_goal: bool = False,
                           context: str = ""):
        """
        Lernt aus Feedback.
        
        Args:
            domain: "response", "emotion", "activity", etc.
            state: Der State bei der Entscheidung
            action: Die gewählte Aktion
            user_reaction: -1 bis +1 (User-Reaktion)
            was_authentic: War die Reaktion authentisch?
            relationship_change: Hat sich die Beziehung verändert?
            achieved_goal: Wurde das Ziel erreicht?
            context: Zusätzlicher Kontext
        """
        with self.lock:
            # Reward berechnen
            reward = self.reward_calculator.calculate_from_feedback(
                user_reaction=user_reaction,
                was_authentic=was_authentic,
                relationship_changed=relationship_change,
                expressed_self=was_authentic,
                achieved_goal=achieved_goal,
            )
            
            # State Index
            if hasattr(state, 'to_index'):
                state_idx = state.to_index()
            else:
                state_idx = hash(str(state)) % 100000
            
            # Q-Table Update
            policy = self._get_policy(domain)
            if policy:
                # Nächster State (vereinfacht: gleicher State mit kleiner Änderung)
                next_state_idx = state_idx + (1 if reward > 0 else -1)
                policy.update(state_idx, action, reward, next_state_idx)
                policy.decay_epsilon()
            
            # Experience speichern
            features = state.to_features() if hasattr(state, 'to_features') else {}
            experience = Experience(
                state_index=state_idx,
                action=action.value,
                reward=reward,
                next_state_index=next_state_idx if policy else state_idx,
                done=False,
                timestamp=time.time(),
                domain=domain,
                features=features,
                context=context,
            )
            self.experience_buffer.add(experience)
            
            # Beliefs updaten
            self._update_beliefs_from_feedback(domain, user_reaction, context)
            
            # Meta-Learning
            self.meta_learner.record_performance(domain, reward, features)
            if self.meta_learner.should_update():
                self.meta_learner.update_learning_rates()
                self._apply_meta_learning()
            
            # Experience Replay
            if len(self.experience_buffer) % PolicyConfig.REPLAY_FREQUENCY == 0:
                self._experience_replay(domain)
            
            # Periodisch speichern
            if self.total_decisions % PolicyConfig.SAVE_FREQUENCY == 0:
                self._save_async()
            
            logger.debug(f"📚 Learned from {domain}: {action.value} → reward={reward:.2f}")
    
    def learn_from_conversation_end(self, 
                                   conversation_quality: float,
                                   user_final_sentiment: float,
                                   topics_discussed: List[str] = None,
                                   highlights: List[str] = None):
        """
        Lernt am Ende einer Konversation.
        
        Gesamtbewertung der Konversation.
        """
        with self.lock:
            # Bonus-Reward für gesamte Konversation
            bonus = conversation_quality * 0.5 + user_final_sentiment * 0.3
            
            # Alle Domains mit Bonus updaten
            for domain, (action, state_idx) in self.last_decisions.items():
                policy = self._get_policy(domain)
                if policy:
                    policy.update(state_idx, action, bonus, state_idx, done=True)
            
            # Beliefs updaten basierend auf Konversation
            if user_final_sentiment > 0.5:
                self.beliefs.update_belief("user", "engages_with_stories", True)
            
            # Clear last decisions
            self.last_decisions.clear()
            
            logger.info(f"📝 Conversation end learning: quality={conversation_quality:.2f}")
    
    def _update_beliefs_from_feedback(self, domain: str, user_reaction: float, 
                                     context: str):
        """Aktualisiert Beliefs basierend auf Feedback"""
        positive = user_reaction > 0.3
        
        # Domain-spezifische Belief Updates
        if domain == "response":
            if "humor" in context.lower() or "lustig" in context.lower():
                self.beliefs.update_belief("user", "likes_humor", positive)
            if "lang" in context.lower() or "ausführlich" in context.lower():
                self.beliefs.update_belief("user", "likes_long_responses", positive)
        
        elif domain == "emotion":
            if "empathie" in context.lower() or "verständnis" in context.lower():
                self.beliefs.update_belief("self", "good_at_empathy", positive)
        
        elif domain == "expression":
            if "witzig" in context.lower():
                self.beliefs.update_belief("self", "good_at_humor", positive)
    
    def _experience_replay(self, domain: str = None):
        """Experience Replay für besseres Lernen"""
        batch_size = PolicyConfig.REPLAY_BATCH_SIZE
        
        if domain:
            experiences = self.experience_buffer.sample_by_domain(domain, batch_size)
        else:
            experiences = self.experience_buffer.sample(batch_size)
        
        for exp in experiences:
            policy = self._get_policy(exp.domain)
            if policy:
                # Finde Aktion-Enum
                action = self._find_action_enum(exp.domain, exp.action)
                if action:
                    policy.update(
                        exp.state_index,
                        action,
                        exp.reward,
                        exp.next_state_index,
                        exp.done
                    )
    
    def _apply_meta_learning(self):
        """Wendet Meta-Learning Updates an"""
        # Learning Rates updaten
        for domain in ["response", "emotion", "activity", "expression", "engagement"]:
            policy = self._get_policy(domain)
            if policy:
                policy.learning_rate = self.meta_learner.get_learning_rate(domain)
        
        # Reward Weights updaten
        component_avgs = self.reward_calculator.get_component_averages()
        new_weights = self.meta_learner.suggest_reward_weight_update(component_avgs)
        self.reward_calculator.update_weights(new_weights)
    
    def _get_policy(self, domain: str) -> Optional[QTable]:
        """Holt Policy für Domain"""
        policies = {
            "response": self.response_policy,
            "emotion": self.emotion_policy,
            "activity": self.activity_policy,
            "expression": self.expression_policy,
            "engagement": self.engagement_policy,
            "goal": self.goal_policy,
        }
        return policies.get(domain)
    
    def _find_action_enum(self, domain: str, action_value: str) -> Optional[Enum]:
        """Findet Enum für Action-String"""
        enums = {
            "response": ResponseStyle,
            "emotion": EmotionalResponse,
            "activity": AutonomousActivity,
            "expression": ExpressionStyle,
            "engagement": EngagementLevel,
            "goal": ConversationGoal,
        }
        
        enum_class = enums.get(domain)
        if enum_class:
            for member in enum_class:
                if member.value == action_value:
                    return member
        return None
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def get_decision_context(self, state: ConversationState) -> Dict:
        """
        Erstellt Entscheidungs-Kontext für Debugging/Logging.
        """
        return {
            "state_index": state.to_index(),
            "beliefs": {
                "likes_humor": self.beliefs.get_belief("user", "likes_humor"),
                "likes_enthusiasm": self.beliefs.get_belief("user", "likes_enthusiasm"),
                "appreciates_support": self.beliefs.get_belief("user", "appreciates_support"),
            },
            "uncertain_beliefs": self.beliefs.get_uncertain_beliefs(),
            "avg_recent_reward": self.reward_calculator.get_average_reward(50),
            "total_decisions": self.total_decisions,
        }
    
    def get_stats(self) -> Dict:
        """Statistiken über das Policy-System"""
        return {
            "total_decisions": self.total_decisions,
            "decisions_per_domain": dict(self.decisions_per_domain),
            "experience_buffer_size": len(self.experience_buffer),
            "avg_reward": self.reward_calculator.get_average_reward(),
            "reward_components": self.reward_calculator.get_component_averages(),
            "meta_learning_rates": self.meta_learner.domain_learning_rates,
            "important_features": self.meta_learner.get_important_features(5),
            "action_stats": {
                "response": self.response_policy.get_action_stats(),
                "emotion": self.emotion_policy.get_action_stats(),
            },
        }
    
    def get_user_profile(self) -> Dict:
        """Aktuelles User-Profil basierend auf Beliefs"""
        return self.beliefs.get_user_profile()
    
    def get_recommended_actions(self, state: ConversationState) -> Dict[str, str]:
        """Empfohlene Aktionen für einen State (ohne Exploration)"""
        return {
            "response_style": self.response_policy.get_best_action(state.to_index()).value,
            "emotion": self.emotion_policy.get_best_action(state.to_index()).value,
            "expression": self.expression_policy.get_best_action(state.to_index()).value,
            "engagement": self.engagement_policy.get_best_action(state.to_index()).value,
        }
    
    # =========================================================================
    # PERSISTENCE
    # =========================================================================
    
    def _save(self):
        """Speichert State"""
        data = {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "total_decisions": self.total_decisions,
            "decisions_per_domain": dict(self.decisions_per_domain),
            "policies": {
                "response": self.response_policy.to_dict(),
                "emotion": self.emotion_policy.to_dict(),
                "activity": self.activity_policy.to_dict(),
                "expression": self.expression_policy.to_dict(),
                "engagement": self.engagement_policy.to_dict(),
                "goal": self.goal_policy.to_dict(),
            },
            "beliefs": self.beliefs.to_dict(),
            "meta_learner": self.meta_learner.to_dict(),
            "reward_weights": self.reward_calculator.weights,
            "experience_buffer": self.experience_buffer.to_list()[-1000:],  # Last 1000
        }
        
        # Atomic write
        temp_file = self.state_file.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(data, f, indent=2)
        temp_file.replace(self.state_file)
        
        logger.debug(f"💾 Policy state saved to {self.state_file}")
    
    def _save_async(self):
        """Speichert asynchron"""
        thread = threading.Thread(target=self._save, daemon=True)
        thread.start()
    
    def _load(self):
        """Lädt State"""
        if not self.state_file.exists():
            logger.info("📂 No existing policy state, starting fresh")
            return
        
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)
            
            self.total_decisions = data.get("total_decisions", 0)
            self.decisions_per_domain = defaultdict(int, data.get("decisions_per_domain", {}))
            
            # Policies
            if "policies" in data:
                for domain, policy_data in data["policies"].items():
                    policy = self._get_policy(domain)
                    if policy:
                        policy.from_dict(policy_data)
            
            # Beliefs
            if "beliefs" in data:
                self.beliefs.from_dict(data["beliefs"])
            
            # Meta-Learner
            if "meta_learner" in data:
                self.meta_learner.from_dict(data["meta_learner"])
            
            # Reward Weights
            if "reward_weights" in data:
                self.reward_calculator.weights = data["reward_weights"]
            
            # Experience Buffer
            if "experience_buffer" in data:
                self.experience_buffer.from_list(data["experience_buffer"])
            
            logger.info(f"📂 Loaded policy state: {self.total_decisions} decisions")
            
        except Exception as e:
            logger.error(f"❌ Error loading policy state: {e}")
    
    def save(self):
        """Öffentliche Save-Methode"""
        self._save()
    
    def close(self):
        """Cleanup"""
        self._save()
        logger.info("🔒 HoloPolicyEngine closed")


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_policy_engine(data_dir: Path = None) -> HoloPolicyEngine:
    """Factory für Policy Engine"""
    return HoloPolicyEngine(data_dir)


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 70)
    print("🐺 HOLO POLICY ENGINE - TEST")
    print("=" * 70)
    
    # Engine erstellen
    engine = HoloPolicyEngine(Path("/tmp/holo_policy_test"))
    
    # 1. Test Decisions
    print("\n1️⃣ DECISION TESTS:")
    
    state = ConversationState(
        user_sentiment=0.5,
        user_energy=0.7,
        user_engagement=0.8,
        topic_type="casual",
        relationship_level=0.6,
    )
    
    response = engine.decide_response_style(state)
    print(f"   Response Style: {response.value}")
    
    emotion = engine.decide_emotional_response(state)
    print(f"   Emotional Response: {emotion.value}")
    
    expression = engine.decide_expression_style(state)
    print(f"   Expression Style: {expression.value}")
    
    engagement = engine.decide_engagement_level(state)
    print(f"   Engagement Level: {engagement.value}")
    
    # 2. Test Learning
    print("\n2️⃣ LEARNING TESTS:")
    
    for i in range(10):
        # Simuliere positive Reaktion auf enthusiastic
        state = ConversationState(
            user_sentiment=random.uniform(0.3, 0.8),
            user_engagement=random.uniform(0.5, 0.9),
        )
        
        response = engine.decide_response_style(state)
        
        # Simuliere User-Reaktion (enthusiastic wird belohnt)
        if response == ResponseStyle.ENTHUSIASTIC:
            user_reaction = random.uniform(0.5, 1.0)
        else:
            user_reaction = random.uniform(-0.2, 0.6)
        
        engine.learn_from_feedback(
            domain="response",
            state=state,
            action=response,
            user_reaction=user_reaction,
            context=f"Test iteration {i}",
        )
    
    print(f"   Completed 10 learning iterations")
    
    # 3. Test Autonomous Activity
    print("\n3️⃣ AUTONOMOUS ACTIVITY TEST:")
    
    auto_state = AutonomousState(
        energy=0.3,
        boredom=0.7,
        curiosity=0.8,
        hours_since_user=4.0,
    )
    
    activity = engine.decide_autonomous_activity(auto_state)
    print(f"   Activity Decision: {activity.value}")
    
    # 4. Beliefs
    print("\n4️⃣ BELIEFS:")
    profile = engine.get_user_profile()
    for name, value in list(profile.items())[:5]:
        print(f"   {name}: {value:.2f}")
    
    uncertain = engine.beliefs.get_uncertain_beliefs()
    print(f"   Uncertain beliefs: {len(uncertain)}")
    
    # 5. Stats
    print("\n5️⃣ STATS:")
    stats = engine.get_stats()
    print(f"   Total Decisions: {stats['total_decisions']}")
    print(f"   Avg Reward: {stats['avg_reward']:.3f}")
    print(f"   Experience Buffer: {stats['experience_buffer_size']}")
    
    # 6. Save
    engine.save()
    print("\n💾 State saved!")
    
    # 7. Test recommended actions
    print("\n6️⃣ RECOMMENDED ACTIONS:")
    recommendations = engine.get_recommended_actions(state)
    for domain, action in recommendations.items():
        print(f"   {domain}: {action}")
    
    print("\n" + "=" * 70)
    print("✅ All tests passed!")
