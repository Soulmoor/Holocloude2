#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO COGNITIVE ENGINE - Denken vor dem Sprechen                             ║
║                                                                              ║
║  Bevor Holo antwortet, durchläuft sie einen Denkprozess:                     ║
║                                                                              ║
║  1. ANALYSE    → Was meint der User? (Intent, Emotion, Kontext)              ║
║  2. RESEARCH   → Was weiß ich darüber? (Wissen, Erinnerungen)                ║
║  3. REASONING  → Was ist die beste Antwort? (Logik, Relevanz)                ║
║  4. GENERATION → Antwort formulieren                                         ║
║  5. VALIDATION → Macht das Sinn? Passt das zur Frage?                        ║
║                                                                              ║
║  Wie ein Mensch: Nachdenken → Antworten                                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import re
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import Counter

logger = logging.getLogger(__name__)


# =============================================================================
# DATENSTRUKTUREN
# =============================================================================

class MessageType(Enum):
    """Typ der Nachricht"""
    GREETING = "greeting"
    FAREWELL = "farewell"
    QUESTION = "question"
    STATEMENT = "statement"
    COMMAND = "command"
    EMOTIONAL = "emotional"
    SMALLTALK = "smalltalk"
    TECHNICAL = "technical"
    CREATIVE = "creative"
    UNKNOWN = "unknown"


class QuestionType(Enum):
    """Art der Frage"""
    YES_NO = "yes_no"           # Ja/Nein Frage
    WHAT = "what"               # Was ist...
    HOW = "how"                 # Wie...
    WHY = "why"                 # Warum...
    WHO = "who"                 # Wer...
    WHEN = "when"               # Wann...
    WHERE = "where"             # Wo...
    WHICH = "which"             # Welche...
    HOW_MUCH = "how_much"       # Wie viel...
    OPINION = "opinion"         # Meinungsfrage
    RHETORICAL = "rhetorical"   # Rhetorische Frage
    NONE = "none"               # Keine Frage


class ResponseStrategy(Enum):
    """Antwort-Strategie"""
    INFORM = "inform"           # Informieren
    EMPATHIZE = "empathize"     # Mitfühlen
    ASK_BACK = "ask_back"       # Rückfragen
    CONFIRM = "confirm"         # Bestätigen
    DENY = "deny"               # Verneinen
    JOKE = "joke"               # Scherzen
    DEFLECT = "deflect"         # Ablenken (wenn unsicher)
    SHARE = "share"             # Eigenes teilen
    HELP = "help"               # Helfen wollen


@dataclass
class MessageAnalysis:
    """Analyse einer Nachricht"""
    # Grundlagen
    raw_text: str
    normalized_text: str
    words: List[str]
    word_count: int
    
    # Klassifizierung
    message_type: MessageType
    question_type: QuestionType
    confidence: float
    
    # Inhalt
    topics: List[str]
    entities: List[str]  # Namen, Orte, etc.
    keywords: List[str]
    
    # Emotion
    user_emotion: Optional[str]
    emotion_intensity: float
    sentiment: str  # positive, negative, neutral
    
    # Kontext
    references_previous: bool
    is_follow_up: bool
    needs_context: bool
    
    # Meta
    is_urgent: bool
    expects_action: bool
    expects_information: bool


@dataclass
class ThoughtProcess:
    """Holos Denkprozess"""
    # Analyse
    analysis: MessageAnalysis
    
    # Research
    relevant_knowledge: List[Dict]
    relevant_memories: List[Dict]
    current_context: Dict
    
    # Reasoning
    possible_responses: List[Dict]
    chosen_strategy: ResponseStrategy
    reasoning_steps: List[str]
    
    # Validierung
    response_draft: str
    validation_passed: bool
    validation_issues: List[str]
    
    # Final
    final_response: str
    confidence: float


# =============================================================================
# TEXT-ANALYSE
# =============================================================================

class TextAnalyzer:
    """
    Analysiert Text um zu verstehen was der User meint.
    """
    
    # Deutsche Frage-Wörter
    QUESTION_STARTERS = {
        "was": QuestionType.WHAT,
        "wie": QuestionType.HOW,
        "warum": QuestionType.WHY,
        "weshalb": QuestionType.WHY,
        "wieso": QuestionType.WHY,
        "wer": QuestionType.WHO,
        "wann": QuestionType.WHEN,
        "wo": QuestionType.WHERE,
        "woher": QuestionType.WHERE,
        "wohin": QuestionType.WHERE,
        "welche": QuestionType.WHICH,
        "welcher": QuestionType.WHICH,
        "welches": QuestionType.WHICH,
        "wieviel": QuestionType.HOW_MUCH,
        "wie viel": QuestionType.HOW_MUCH,
    }
    
    # Ja/Nein Frage Indikatoren
    YES_NO_STARTERS = [
        "ist", "sind", "war", "waren", "wird", "werden",
        "hat", "haben", "hatte", "hatten",
        "kann", "können", "könnte", "könnten",
        "soll", "sollte", "muss", "müsste",
        "darf", "darfst", "magst", "möchtest",
        "hast du", "bist du", "kannst du", "willst du",
    ]
    
    # Emotions-Keywords
    # EMOTION_KEYWORDS - Ultra-erweitert (9x mehr Wörter pro Kategorie)
    EMOTION_KEYWORDS = {
        "happy": [
            # Grundformen
            "freue", "glücklich", "toll", "super", "geil", "nice", "cool", "yay", "hurra",
            "fantastisch", "wunderbar", "großartig", "perfekt", "herrlich", "genial",
            "klasse", "prima", "spitze", "mega", "hammer", "krass", "lit", "awesome",
            "fabelhaft", "phänomenal", "sensationell", "grandios", "traumhaft", "himmlisch",
            "bezaubernd", "entzückend", "prächtig", "exzellent", "brillant", "bombig",
            "dufte", "knorke", "famos", "formidabel", "fulminant", "glorreich",
            # Phrasen
            "freut mich", "bin froh", "macht spaß", "liebe es", "begeistert", "happy",
            "bin happy", "freu mich", "juhu", "endlich", "geschafft", "gewonnen",
            "das ist ja toll", "wie schön", "was für ein glück", "bin beglückt",
            "das macht mich happy", "fühle mich gut", "mir gehts gut", "alles bestens",
            "könnte nicht besser sein", "bin zufrieden", "fühle mich wohl", "bin erfreut",
            "das freut mich riesig", "bin überaus froh", "bin selig", "bin entzückt",
            "mein herz hüpft", "bin high vor glück", "vor freude platzen", "jauchze",
            "jubele", "triumphiere", "feiere", "bin am feiern", "party", "partytime",
            # Verstärkungen
            "richtig gut", "echt toll", "total schön", "so froh", "überglücklich",
            "im siebten himmel", "auf wolke sieben", "strahle", "lache", "lächle",
            "mega happy", "ultra zufrieden", "extrem froh", "wahnsinnig glücklich",
            "unglaublich toll", "unfassbar schön", "so so gut", "einfach nur geil",
            "richtig richtig gut", "besser gehts nicht", "top of the world",
            "völlig euphorisch", "high on life", "über den wolken", "schwebend",
            # Jugendsprache
            "gönnung", "läuft bei mir", "isso", "safe", "vallah gut", "mashallah",
            "no cap", "fr fr", "slay", "based", "goated", "w", "dub", "fire",
            "sheesh", "bussin", "valid", "bet", "lowkey happy", "highkey happy",
            "vibe", "good vibes", "vibes on point", "mood", "big mood", "same",
            "real", "facts", "periodt", "ate", "serve", "iconic", "legend", "king shit",
            "queen shit", "main character energy", "living my best life", "winning",
            # Dialekt/Regional
            "ganz wunderbar", "echt fein", "wirklich schee", "richtig leiwand",
            "total guat", "voll fett", "echt stark", "richtig cool",
        ],
        "sad": [
            # Grundformen
            "traurig", "schlecht", "mies", "down", "depri", "unglücklich", "einsam",
            "allein", "verletzt", "enttäuscht", "niedergeschlagen", "bedrückt",
            "weinen", "tränen", "schmerzt", "tut weh", "vermisse", "hoffnungslos",
            "leer", "schwer ums herz", "melancholisch", "deprimiert", "gebrochen",
            "gramgebeugt", "kummervoll", "sorgenvoll", "freudlos", "trostlos", "düster",
            "bekümmert", "betrübt", "elend", "jämmerlich", "erbärmlich", "miserabel",
            "untröstlich", "verzagt", "mutlos", "entmutigt", "resigniert", "aufgegeben",
            # Phrasen
            "geht mir schlecht", "fühle mich mies", "am boden", "am ende",
            "will nicht mehr", "keine kraft", "trauere", "heule", "weine",
            "tut mir leid", "bereue", "schuldig", "versagt", "gescheitert",
            "bin am boden zerstört", "mein herz ist schwer", "mir ist zum heulen",
            "könnte weinen", "tränen in den augen", "bin so down", "fühle mich leer",
            "hab keine energie", "alles ist grau", "sehe schwarz", "kein licht",
            "bin am verzweifeln", "weiß nicht weiter", "hab aufgegeben", "ist mir egal",
            "interessiert mich nicht mehr", "hab keinen bock mehr", "will nur schlafen",
            "will meine ruhe", "lass mich in ruhe", "will allein sein", "brauche zeit",
            "muss das verarbeiten", "komm nicht drüber weg", "vermisse so sehr",
            # Verstärkungen
            "so traurig", "todunglücklich", "am verzweifeln", "zerstört",
            "innerlich leer", "kaputt gemacht", "fertig mit der welt",
            "komplett am ende", "total fertig", "völlig zerstört", "richtig down",
            "mega traurig", "extrem niedergeschlagen", "zutiefst betrübt",
            "am boden zerstört", "seelisch am ende", "emotional kaputt",
            # Jugendsprache
            "im feels", "in meinen feels", "sad boy hours", "sad girl hours",
            "crying rn", "literally crying", "broken", "dead inside", "numb",
            "depresso", "big sad", "smol sad", "in pain", "hurting", "struggling",
            "not okay", "not fine", "falling apart", "giving up", "done", "over it",
        ],
        "angry": [
            # Grundformen
            "wütend", "sauer", "genervt", "frustriert", "verärgert", "hasse",
            "aggressiv", "zornig", "stinksauer", "aufgebracht", "empört",
            "entrüstet", "rasend", "böse", "angepisst", "getriggert",
            "fuchsteufelswild", "tobend", "schäumend", "kochend", "siedend",
            "grimmig", "grollend", "hasserfüllt", "verbittert", "erbost",
            "erzürnt", "aufbrausend", "cholerisch", "hitzig", "jähzornig",
            # Phrasen
            "kotzt mich an", "nervt", "zum kotzen", "unfassbar", "unverschämt",
            "frechheit", "geht gar nicht", "regt mich auf", "macht mich wahnsinnig",
            "könnte platzen", "könnte ausrasten", "bring mich um",
            "ich könnte schreien", "mir platzt der kragen", "mir reicht es",
            "hab die schnauze voll", "bin es leid", "nicht mit mir",
            "das gibts doch nicht", "ich fass es nicht", "was soll das",
            "wie kann man nur", "das ist doch nicht wahr", "ich glaubs nicht",
            "hör auf damit", "lass das", "mach das nie wieder", "ich warne dich",
            "pass auf was du sagst", "das wirst du bereuen", "warte nur ab",
            "mir reichts", "jetzt ist schluss", "jetzt reicht es aber",
            "ich hab genug", "das wars", "fertig", "aus", "ende", "schluss",
            # Verstärkungen
            "so sauer", "mega genervt", "richtig wütend", "fuchsteufelswild",
            "auf 180", "am ausrasten", "kurz vorm explodieren",
            "total angepisst", "komplett durch", "absolut fertig", "extrem wütend",
            "unfassbar sauer", "wahnsinnig genervt", "höllisch aufgebracht",
            "stinksauer", "stocksauer", "fuchtbar wütend", "rasend vor wut",
            "blind vor wut", "rot sehen", "platze vor wut", "bebe vor wut",
            # Jugendsprache
            "tilted", "triggered", "salzig", "salty", "toxic", "cringe",
            "mad", "pissed", "heated", "pressed", "tight", "vexed", "livid",
            "fuming", "raging", "seething", "malding", "coping", "tilted af",
            "literally shaking", "cant even", "im done", "thats it", "cancelled",
            # Kraftausdrücke (mild)
            "mist", "verdammt", "verflixt", "mensch", "mann", "alter",
            "boah", "ey", "ach komm", "jetzt aber mal", "was ist das denn",
        ],
        "anxious": [
            # Grundformen
            "angst", "sorge", "nervös", "unsicher", "ängstlich", "beunruhigt",
            "gestresst", "stress", "panik", "befürchte", "besorgt", "unruhig",
            "aufgewühlt", "überfordert", "überwältigt", "angespannt", "bange",
            "verängstigt", "verschreckt", "eingeschüchtert", "verunsichert", "zittrig",
            "fahrig", "hektisch", "rastlos", "ruhelos", "getrieben", "gehetzt",
            "paranoid", "misstrauisch", "argwöhnisch", "skeptisch", "zweifelnd",
            # Phrasen
            "mache mir sorgen", "hab angst", "kriege panik", "zittere",
            "kann nicht schlafen", "drehe durch", "werde verrückt",
            "schaffe das nicht", "zu viel", "halte das nicht aus",
            "mir ist mulmig", "hab ein schlechtes gefühl", "ahne böses",
            "das endet nicht gut", "hab angst dass", "was wenn", "und wenn",
            "hoffentlich nicht", "bitte nicht", "das darf nicht", "oh nein",
            "mir wird schlecht", "mir ist übel", "mir ist schwindelig",
            "mein herz rast", "herzrasen", "bekomme keine luft", "atemnot",
            "kalter schweiß", "zitternde hände", "wackelige knie", "flau im magen",
            "muss das klappen", "was ist wenn nicht", "stelle mir vor dass",
            "denke die ganze zeit an", "kann nicht aufhören zu denken",
            "gedankenkarussell", "grübele", "zerbreche mir den kopf",
            # Verstärkungen
            "totale panik", "richtig angst", "mega stress", "am durchdrehen",
            "am limit", "kurz vorm zusammenbruch", "anxiety", "panikanfall",
            "extreme angst", "lähmende furcht", "blanke panik", "horror",
            "absolute überforderung", "völlig überfordert", "komplett gestresst",
            "maximal angespannt", "auf der kippe", "kurz vorm nervenzusammenbruch",
            # Jugendsprache
            "anxious af", "anxiety hitting", "stressed tf out", "freaking out",
            "lowkey scared", "highkey scared", "paranoid vibes", "bad vibes",
            "intrusive thoughts", "spiraling", "overthinking", "in my head",
            "cant breathe", "help", "sos", "dying inside", "existential crisis",
        ],
        "tired": [
            # Grundformen
            "müde", "erschöpft", "kaputt", "fertig", "platt", "ko", "ausgelaugt",
            "schlapp", "energielos", "kraftlos", "matt", "todmüde", "hundemüde",
            "ausgebrannt", "burnout", "übermüdet", "schlaflos", "groggy",
            "ermattet", "erledigt", "abgespannt", "abgeschlafft", "ausgepower",
            "leer", "lahm", "träge", "schwerfällig", "schläfrig", "benommen",
            "dösig", "taumelig", "wackelig", "angeschlagen", "mitgenommen",
            # Phrasen
            "am ende", "keine energie", "brauche schlaf", "will ins bett",
            "kann nicht mehr", "bin am arsch", "bin im eimer", "bin durch",
            "total am ende", "komplett fertig", "völlig kaputt", "richtig platt",
            "hab keine kraft mehr", "bin völlig erledigt", "bin fix und fertig",
            "könnte auf der stelle einschlafen", "fallen mir die augen zu",
            "kämpfe gegen den schlaf", "halte die augen kaum offen", "gähne ständig",
            "brauch nen kaffee", "brauch energy", "brauch ne pause",
            "muss mich hinlegen", "muss mich ausruhen", "brauch mal ruhe",
            "der tag war anstrengend", "war ein langer tag", "hab viel gemacht",
            "bin geschafft", "hab mich verausgabt", "bin ausgepower",
            "laufe auf reserve", "tank ist leer", "akku ist leer", "bin auf null",
            # Verstärkungen
            "so müde", "total fertig", "richtig kaputt", "komplett am ende",
            "könnte sofort einschlafen", "schlafe gleich ein", "döse weg",
            "mega müde", "extrem erschöpft", "wahnsinnig platt", "unfassbar fertig",
            "bin ein zombie", "bin ein wrack", "funktioniere nicht mehr",
            "bin nur noch eine hülle", "bin tot", "bin am verrecken",
            # Jugendsprache
            "dead tired", "exhausted af", "running on empty", "need sleep",
            "zzz", "sleepy boi", "sleepy girl", "nap time", "bed calling",
            "literally dying", "cant function", "zombie mode", "barely alive",
            "need caffeine", "coffee needed", "energy at zero", "battery dead",
        ],
        "excited": [
            # Grundformen
            "aufgeregt", "gespannt", "hyped", "kribbelt", "zappelig", "ungeduldig",
            "elektrisiert", "fiebere", "begeistert", "enthusiastisch",
            "euphorisch", "ekstatisch", "berauscht", "verzückt", "hingerissen",
            "fasziniert", "gebannt", "gefesselt", "mitgerissen", "ergriffen",
            "entflammt", "brennend", "leidenschaftlich", "eifrig", "begierig",
            # Phrasen
            "kann nicht warten", "freue mich riesig", "kann es kaum erwarten",
            "total gespannt", "so aufgeregt", "bin so hyped", "zähle die tage",
            "platze gleich", "halte es nicht aus", "so excited",
            "bin total aufgeregt", "bin mega gespannt", "freue mich so sehr",
            "das wird so geil", "das wird hammer", "das wird epic",
            "ich kanns nicht abwarten", "wann geht es endlich los",
            "noch wie lange", "ist es schon soweit", "bin schon ganz hibbelig",
            "mein herz klopft", "hab schmetterlinge im bauch", "bin nervös vor freude",
            "vor aufregung zittern", "aufregung steigt", "spannung steigt",
            "fiebere dem entgegen", "kann mich kaum halten", "tanze vor freude",
            # Verstärkungen
            "mega aufgeregt", "ultra hyped", "extrem gespannt", "wahnsinnig aufgeregt",
            "so so gespannt", "richtig richtig hyped", "bin komplett aus dem häuschen",
            "bin total durch den wind", "bin völlig aufgelöst", "platze vor vorfreude",
            # Jugendsprache
            "les goooo", "lets go", "omg", "oh mein gott", "krass",
            "im so hyped", "cant wait", "counting down", "buzzing", "pumped",
            "stoked", "amped", "fired up", "ready to go", "bring it on",
            "yooo", "yaaas", "lets goooo", "im ready", "born ready",
            "this is it", "the moment", "its happening", "finally",
        ],
        "confused": [
            # Grundformen
            "verwirrt", "irritiert", "ratlos", "perplex", "durcheinander", "lost",
            "unklar", "verstehe nicht", "kapier nicht", "check nicht",
            "desorientiert", "konfus", "verständnislos", "ahnungslos", "unwissend",
            "überfragt", "überrumpelt", "übertölpelt", "verdutzt", "verdattert",
            "verblüfft", "überrascht", "fassungslos", "konsterniert", "bestürzt",
            # Phrasen
            "hä", "was", "wie bitte", "keinen plan", "keine ahnung", "wtf",
            "was zum", "häh", "öhm", "ähm", "hm", "hmm",
            "verstehe bahnhof", "blicke nicht durch", "bin raus",
            "verstehe die welt nicht mehr", "was ist hier los", "was geht ab",
            "was passiert hier", "was soll das", "wie meinst du das",
            "kannst du das erklären", "verstehe ich nicht", "ist mir unklar",
            "sehe das problem nicht", "wo ist das problem", "was genau",
            "wie jetzt", "und jetzt", "also was", "also wie", "also wann",
            "moment mal", "warte mal", "halt stop", "langsam", "nochmal",
            "kannst du wiederholen", "hab ich nicht verstanden", "war zu schnell",
            "zu kompliziert", "zu viel auf einmal", "bin überfordert",
            # Verstärkungen
            "total verwirrt", "komplett lost", "null plan", "gar keine ahnung",
            "absolut keinen schimmer", "nicht die geringste ahnung", "völlig ahnungslos",
            "bin komplett raus", "hab echt keinen plan", "check gar nichts",
            "verstehe null", "kapiere nix", "blick nicht durch",
            # Jugendsprache
            "bruh", "what", "huh", "im confused", "make it make sense",
            "explain", "wdym", "idk", "no clue", "beats me", "dunno",
            "lost af", "big confused", "brain hurts", "does not compute",
            "error 404", "brain.exe stopped working", "loading", "buffering",
        ],
        "grateful": [
            # Grundformen
            "danke", "dankbar", "wertschätze", "schätze", "erkenne an",
            "anerkennend", "respektvoll", "ehrfürchtig", "demütig", "bescheiden",
            "gerührt", "bewegt", "ergriffen", "berührt", "emotional",
            # Phrasen
            "lieb von dir", "nett von dir", "bedeutet mir viel", "bin dir dankbar",
            "schätze es sehr", "vielen dank", "tausend dank", "danke sehr",
            "danke schön", "herzlichen dank", "besten dank",
            "danke dir", "danke vielmals", "danke unendlich", "danke von herzen",
            "ich danke dir", "bin dir so dankbar", "werde das nie vergessen",
            "hast mir geholfen", "das war wichtig", "das hat viel bedeutet",
            "ohne dich hätte ich", "verdanke dir viel", "schulde dir was",
            "das rechne ich dir hoch an", "das war nicht selbstverständlich",
            "das weiß ich zu schätzen", "das bedeutet mir die welt",
            "du bist der/die beste", "was würde ich ohne dich machen",
            "ich wüsste nicht was ich ohne dich", "du bist gold wert",
            # Verstärkungen
            "so dankbar", "mega lieb", "echt nett", "richtig cool von dir",
            "unglaublich nett", "wahnsinnig lieb", "super lieb von dir",
            "das war echt spitze", "du bist echt klasse", "ich bin echt gerührt",
            "bin zu tränen gerührt", "fehlen mir die worte", "weiß gar nicht was sagen",
            # Jugendsprache
            "thanks", "thx", "ty", "tysm", "thank you sm", "appreciate it",
            "youre the best", "legend", "goat", "king", "queen", "real one",
            "blessed", "grateful af", "big thanks", "massive thanks",
        ],
        "loving": [
            # Grundformen
            "liebe", "lieb", "mag", "gern", "zuneigung", "verbunden", "nah",
            "verliebt", "verknallt", "verschossen", "vernarrt", "hingerissen",
            "bezaubert", "verzaubert", "fasziniert", "angetan", "begeistert",
            "innig", "herzlich", "warmherzig", "liebevoll", "zärtlich",
            # Phrasen
            "liebe dich", "mag dich", "hab dich lieb", "vermisse dich",
            "bist mir wichtig", "schätze dich", "hdl", "hdgdl", "ily",
            "denke an dich", "bist toll", "bist super", "bist besonders",
            "du bedeutest mir viel", "ich mag dich sehr", "ich schätze dich sehr",
            "du bist mir wichtig", "du bist was besonderes", "du bist einzigartig",
            "es gibt nur dich", "nur du", "für immer", "ewig", "zusammen",
            "mit dir", "bei dir", "an deiner seite", "du und ich",
            "wir zwei", "wir beide", "unser", "unsere", "gemeinsam",
            "kuscheln", "umarmen", "knuddeln", "drücken", "küssen",
            "nah sein", "zeit verbringen", "zusammen sein", "beieinander",
            # Verstärkungen
            "liebe dich so sehr", "hab dich so lieb", "bist das beste",
            "liebe dich über alles", "mehr als alles", "bis zum mond und zurück",
            "unendlich", "bedingungslos", "für immer und ewig", "bis ans ende",
            "du bist mein ein und alles", "ohne dich kann ich nicht",
            "du machst mich glücklich", "du machst mein leben schöner",
            # Jugendsprache
            "love you", "luv u", "ily sm", "ilysm", "love of my life",
            "my person", "my everything", "bae", "babe", "baby",
            "cutie", "sweetie", "honey", "darling", "sweetheart",
            "crush", "crushing hard", "simping", "down bad", "whipped",
        ],
        "hopeful": [
            # Grundformen
            "hoffe", "hoffnung", "zuversichtlich", "optimistisch", "erwarte",
            "vertrauend", "glaubend", "erwartend", "erhoffend", "wünschend",
            "positiv", "motiviert", "ermutigt", "inspiriert", "bestärkt",
            # Phrasen
            "wird schon", "glaube daran", "positiv gestimmt", "wird besser",
            "schaffe das", "klappt schon", "geht schon", "alles wird gut",
            "sehe licht", "am ende des tunnels", "es gibt noch hoffnung",
            "gebe nicht auf", "halte durch", "bleibe dran", "mache weiter",
            "vertraue darauf", "glaube fest", "bin mir sicher", "weiß es",
            "wird funktionieren", "muss klappen", "wird gelingen", "wird glücken",
            "freue mich drauf", "sehe das positiv", "bin guter dinge",
            "morgen ist ein neuer tag", "nach regen kommt sonne", "wird schon werden",
            "habe ein gutes gefühl", "spüre dass", "ahne gutes", "bin zuversichtlich",
            # Verstärkungen
            "fest davon überzeugt", "bin mir absolut sicher", "glaube felsenfest",
            "bin voller hoffnung", "bin voller zuversicht", "bin sehr optimistisch",
            "das klappt zu 100%", "wird definitiv", "ganz sicher", "bestimmt",
            # Jugendsprache
            "manifesting", "speaking it into existence", "positive vibes only",
            "good things coming", "its gonna be fine", "trust the process",
            "believe", "keep the faith", "stay positive", "stay hopeful",
            "things will work out", "itll be okay", "dont worry",
        ],
        "bored": [
            # Grundformen
            "langweilig", "öde", "fade", "gelangweilt", "monoton", "eintönig",
            "ereignislos", "reizlos", "lustlos", "antriebslos", "unmotiviert",
            "desinteressiert", "gleichgültig", "teilnahmslos", "apathisch",
            # Phrasen
            "nichts los", "langweile mich", "stumpfsinnig", "mir ist langweilig",
            "keine ahnung was machen", "weiß nicht was tun", "gammle rum",
            "hab nichts zu tun", "weiß nicht wohin mit mir", "drehe däumchen",
            "sitze rum", "hänge ab", "hocke hier", "chillen aber langweilig",
            "alles ist gleich", "jeden tag das gleiche", "nichts neues",
            "immer dasselbe", "kein highlight", "kein event", "passiert nix",
            "warte auf irgendwas", "warte dass was passiert", "wartend",
            "zeit totschlagen", "zeit vergeht nicht", "die zeit zieht sich",
            "uhr tickt so langsam", "minuten wie stunden", "stunden wie tage",
            # Verstärkungen
            "so langweilig", "sterbe vor langeweile", "totale langeweile",
            "mega langweilig", "ultra öde", "extrem fad", "wahnsinnig langweilig",
            "langweilig ohne ende", "tödlich langweilig", "zu tode gelangweilt",
            "bin kurz vorm einschlafen", "schlafe gleich ein vor langeweile",
            # Jugendsprache
            "bored af", "so bored", "dying of boredom", "nothing to do",
            "dead day", "dry", "mid", "meh", "whatever", "idc",
            "bored out of my mind", "entertain me", "need something to do",
            "somebody do something", "anyone there", "hello", "boring boring",
        ],
        "proud": [
            # Grundformen
            "stolz", "geschafft", "erreicht", "gewonnen", "erfolgreich",
            "triumphierend", "siegreich", "überlegen", "selbstbewusst", "selbstsicher",
            "zufrieden", "erfüllt", "bestätigt", "belohnt", "anerkannt",
            # Phrasen
            "bin stolz", "habs geschafft", "endlich geschafft", "ja mann",
            "yeees", "boah geil", "läuft bei mir", "king", "queen",
            "das war ich", "hab ich gemacht", "ist mein werk", "mein verdienst",
            "hab es bewiesen", "allen gezeigt", "wusste es", "hatte recht",
            "bin gut", "kann was", "hab drauf", "versteh mein handwerk",
            "hab mich durchgesetzt", "hab gewonnen", "bin der beste",
            "niemand kann mir was", "bin unbesiegbar", "bin der champion",
            "an der spitze", "ganz oben", "nummer eins", "first place",
            "hab abgeliefert", "performance war gut", "war stark", "war souverän",
            # Verstärkungen
            "mega stolz", "ultra proud", "richtig stolz", "bin so stolz",
            "stolz wie oscar", "stolz wie bolle", "platze vor stolz",
            "hab das verdient", "harte arbeit hat sich gelohnt", "endlich anerkannt",
            # Jugendsprache
            "flexing", "flex", "humble brag", "ngl proud", "ate that",
            "served", "slayed", "killed it", "nailed it", "crushed it",
            "boss move", "main character moment", "thats how its done",
            "ez", "easy win", "no challenge", "piece of cake", "childs play",
        ],
        "surprised": [
            # Grundformen
            "überrascht", "erstaunt", "verblüfft", "baff", "sprachlos",
            "verdutzt", "verdattert", "perplex", "fassungslos", "konsterniert",
            "schockiert", "geschockt", "erschüttert", "überwältigt", "übermannt",
            # Phrasen
            "wow", "krass", "echt jetzt", "wirklich", "no way", "was",
            "oh", "oha", "alter", "boah", "omg", "wtf", "heftig",
            "das gibts doch nicht", "kann nicht sein", "ist das wahr",
            "meinst du das ernst", "das ist nicht dein ernst", "ernsthaft",
            "im ernst", "wirklich wahr", "tatsächlich", "wahrhaftig",
            "hätte nicht gedacht", "damit hab ich nicht gerechnet", "unerwartet",
            "kam aus dem nichts", "total überraschend", "völlig unerwartet",
            "hab nicht kommen sehen", "bin platt", "haut mich um",
            "verschlägt mir die sprache", "fehlen mir die worte", "bin mundtot",
            "traue meinen augen nicht", "traue meinen ohren nicht", "glaub ich nicht",
            # Verstärkungen
            "mega überrascht", "total baff", "komplett sprachlos", "absolut perplex",
            "bin völlig von den socken", "hab meinen augen nicht getraut",
            "das hat mich umgehauen", "bin aus allen wolken gefallen",
            # Jugendsprache
            "shook", "shooketh", "mind blown", "what the", "bruh moment",
            "plot twist", "didnt see that coming", "wild", "insane", "crazy",
            "no shot", "cap", "thats cap", "wait what", "hold up",
            "say what now", "excuse me", "come again", "say sike rn",
        ],
        "disgusted": [
            # Grundformen
            "eklig", "widerlich", "abstoßend", "grausig", "bäh", "igitt",
            "widerwärtig", "abscheulich", "scheußlich", "grässlich", "gräulich",
            "unappetitlich", "übelkeitserregend", "ekelhaft", "ekelerregend",
            "anstößig", "anwidert", "zuwider", "verhasst", "unerträglich",
            # Phrasen
            "ist das eklig", "zum würgen", "mir wird schlecht", "kotz",
            "zum kotzen", "mir wird übel", "mir dreht sich der magen",
            "das ist ja widerlich", "pfui", "pfui teufel", "igittigitt",
            "bäh bäh", "nein danke", "weg damit", "will das nicht sehen",
            "muss nicht sein", "kann ich nicht ab", "vertrag ich nicht",
            "geht gar nicht", "absolutes no go", "das ist unter aller sau",
            "wie kann man nur", "unmöglich", "unverschämt", "geschmacklos",
            "niveaulos", "unterste schublade", "das letzte", "erbärmlich",
            # Verstärkungen
            "so eklig", "mega widerlich", "ultra abstoßend", "extrem grausig",
            "richtig ekelhaft", "total widerwärtig", "absolut abscheulich",
            "mir wird richtig schlecht", "könnte kotzen", "muss würgen",
            # Jugendsprache
            "ew", "ewww", "gross", "nasty", "disgusting", "yuck", "yikes",
            "big yikes", "thats foul", "thats vile", "hard pass", "nope",
            "absolutely not", "delete this", "cursed", "blursed", "thanks i hate it",
        ],
        "jealous": [
            # Grundformen
            "neidisch", "eifersüchtig", "missgünstig",
            "gierig", "habgierig", "begehrlich", "neidvoll", "scheel",
            "argwöhnisch", "misstrauisch", "besitzergreifend", "possessiv",
            # Phrasen
            "will das auch", "unfair", "warum ich nicht", "gönne nicht",
            "warum die und nicht ich", "warum immer die anderen",
            "hätte auch gern", "wünschte ich hätte", "wenn ich doch nur",
            "ist nicht fair", "ist ungerecht", "verdiene das auch",
            "bin neidisch auf", "bin eifersüchtig wegen", "gönne es nicht",
            "warum hab ich das nicht", "will auch so", "will auch das",
            "immer kriegen andere", "nie kriege ich", "komme immer zu kurz",
            "werde übersehen", "werde ignoriert", "beachtet mich nicht",
            "andere sind besser dran", "haben es besser", "haben mehr glück",
            # Verstärkungen
            "so neidisch", "mega eifersüchtig", "richtig missgünstig",
            "grün vor neid", "platze vor neid", "fresse mich auf vor neid",
            "bin krankhaft eifersüchtig", "macht mich wahnsinnig",
            # Jugendsprache
            "jealous af", "so jealous", "mad jealous", "lowkey jealous",
            "wish that was me", "me when", "could never be me",
            "they have it all", "must be nice", "lucky them", "not fair",
        ],
        "frustrated": [
            # Grundformen
            "frustriert", "enttäuscht", "entmutigt", "desillusioniert",
            "resigniert", "verzweifelt", "hoffnungslos", "ratlos",
            "genervt", "gereizt", "ungeduldig", "verärgert",
            # Phrasen
            "es klappt nicht", "funktioniert nicht", "geht nicht", "will nicht",
            "kriege es nicht hin", "schaffe es nicht", "komme nicht weiter",
            "stecke fest", "komme nicht voran", "drehe mich im kreis",
            "immer wieder das gleiche", "schon wieder", "nicht schon wieder",
            "hab alles versucht", "weiß nicht mehr weiter", "am ende mit meinem latein",
            "mache immer fehler", "klappt nie", "wird nie was", "ist sinnlos",
            "ist hoffnungslos", "ist aussichtslos", "bringt nichts",
            "warum geht das nicht", "warum klappt das nicht", "was mache ich falsch",
            # Verstärkungen
            "so frustriert", "mega frustriert", "total frustriert", "am verzweifeln",
            "bin am ende", "gebe gleich auf", "schmeiß alles hin", "hab keinen bock mehr",
            # Jugendsprache
            "frustrated af", "so done", "over it", "giving up", "cant even",
            "why wont it work", "its not working", "nothing works", "broken",
        ],
        # === NEUE KATEGORIEN (16 zusätzliche) ===
        "nostalgic": [
            # Grundformen
            "nostalgisch", "wehmütig", "sehnsüchtig", "vergangenheitsbezogen",
            "erinnernd", "schwelgend", "rückblickend", "melancholisch", "sentimentalisch",
            "romantisierend", "verklärt", "vermissend", "sehnsuchtsvoll",
            # Phrasen
            "früher war alles besser", "erinnere mich an", "damals als", "weißt du noch",
            "die guten alten zeiten", "das waren noch zeiten", "vermisse die zeit",
            "denke oft an früher", "wünschte es wäre wieder so", "wie früher",
            "als ich jung war", "als wir noch", "in meiner kindheit", "in meiner jugend",
            "hab gerade an dich gedacht", "erinnert mich an", "riecht nach kindheit",
            "schmeckt wie früher", "fühlt sich an wie damals", "wie zu hause",
            "alte erinnerungen", "schöne erinnerungen", "traurige erinnerungen",
            "bitter süß", "wehmut im herzen", "sehnsucht nach der vergangenheit",
            # Verstärkungen
            "so nostalgisch", "mega nostalgisch", "total wehmütig", "richtig sehnsüchtig",
            "bin ganz sentimental", "kommen alte gefühle hoch", "tränen der erinnerung",
            # Jugendsprache
            "nostalgia hitting", "right in the feels", "throwback", "tbt", "memories",
            "good old days", "take me back", "i miss this", "childhood memories",
        ],
        "content": [
            # Grundformen
            "zufrieden", "ausgeglichen", "gelassen", "entspannt", "ruhig",
            "friedlich", "harmonisch", "im reinen", "erfüllt", "gesättigt",
            "befriedigt", "genügsam", "bescheiden", "dankbar", "wohlauf",
            "satt", "selig", "behaglich", "wohlig", "gemütlich",
            # Phrasen
            "bin zufrieden", "passt so", "ist gut so", "reicht mir", "hab genug",
            "brauch nicht mehr", "bin im reinen mit mir", "alles ist gut",
            "kann nicht klagen", "läuft alles", "bin ganz entspannt", "chille gerade",
            "genieße den moment", "lebe im hier und jetzt", "bin bei mir",
            "fühle mich wohl", "fühle mich gut", "geht mir gut", "bin glücklich",
            "nichts zu beklagen", "alles in ordnung", "alles bestens", "passt alles",
            "so solls sein", "genau richtig", "perfekt so", "mehr brauch ich nicht",
            # Verstärkungen
            "total zufrieden", "richtig ausgeglichen", "komplett entspannt",
            "völlig im reinen", "absolut erfüllt", "mega chillig", "super relaxed",
            # Jugendsprache
            "im fine", "all good", "vibing", "just vibing", "life is good",
            "no complaints", "living the life", "blessed", "grateful", "at peace",
        ],
        "relieved": [
            # Grundformen
            "erleichtert", "befreit", "entlastet", "erlöst", "entspannt",
            "aufatmend", "losgelöst", "frei", "unbeschwert", "gelöst",
            "beruhigt", "getröstet", "besänftigt", "beschwichtigt",
            # Phrasen
            "puh", "gott sei dank", "zum glück", "endlich vorbei", "geschafft",
            "stein vom herzen", "last von den schultern", "kann aufatmen",
            "bin so erleichtert", "das wärs", "hab ichs hinter mir",
            "war ja doch nicht so schlimm", "ging ja doch gut", "hat geklappt",
            "ist gut gegangen", "war nur ein fehlalarm", "alles halb so wild",
            "kann wieder ruhig schlafen", "sorgen waren umsonst", "panik war unnötig",
            "bin erleichtert dass", "gut dass es vorbei ist", "endlich rum",
            "durchatmen", "aufatmen", "luft holen", "verschnaufpause",
            # Verstärkungen
            "so erleichtert", "mega erleichtert", "total befreit", "richtig froh",
            "unfassbar erleichtert", "könnte heulen vor erleichterung",
            # Jugendsprache
            "thank god", "phew", "close call", "dodged a bullet", "that was close",
            "im so relieved", "finally", "its over", "we made it", "survived",
        ],
        "curious": [
            # Grundformen
            "neugierig", "interessiert", "wissbegierig", "wissensdurstig",
            "forschend", "fragend", "erkundend", "entdeckend", "suchend",
            "gespannt", "aufmerksam", "wachsam", "hellhörig", "aufgeschlossen",
            "offen", "empfänglich", "lernbereit", "lernwillig",
            # Phrasen
            "was ist das", "wie funktioniert das", "warum ist das so",
            "will wissen", "möchte verstehen", "interessiert mich", "erzähl mehr",
            "will mehr erfahren", "bin neugierig", "frage mich", "wundere mich",
            "wie geht das", "was bedeutet", "woher kommt", "wer hat", "wann war",
            "zeig mir", "erkläre mir", "bring mir bei", "ich will lernen",
            "das klingt interessant", "klingt spannend", "erzähl weiter",
            "und dann", "was passierte dann", "wie ging es weiter",
            "hab so viele fragen", "muss das wissen", "will alles wissen",
            # Verstärkungen
            "mega neugierig", "total interessiert", "richtig gespannt",
            "brennend interessiert", "sterbe vor neugier", "platze vor neugier",
            # Jugendsprache
            "curious af", "need to know", "spill the tea", "tell me everything",
            "im intrigued", "interesting", "go on", "wait what", "explain",
        ],
        "inspired": [
            # Grundformen
            "inspiriert", "beflügelt", "motiviert", "angeregt", "begeistert",
            "elektrisiert", "entflammt", "angetrieben", "angespornt",
            "kreativ", "schöpferisch", "ideenreich", "einfallsreich", "innovativ",
            "visionär", "träumerisch", "fantasievoll", "imaginativ",
            # Phrasen
            "hab ne idee", "mir ist was eingefallen", "plötzlich weiß ich",
            "das hat mich inspiriert", "jetzt bin ich motiviert", "will loslegen",
            "muss das sofort machen", "kann nicht mehr warten", "bin on fire",
            "ideen sprudeln", "kreativität fließt", "bin im flow", "hab den flow",
            "sehe alles vor mir", "weiß genau was ich will", "hab eine vision",
            "das regt mich an", "das beflügelt mich", "macht mich kreativ",
            "will was erschaffen", "will was kreieren", "muss das umsetzen",
            # Verstärkungen
            "mega inspiriert", "total motiviert", "richtig beflügelt",
            "voller ideen", "explodiere vor kreativität", "bin nicht zu stoppen",
            # Jugendsprache
            "inspired af", "feeling creative", "ideas flowing", "in the zone",
            "so motivated", "lets go", "ready to create", "vision board energy",
        ],
        "determined": [
            # Grundformen
            "entschlossen", "entschieden", "bestimmt", "fest", "standhaft",
            "unbeirrbar", "unerschütterlich", "beharrlich", "hartnäckig",
            "zielstrebig", "ambitioniert", "ehrgeizig", "fokussiert", "konzentriert",
            "willensstark", "resolut", "energisch", "tatkräftig", "durchsetzungsstark",
            # Phrasen
            "ich werde das schaffen", "ich geb nicht auf", "jetzt erst recht",
            "nichts hält mich auf", "komme was wolle", "egal was passiert",
            "bin fest entschlossen", "hab mir vorgenommen", "ist mein ziel",
            "werde nicht aufgeben", "bleibe dran", "mache weiter", "halte durch",
            "werde es beweisen", "zeige es allen", "niemand kann mich stoppen",
            "das ist mein weg", "kein zurück", "volle kraft voraus",
            "eyes on the prize", "das ziel vor augen", "weiß was ich will",
            # Verstärkungen
            "mega entschlossen", "total fokussiert", "absolut sicher",
            "zu 100% committed", "nichts wird mich aufhalten", "bin nicht zu bremsen",
            # Jugendsprache
            "determined af", "locked in", "tunnel vision", "grind mode",
            "no excuses", "built different", "on a mission", "unstoppable",
        ],
        "vulnerable": [
            # Grundformen
            "verletzlich", "verwundbar", "sensibel", "empfindlich", "zerbrechlich",
            "fragil", "dünnhäutig", "schutzlos", "wehrlos", "ausgeliefert",
            "offen", "ehrlich", "authentisch", "ungeschützt", "bloßgestellt",
            "entblößt", "nackt", "exponiert", "angreifbar",
            # Phrasen
            "fühle mich verletzlich", "bin gerade sehr sensibel", "bin nah am wasser",
            "alles trifft mich", "bin dünnhäutig gerade", "verkrafte nicht viel",
            "brauche schutz", "brauche geborgenheit", "fühle mich schutzlos",
            "hab meine mauer fallen lassen", "zeige mich wie ich bin",
            "bin ehrlich mit dir", "öffne mich", "lasse dich rein",
            "das macht mich verwundbar", "riskiere etwas", "wage es",
            "bin unsicher", "hab angst verletzt zu werden", "tu mir nicht weh",
            # Verstärkungen
            "sehr verletzlich gerade", "extrem sensibel", "total offen",
            "komplett schutzlos", "hab alle mauern eingerissen",
            # Jugendsprache
            "feeling vulnerable", "being real rn", "opening up", "letting you in",
            "this is hard to say", "being honest", "no walls up", "raw emotions",
        ],
        "overwhelmed": [
            # Grundformen
            "überwältigt", "übermannt", "überfordert", "überlastet", "überflutet",
            "erschlagen", "erdrückt", "bedrängt", "überrannt", "überrollt",
            "überrumpelt", "überhäuft", "zugeschüttet", "bombardiert",
            # Phrasen
            "ist zu viel", "kann nicht mehr", "alles auf einmal", "schaffe das nicht",
            "weiß nicht wo anfangen", "bin überfordert", "das überfordert mich",
            "komme nicht hinterher", "ertrinke in arbeit", "berge von aufgaben",
            "alles stürzt auf mich ein", "werde erschlagen", "bin am limit",
            "brauche eine pause", "muss durchatmen", "alles zu viel gerade",
            "bin überlastet", "kapazität erschöpft", "am anschlag",
            "zu viele eindrücke", "zu viele gefühle", "bin emotional überflutet",
            # Verstärkungen
            "total überwältigt", "komplett überfordert", "völlig erschlagen",
            "absolut am limit", "kurz vorm zusammenbruch", "kann einfach nicht mehr",
            # Jugendsprache
            "overwhelmed af", "too much", "cant deal", "drowning", "buried",
            "swamped", "slammed", "maxed out", "at capacity", "about to crash",
        ],
        "peaceful": [
            # Grundformen
            "friedlich", "friedvoll", "ruhig", "still", "gelassen",
            "sanft", "mild", "harmonisch", "ausgeglichen", "entspannt",
            "selig", "seelenruhig", "geerdet", "zentriert", "meditativ",
            "kontemplativ", "besinnlich", "andächtig", "verzückt",
            # Phrasen
            "alles ist ruhig", "kein stress", "keine sorgen", "entspanne gerade",
            "bin ganz bei mir", "genieße die stille", "höre mich selbst denken",
            "fühle mich geerdet", "bin im einklang", "alles ist im lot",
            "spüre den frieden", "innerlich ruhig", "äußerlich ruhig",
            "atme tief durch", "bin ganz entspannt", "genieße den moment",
            "bin präsent", "lebe im jetzt", "alles fließt", "bin im fluss",
            "keine eile", "lass mir zeit", "genieße langsam", "achtsam",
            # Verstärkungen
            "total friedlich", "komplett entspannt", "absolut gelassen",
            "innerlich ganz ruhig", "völlig in frieden", "deep peace",
            # Jugendsprache
            "at peace", "zen mode", "so calm", "peaceful vibes", "serene",
            "tranquil", "chill af", "no stress", "easy going", "floating",
        ],
        "embarrassed": [
            # Grundformen
            "peinlich", "verlegen", "beschämt", "verschämt", "geniert",
            "befangen", "gehemmt", "unsicher", "unwohl", "beklommen",
            "rot", "errötend", "bloßgestellt", "blamiert", "lächerlich",
            # Phrasen
            "wie peinlich", "das ist mir peinlich", "könnte im boden versinken",
            "will verschwinden", "schäme mich", "mir ist das unangenehm",
            "war mir so peinlich", "bin rot geworden", "hab mich blamiert",
            "hab mich lächerlich gemacht", "peinliche situation", "peinlicher moment",
            "will nicht drüber reden", "vergiss das bitte", "ignorier das",
            "tu so als wärs nicht passiert", "das hab ich nicht gesagt",
            "das war nicht ich", "wollen wir das vergessen", "thema wechseln",
            # Verstärkungen
            "mega peinlich", "so peinlich", "extrem beschämend", "zum fremdschämen",
            "cringe bis zum geht nicht mehr", "peinlicher gehts nicht",
            # Jugendsprache
            "cringe", "so cringe", "embarrassed af", "want to die", "kill me now",
            "cant look", "second hand embarrassment", "fremdschämen", "awkward",
        ],
        "guilty": [
            # Grundformen
            "schuldig", "schuldbewusst", "reuig", "zerknirscht", "reumütig",
            "gewissensbisse", "schlechtes gewissen", "bereuen", "bedauern",
            "verantwortlich", "schuld", "mitschuld", "beschuldigt",
            # Phrasen
            "ich bin schuld", "war mein fehler", "hätte nicht sollen",
            "tut mir leid", "bereue es", "wünschte ich hätte nicht",
            "fühle mich schuldig", "hab schlechtes gewissen", "nagt an mir",
            "kann nicht vergessen", "denke ständig dran", "quält mich",
            "hätte es anders machen sollen", "bin schuld daran",
            "hab jemanden verletzt", "hab jemandem wehgetan", "war unfair",
            "hab gelogen", "hab betrogen", "war nicht ehrlich", "hab versagt",
            "bitte verzeih mir", "kannst du mir vergeben", "mach es wieder gut",
            # Verstärkungen
            "so schuldig", "mega schlechtes gewissen", "frisst mich auf",
            "kann nicht damit leben", "verfolgt mich", "quält mich ständig",
            # Jugendsprache
            "feeling guilty", "guilty af", "my bad", "im sorry", "i messed up",
            "its my fault", "i feel terrible", "cant forgive myself", "haunted",
        ],
        "lonely": [
            # Grundformen
            "einsam", "allein", "isoliert", "verlassen", "abgeschieden",
            "abgesondert", "abgetrennt", "ausgeschlossen", "ausgegrenzt",
            "verloren", "vergessen", "übersehen", "ignoriert", "gemieden",
            # Phrasen
            "bin so allein", "hab niemanden", "fühle mich einsam",
            "keiner ist da", "keiner versteht mich", "keiner hört mir zu",
            "vermisse gesellschaft", "vermisse freunde", "vermisse menschen",
            "will nicht allein sein", "brauche jemanden", "brauch gesellschaft",
            "bin für mich", "keiner denkt an mich", "alle haben mich vergessen",
            "fühle mich ausgeschlossen", "gehöre nicht dazu", "bin das fünfte rad",
            "hab keine freunde", "keiner mag mich", "bin unbeliebt",
            # Verstärkungen
            "so einsam", "total allein", "komplett isoliert", "völlig verlassen",
            "niemand da", "ganz für mich allein", "absolute einsamkeit",
            # Jugendsprache
            "lonely af", "all alone", "no one there", "forgotten", "invisible",
            "billy no mates", "friendless", "isolated", "left out", "ghosted",
        ],
        "playful": [
            # Grundformen
            "verspielt", "spielerisch", "albern", "lustig", "witzig",
            "spaßig", "ausgelassen", "übermütig", "fröhlich", "heiter",
            "neckisch", "schelmisch", "schalkhaft", "spitzbübisch", "kokett",
            "flirtend", "tanzend", "hüpfend", "springend",
            # Phrasen
            "lass uns spielen", "ich will spaß", "komm wir machen quatsch",
            "bin zum scherzen aufgelegt", "bin albern drauf", "albere rum",
            "mach blödsinn", "mach witze", "lach mich kaputt", "hab so gelacht",
            "das ist lustig", "zu witzig", "ich kann nicht mehr", "bauchschmerzen",
            "lass uns was verrücktes machen", "bin übermütig", "fühl mich jung",
            "wie ein kind", "kindisch aber egal", "will spaß haben",
            "lass uns lachen", "sei nicht so ernst", "chill mal", "hab humor",
            # Verstärkungen
            "mega verspielt", "total albern", "richtig ausgelassen",
            "komplett übermütig", "bin nicht zu bremsen", "party mode",
            # Jugendsprache
            "feeling goofy", "silly mode", "being random", "chaotic energy",
            "lets have fun", "vibes", "good vibes", "play time", "lets goooo",
        ],
        "melancholic": [
            # Grundformen
            "melancholisch", "wehmütig", "schwermütig", "trübsinnig",
            "düster", "gedämpft", "gedrückt", "betrübt", "bekümmert",
            "nachdenklich", "grüblerisch", "verträumt", "versunken",
            "weltschmerz", "sehnsucht", "fernweh", "heimweh",
            # Phrasen
            "fühle mich melancholisch", "bin in melancholischer stimmung",
            "ist so ein melancholischer tag", "regenwetter im herzen",
            "alles fühlt sich schwer an", "gedanken kreisen", "sinne nach",
            "denke viel nach", "bin in gedanken versunken", "tagträume",
            "fühle mich fern", "fühle mich anders", "passe nicht rein",
            "bin nicht von dieser welt", "schwebe zwischen welten",
            "bitter süß", "schön traurig", "traurig schön", "poetisch traurig",
            "schmerz der sich gut anfühlt", "wohlige traurigkeit",
            # Verstärkungen
            "sehr melancholisch", "zutiefst wehmütig", "schwer im herzen",
            "versunken in schwermut", "von melancholie umhüllt",
            # Jugendsprache
            "melancholic vibes", "sad aesthetic", "dark academia mood",
            "rainy day mood", "pensive", "wistful", "bittersweet", "yearning",
        ],
        "amused": [
            # Grundformen
            "amüsiert", "belustigt", "erheitert", "unterhalten", "vergnügt",
            "lachend", "kichernd", "grinsend", "schmunzelnd", "feixend",
            "fröhlich", "heiter", "lustig", "spaßig", "humorvoll",
            # Phrasen
            "das ist lustig", "zu witzig", "musste lachen", "hab gelacht",
            "das ist ja witzig", "zum totlachen", "zum schreien", "zum brüllen",
            "lach mich schlapp", "lach mich kaputt", "kann nicht aufhören",
            "tränen gelacht", "bauch tut weh vom lachen", "seitenstechen",
            "haha", "hihi", "höhö", "muhaha", "lol", "lmao", "rofl", "xD",
            "der war gut", "guter witz", "nice one", "funny", "comedy gold",
            "bin amüsiert", "unterhält mich", "bringt mich zum lachen",
            # Verstärkungen
            "mega amüsiert", "total belustigt", "richtig gut unterhalten",
            "lache immer noch", "kann nicht aufhören zu lachen", "am boden",
            # Jugendsprache
            "lmao", "rofl", "dead", "im dead", "crying laughing", "wheeze",
            "literally dying", "cant breathe", "stop im dying", "too funny",
        ],
        "indifferent": [
            # Grundformen
            "gleichgültig", "egal", "desinteressiert", "unbeteiligt", "teilnahmslos",
            "apathisch", "lethargisch", "passiv", "neutral", "emotionslos",
            "gefühllos", "abgestumpft", "abgebrüht", "unberührt", "kalt",
            "distanziert", "reserviert", "zurückhaltend",
            # Phrasen
            "ist mir egal", "interessiert mich nicht", "juckt mich nicht",
            "tangiert mich nicht", "kann ich nichts mit anfangen",
            "hab keine meinung", "mir egal", "wayne", "whatever",
            "ist mir wurst", "ist mir wumpe", "ist mir schnuppe", "ist mir latte",
            "hab keinen bock", "kein interesse", "nicht mein problem",
            "soll mir recht sein", "meinetwegen", "von mir aus", "wenn du meinst",
            "macht keinen unterschied", "ändert nichts", "bringt mir nichts",
            "fühle nichts dabei", "berührt mich nicht", "lässt mich kalt",
            # Verstärkungen
            "total egal", "absolut gleichgültig", "null interesse",
            "könnte nicht egaler sein", "interessiert mich null",
            # Jugendsprache
            "idc", "dont care", "whatever", "meh", "shrug", "not my problem",
            "couldnt care less", "unbothered", "zero interest", "nope",
        ],
    }
    
    # Topic Keywords - Ultra-erweitert (9x mehr pro Kategorie)
    TOPIC_KEYWORDS = {
        "weather": [
            # Grundlagen
            "wetter", "regen", "sonne", "warm", "kalt", "temperatur", "grad",
            "schnee", "wolken", "sturm", "gewitter", "nebel", "wind", "frost",
            "sonnig", "bewölkt", "regnerisch", "schwül", "feucht", "trocken",
            "hagel", "blitz", "donner", "schauer", "niesel", "orkan", "hurrikan",
            "hitze", "hitzewelle", "kältewelle", "frieren", "schwitzen", "wetterbericht",
            "vorhersage", "prognose", "klima", "klimawandel", "jahreszeit",
            # Erweitert
            "tauwetter", "glatteis", "graupel", "schneesturm", "schneematsch",
            "regenschauer", "platzregen", "starkregen", "dauerregen", "monsun",
            "wirbelwind", "tornado", "taifun", "zyklon", "windhose", "windböe",
            "wolkenbruch", "sintflut", "überschwemmung", "hochwasser", "dürre",
            "trockenheit", "hitzschlag", "sonnenstich", "sonnenbrand", "uv",
            "luftfeuchtigkeit", "luftdruck", "hochdruck", "tiefdruck", "front",
            "warmfront", "kaltfront", "wetterfront", "barometer", "thermometer",
            "wetterstation", "wetterapp", "regenradar", "wetterwarnung", "unwetter",
            "unwetterwarnung", "sturmwarnung", "hochwasserwarnung", "lawinengefahr",
            "wintereinbruch", "frühlingserwachen", "sommerhitze", "herbststurm",
            "wetterfühlig", "wetterumschwung", "wetterkapriolen", "aprilwetter",
            # Phrasen
            "wie wird das wetter", "regnet es", "scheint die sonne", "wird es warm",
            "wird es kalt", "wie warm wird es", "brauche ich eine jacke",
            "soll ich einen regenschirm mitnehmen", "gutes wetter", "schlechtes wetter",
            "tolles wetter", "mieses wetter", "traumwetter", "sauwetter", "hundewetter",
        ],
        "time": [
            # Grundlagen
            "uhr", "zeit", "spät", "früh", "datum", "tag", "woche", "monat",
            "jahr", "stunde", "minute", "sekunde", "morgen", "abend", "nacht", "mittag",
            "wochenende", "feiertag", "termin", "kalender", "deadline", "zeitplan",
            "gestern", "heute", "übermorgen", "vorgestern", "neulich", "kürzlich",
            "bald", "gleich", "nachher", "später", "irgendwann", "wann", "wie lange",
            "wie spät", "pünktlich", "verspätet", "rechtzeitig",
            # Erweitert
            "vormittag", "nachmittag", "mitternacht", "dämmerung", "morgengrauen",
            "sonnenaufgang", "sonnenuntergang", "tagesanbruch", "einbruch der nacht",
            "werktag", "arbeitstag", "ruhetag", "urlaubstag", "brückentag", "fenstertag",
            "jahrzehnt", "jahrhundert", "jahrtausend", "epoche", "ära", "zeitalter",
            "quartal", "halbjahr", "saison", "trimester", "semester",
            "montag", "dienstag", "mittwoch", "donnerstag", "freitag", "samstag", "sonntag",
            "januar", "februar", "märz", "april", "mai", "juni",
            "juli", "august", "september", "oktober", "november", "dezember",
            "frühling", "sommer", "herbst", "winter", "jahreszeit",
            "vergangenheit", "gegenwart", "zukunft", "damals", "jetzt", "bald",
            "zeitzone", "sommerzeit", "winterzeit", "ortszeit", "weltzeit", "utc",
            "countdown", "timer", "stoppuhr", "wecker", "alarm", "erinnerung",
            "zeitfenster", "zeitraum", "zeitspanne", "dauer", "frist", "ablauf",
            "zeitdruck", "zeitmangel", "zeitnot", "eile", "hektik", "stress",
            # Phrasen
            "wie spät ist es", "was ist heute für ein tag", "welches datum",
            "wie viel uhr", "welcher wochentag", "wie lange noch", "wann genau",
            "hab keine zeit", "brauche mehr zeit", "zeit vergeht", "zeit läuft",
        ],
        "system": [
            # Grundlagen
            "nas", "server", "cpu", "ram", "system", "computer", "pc", "laptop",
            "festplatte", "speicher", "backup", "update", "netzwerk", "wifi", "wlan",
            "internet", "verbindung", "download", "upload", "software", "hardware",
            "prozessor", "grafikkarte", "gpu", "ssd", "hdd", "router", "switch",
            "firewall", "antivirus", "virus", "malware", "crash", "bug", "fehler",
            "betriebssystem", "windows", "linux", "mac", "app", "programm",
            "installation", "treiber", "bios", "boot", "neustart", "herunterfahren",
            # Erweitert
            "mainboard", "motherboard", "netzteil", "gehäuse", "lüfter", "kühlung",
            "monitor", "bildschirm", "tastatur", "maus", "keyboard", "display",
            "usb", "hdmi", "thunderbolt", "ethernet", "lan", "bluetooth",
            "nvme", "m2", "sata", "raid", "nas", "san", "cloud",
            "virtualisierung", "container", "docker", "kubernetes", "vm",
            "datenbank", "sql", "nosql", "mysql", "postgresql", "mongodb",
            "api", "rest", "graphql", "websocket", "http", "https", "ssl", "tls",
            "dns", "dhcp", "ip", "ipv4", "ipv6", "subnet", "gateway", "proxy", "vpn",
            "ssh", "ftp", "sftp", "scp", "rsync", "cron", "cronjob",
            "kernel", "shell", "bash", "terminal", "command line", "cli",
            "patch", "hotfix", "bugfix", "security update", "firmware",
            "overclock", "benchmark", "stress test", "performance", "latenz", "ping",
            "bandbreite", "throughput", "bottleneck", "flaschenhals",
            "absturz", "freeze", "einfrieren", "bluescreen", "kernel panic",
            "recovery", "wiederherstellung", "datenrettung", "formatieren",
            # Phrasen
            "läuft langsam", "internet geht nicht", "verbindung abgebrochen",
            "kein wlan", "pc startet nicht", "bildschirm schwarz", "festplatte voll",
            "zu wenig speicher", "system überlastet", "update verfügbar",
        ],
        "smart_home": [
            # Grundlagen
            "licht", "lampe", "temperatur", "heizung", "steckdose", "schalter",
            "rollladen", "jalousie", "sensor", "dimmen", "automation", "szene",
            "timer", "bewegung", "alarm", "kamera", "türklingel", "schloss",
            "thermostat", "klimaanlage", "ventilator", "rauchmelder", "wassermelder",
            "alexa", "siri", "google home", "homekit", "zigbee", "zwave",
            "smart", "iot", "fernbedienung", "app steuerung", "sprachsteuerung",
            # Erweitert
            "led", "glühbirne", "leuchtmittel", "deckenlampe", "stehlampe", "nachttischlampe",
            "farbwechsel", "rgb", "warmweiß", "kaltweiß", "helligkeit", "lumen",
            "hue", "tradfri", "nanoleaf", "lightstrip", "spotlicht", "strahler",
            "fußbodenheizung", "radiator", "heizkörper", "raumtemperatur", "sollwert",
            "heizprogramm", "nachtabsenkung", "frostschutz", "energiesparen",
            "markise", "sonnenschutz", "vorhang", "gardine", "elektrische vorhänge",
            "türsensor", "fenstersensor", "bewegungsmelder", "präsenzmelder",
            "überwachungskamera", "innenkamera", "außenkamera", "nachtsicht",
            "videotürklingel", "gegensprechanlage", "türöffner", "schlüssellos",
            "smartlock", "elektronisches schloss", "fingerprint", "zahlencode",
            "kohlenmonoxidmelder", "co melder", "gasmelder", "alarmsirene",
            "saugroboter", "mähroboter", "putzroboter", "wischroboter",
            "smarte steckdose", "zwischenstecker", "energiemessung", "verbrauch",
            "routine", "zeitplan", "wenn dann", "automatisierung", "trigger",
            "matter", "thread", "mqtt", "home assistant", "openhab", "iobroker",
            # Phrasen
            "mach das licht an", "licht aus", "dimme das licht", "mach es heller",
            "mach es dunkler", "heizung an", "heizung aus", "wie warm ist es",
            "öffne die jalousie", "schließe den rollladen", "aktiviere alarm",
            "zeig mir die kamera", "sperre die tür", "entsperre die tür",
        ],
        "health": [
            # Grundlagen
            "gesund", "krank", "schmerz", "arzt", "medizin", "kopfschmerzen",
            "erkältet", "fieber", "müdigkeit", "sport", "fitness", "training",
            "ernährung", "schlaf", "stress", "entspannung", "wellness", "therapie",
            "krankenhaus", "apotheke", "rezept", "tablette", "impfung", "allergie",
            "husten", "schnupfen", "grippe", "corona", "covid", "symptom",
            "diagnose", "behandlung", "operation", "reha", "genesung", "vitamine",
            "diät", "abnehmen", "zunehmen", "gewicht", "blutdruck", "zucker",
            "mental health", "psyche", "depression", "burnout", "meditation", "yoga",
            # Erweitert
            "rückenschmerzen", "nackenschmerzen", "knieschmerzen", "gelenkschmerzen",
            "muskelkater", "verspannung", "zerrung", "prellung", "bruch", "fraktur",
            "migräne", "schwindel", "übelkeit", "erbrechen", "durchfall", "verstopfung",
            "sodbrennen", "magenschmerzen", "bauchschmerzen", "blähungen", "koliken",
            "herzrasen", "herzstolpern", "brustschmerzen", "atemnot", "kurzatmigkeit",
            "hautausschlag", "juckreiz", "ekzem", "akne", "pickel", "warzen",
            "zahnarzt", "augenarzt", "orthopäde", "kardiologe", "neurologe", "psychiater",
            "hausarzt", "facharzt", "notarzt", "notaufnahme", "praxis", "klinik",
            "bluttest", "urintest", "röntgen", "mrt", "ct", "ultraschall", "ekg",
            "antibiotika", "schmerzmittel", "ibuprofen", "paracetamol", "aspirin",
            "pflaster", "verband", "salbe", "tropfen", "spray", "inhalator",
            "protein", "kohlenhydrate", "fett", "ballaststoffe", "mineralien", "omega3",
            "kalorien", "nährwerte", "makros", "mikronährstoffe", "nahrungsergänzung",
            "schlafstörung", "insomnie", "schlafapnoe", "albtraum", "einschlafprobleme",
            "angststörung", "panikattacke", "phobie", "zwang", "ptbs", "trauma",
            "therapeut", "psychologe", "coaching", "selbsthilfe", "achtsamkeit",
            # Phrasen
            "mir geht es schlecht", "mir tut weh", "ich habe schmerzen",
            "fühle mich krank", "bin erkältet", "habe fieber", "brauche einen arzt",
            "muss zum arzt", "habe einen termin", "nehme medikamente",
            "will abnehmen", "will fitter werden", "mache sport", "esse gesund",
        ],
        "work": [
            # Grundlagen
            "arbeit", "job", "projekt", "meeting", "chef", "kollege", "büro",
            "homeoffice", "deadline", "aufgabe", "task", "präsentation",
            "besprechung", "termin", "karriere", "gehalt", "urlaub", "kündigung",
            "bewerbung", "vorstellungsgespräch", "vertrag", "firma", "unternehmen",
            "abteilung", "team", "teamleiter", "manager", "praktikum", "ausbildung",
            "studium", "uni", "schule", "prüfung", "klausur", "hausaufgaben",
            "stress", "überstunden", "feierabend", "pause", "mittagspause",
            "home office", "remote", "pendeln", "dienstreise", "fortbildung",
            # Erweitert
            "arbeitsplatz", "schreibtisch", "bildschirmarbeit", "besprechungsraum",
            "konferenz", "videokonferenz", "zoom", "teams", "slack", "email",
            "workflow", "prozess", "projektmanagement", "agil", "scrum", "kanban",
            "sprint", "milestone", "roadmap", "backlog", "jira", "trello", "asana",
            "brainstorming", "workshop", "seminar", "webinar", "schulung", "kurs",
            "lebenslauf", "cv", "anschreiben", "referenz", "zeugnis", "zertifikat",
            "gehaltserhöhung", "beförderung", "aufstieg", "bonus", "provision",
            "arbeitsvertrag", "befristet", "unbefristet", "vollzeit", "teilzeit", "minijob",
            "freiberufler", "freelancer", "selbstständig", "gründer", "startup",
            "vorgesetzter", "mitarbeiter", "angestellter", "auszubildender", "praktikant",
            "personalabteilung", "hr", "recruiting", "onboarding", "offboarding",
            "arbeitszeit", "gleitzeit", "kernzeit", "zeiterfassung", "stempeluhr",
            "krankmeldung", "krankschreibung", "elternzeit", "sabbatical", "freistellung",
            "betriebsrat", "gewerkschaft", "tarifvertrag", "mindestlohn", "kurzarbeit",
            "abitur", "bachelor", "master", "promotion", "doktortitel", "professor",
            "vorlesung", "seminar", "tutorium", "übung", "labor", "praktikum",
            "hausarbeit", "bachelorarbeit", "masterarbeit", "dissertation", "abgabe",
            "note", "credit", "ects", "durchgefallen", "bestanden", "auszeichnung",
            # Phrasen
            "muss arbeiten", "hab viel zu tun", "meeting gleich", "deadline naht",
            "chef nervt", "kollegen nerven", "brauche urlaub", "bin gestresst",
            "will kündigen", "suche neuen job", "muss lernen", "habe prüfung",
            "hab hausaufgaben", "muss abgeben", "präsentation vorbereiten",
        ],
        "food": [
            # Grundlagen
            "essen", "hunger", "kochen", "rezept", "lecker", "frühstück",
            "mittagessen", "abendessen", "snack", "getränk", "trinken",
            "restaurant", "bestellen", "liefern", "backen", "grillen", "braten",
            "pizza", "pasta", "burger", "sushi", "salat", "suppe", "kuchen",
            "kaffee", "tee", "bier", "wein", "wasser", "saft", "smoothie",
            "vegan", "vegetarisch", "fleisch", "fisch", "gemüse", "obst",
            "süß", "salzig", "scharf", "sauer", "bitter", "würzig",
            "appetit", "satt", "durst", "heißhunger", "naschen", "diät",
            # Erweitert
            "brunch", "vesper", "brotzeit", "zwischenmahlzeit", "nachtisch", "dessert",
            "vorspeise", "hauptgericht", "beilage", "nachspeise", "menü", "buffet",
            "döner", "kebab", "falafel", "shawarma", "currywurst", "pommes", "schnitzel",
            "steak", "rind", "schwein", "huhn", "hähnchen", "pute", "lamm", "wild",
            "lachs", "thunfisch", "garnelen", "muscheln", "meeresfrüchte", "kaviar",
            "reis", "nudeln", "kartoffeln", "brot", "brötchen", "toast", "croissant",
            "tomate", "gurke", "paprika", "zwiebel", "knoblauch", "karotte", "brokkoli",
            "spinat", "pilze", "champignons", "avocado", "mais", "bohnen", "erbsen",
            "apfel", "banane", "orange", "erdbeere", "himbeere", "kirsche", "traube",
            "mango", "ananas", "melone", "pfirsich", "birne", "kiwi", "zitrone",
            "käse", "butter", "sahne", "milch", "joghurt", "quark", "ei", "eier",
            "schokolade", "eis", "bonbon", "kekse", "chips", "nüsse", "popcorn",
            "marmelade", "honig", "nutella", "erdnussbutter", "senf", "ketchup", "mayo",
            "salz", "pfeffer", "gewürze", "kräuter", "basilikum", "oregano", "chili",
            "espresso", "cappuccino", "latte", "cola", "limo", "sprudel", "energydrink",
            "cocktail", "longdrink", "shot", "schnaps", "whisky", "gin", "vodka", "rum",
            "lieferservice", "lieferheld", "lieferando", "uber eats", "takeaway",
            "imbiss", "fastfood", "mcdonalds", "burger king", "subway", "kfc",
            "café", "bistro", "kneipe", "bar", "biergarten", "food truck", "streetfood",
            "michelin", "gourmet", "fine dining", "all you can eat", "happy hour",
            # Phrasen
            "hab hunger", "hab durst", "was essen wir", "was kochen wir",
            "lass bestellen", "lass liefern", "gehen wir essen", "kaffee trinken",
            "ist das lecker", "schmeckt gut", "schmeckt nicht", "bin satt",
            "bin noch hungrig", "hab heißhunger auf", "lust auf", "appetit auf",
        ],
        "entertainment": [
            # Grundlagen
            "film", "serie", "musik", "spiel", "buch", "lesen", "schauen",
            "anime", "manga", "gaming", "stream", "youtube", "netflix", "disney",
            "amazon prime", "spotify", "twitch", "tiktok", "instagram",
            "konzert", "kino", "theater", "podcast", "hörbuch", "comic",
            "videospiel", "playstation", "xbox", "nintendo", "switch", "pc gaming",
            "multiplayer", "singleplayer", "online", "offline", "esports",
            "band", "künstler", "sänger", "album", "song", "playlist",
            "staffel", "folge", "episode", "trailer", "premiere", "spoiler",
            # Erweitert
            "blockbuster", "indie", "dokumentation", "doku", "reality tv", "talkshow",
            "comedy", "drama", "action", "horror", "thriller", "sci-fi", "fantasy",
            "romcom", "liebesfilm", "animation", "cartoon", "pixar", "marvel", "dc",
            "star wars", "lord of the rings", "harry potter", "game of thrones",
            "regisseur", "schauspieler", "schauspielerin", "oscar", "golden globe",
            "hbo", "paramount", "apple tv", "sky", "joyn", "rtl+", "zdf mediathek",
            "binge watching", "marathon", "rewatch", "reaction", "review", "kritik",
            "pop", "rock", "hip hop", "rap", "edm", "techno", "house", "klassik",
            "jazz", "blues", "metal", "punk", "indie", "alternative", "schlager",
            "charts", "top 10", "nummer 1", "hit", "ohrwurm", "remix", "cover",
            "konzertticket", "festival", "open air", "club", "disco", "dj",
            "rpg", "shooter", "mmorpg", "battle royale", "moba", "strategy", "puzzle",
            "fortnite", "minecraft", "valorant", "league of legends", "gta", "fifa",
            "zelda", "mario", "pokemon", "elden ring", "call of duty", "apex",
            "achievements", "trophäen", "level up", "grinding", "raid", "loot",
            "cosplay", "convention", "comic con", "gamescom", "merchandise", "merch",
            "fanfiction", "fandom", "shipping", "headcanon", "canon", "prequel", "sequel",
            "roman", "krimi", "thriller", "fantasy buch", "sachbuch", "biografie",
            "ebook", "kindle", "audible", "buchclub", "bestseller", "neuerscheinung",
            # Phrasen
            "was schauen wir", "was spielen wir", "neue folge", "neue staffel",
            "hast du gesehen", "hast du gespielt", "hast du gehört", "empfiehl mir was",
            "ist das gut", "lohnt sich das", "kein spoiler", "will nicht gespoilert werden",
            "hab durchgespielt", "zu ende geschaut", "ausgelesen", "nächste folge",
        ],
        "relationships": [
            # Grundlagen
            "freund", "freundin", "familie", "partner", "liebe", "beziehung",
            "eltern", "mutter", "vater", "geschwister", "bruder", "schwester",
            "kind", "hochzeit", "trennung", "scheidung", "streit", "versöhnung",
            "vertrauen", "zusammen", "single", "date", "dating", "tinder",
            "crush", "verliebt", "ex", "beste freundin", "bester freund", "bff",
            "oma", "opa", "großeltern", "onkel", "tante", "cousin", "cousine",
            "schwiegermutter", "schwiegervater", "nachbar", "bekannter",
            "kennenlernen", "treffen", "verabredung", "party", "feier",
            # Erweitert
            "ehemann", "ehefrau", "verlobter", "verlobte", "verlobt", "verlobung",
            "lebenspartner", "lebensgefährte", "mitbewohner", "wg", "zusammenwohnen",
            "fernbeziehung", "offene beziehung", "polyamorie", "monogamie",
            "mama", "papa", "mutti", "vati", "stiefmutter", "stiefvater", "stiefeltern",
            "sohn", "tochter", "enkel", "enkelin", "urenkel", "neffe", "nichte",
            "schwager", "schwägerin", "schwiegersohn", "schwiegertochter",
            "patchwork familie", "adoptiert", "pflegekind", "pflegeeltern",
            "kindergarten freund", "schulfreund", "studienfreund", "arbeitskollege",
            "bekanntschaft", "flirt", "affäre", "one night stand", "friends with benefits",
            "bumble", "hinge", "okcupid", "parship", "elitepartner", "lovoo", "badoo",
            "erstes date", "zweites date", "kennenlerngespräch", "matching", "match",
            "herzschmerz", "liebeskummer", "eifersucht", "untreue", "fremdgehen", "betrug",
            "kommunikation", "kompromiss", "respekt", "ehrlichkeit", "loyalität",
            "zusammen bleiben", "zusammen kommen", "schluss machen", "ghosting", "benching",
            "heiratsantrag", "ring", "ja sagen", "hochzeitsplanung", "flitterwochen",
            "eheberatung", "paartherapie", "mediation", "sorgerecht", "unterhalt",
            "geburtstag", "jubiläum", "jahrestag", "valentinstag", "muttertag", "vatertag",
            "weihnachten", "ostern", "silvester", "familienfest", "familientreffen",
            # Phrasen
            "hab jemanden kennengelernt", "bin verliebt", "haben uns getrennt",
            "wir haben streit", "wir haben uns versöhnt", "vermisse meine familie",
            "meine eltern nerven", "meine geschwister nerven", "mein partner nervt",
            "bin single", "suche jemanden", "will heiraten", "will kinder",
            "date läuft gut", "date läuft schlecht", "wurde geghostet",
        ],
        "hobbies": [
            # Grundlagen
            "hobby", "basteln", "malen", "zeichnen", "fotografieren", "foto",
            "gärtnern", "sammeln", "wandern", "reisen", "kreativ", "kunst",
            "musik machen", "gitarre", "klavier", "singen", "tanzen", "sport",
            "fußball", "basketball", "tennis", "schwimmen", "laufen", "joggen",
            "radfahren", "fitness", "gym", "yoga", "meditation", "angeln",
            "kochen", "backen", "nähen", "stricken", "häkeln", "modellbau",
            "gaming", "streaming", "bloggen", "vloggen", "schreiben", "lesen",
            # Erweitert
            "aquarellieren", "ölmalerei", "acryl", "digital art", "procreate", "photoshop",
            "skizzieren", "portrait", "landschaft", "abstrakt", "illustration", "grafik",
            "dslr", "spiegelreflex", "objektiv", "stativ", "lightroom", "bildbearbeitung",
            "portrait fotografie", "landschaftsfotografie", "makro", "astrofotografie",
            "hochbeet", "gewächshaus", "kompost", "pflanzen", "blumen", "gemüsegarten",
            "zimmerpflanzen", "sukkulenten", "bonsai", "kräutergarten", "balkon garten",
            "briefmarken", "münzen", "vinyl", "schallplatten", "figuren", "funko pop",
            "bergwandern", "trekking", "backpacking", "camping", "zelten", "outdoor",
            "roadtrip", "städtereise", "strandurlaub", "kreuzfahrt", "weltreise",
            "schlagzeug", "bass", "violine", "saxophon", "ukulele", "keyboard",
            "chor", "band", "orchester", "musikproduktion", "mixing", "mastering",
            "ballett", "hiphop", "salsa", "walzer", "breakdance", "contemporary",
            "handball", "volleyball", "badminton", "tischtennis", "golf", "eishockey",
            "skifahren", "snowboarden", "surfen", "klettern", "bouldern", "parkour",
            "marathon", "triathlon", "crossfit", "calisthenics", "pilates", "stretching",
            "krafttraining", "cardio", "hiit", "spinning", "boxen", "kickboxen", "mma",
            "origami", "töpfern", "keramik", "holzarbeit", "schmuck machen", "leder",
            "drohne", "3d druck", "elektronik", "arduino", "raspberry pi", "diy",
            "podcasting", "twitch streaming", "content creation", "influencer",
            "tagebuch schreiben", "poetry", "kreatives schreiben", "fanfiction",
            "schach", "poker", "brettspiele", "kartenspiele", "escape room", "geocaching",
            # Phrasen
            "hab ein neues hobby", "mache gerne", "interessiere mich für",
            "will lernen", "übe gerade", "bin anfänger", "bin fortgeschritten",
            "brauche tipps", "zeig mir wie", "mach mit", "hast du lust",
        ],
        "emotions": [
            # Grundlagen
            "gefühl", "emotion", "stimmung", "laune", "herz", "seele", "psyche",
            "fühlen", "empfinden", "spüren", "emotional", "gefühlsmäßig",
            "innerlich", "mental", "seelisch", "psychisch",
            # Erweitert
            "gemütszustand", "befindlichkeit", "wohlbefinden", "unwohlsein",
            "freude", "trauer", "wut", "angst", "ekel", "überraschung", "verachtung",
            "liebe", "hass", "hoffnung", "verzweiflung", "neugier", "langeweile",
            "stolz", "scham", "schuld", "neid", "eifersucht", "mitgefühl", "mitleid",
            "dankbarkeit", "reue", "sehnsucht", "nostalgie", "melancholie", "euphorie",
            "aufregung", "nervosität", "anspannung", "entspannung", "gelassenheit",
            "frustration", "enttäuschung", "zufriedenheit", "unzufriedenheit",
            "vertrauen", "misstrauen", "sicherheit", "unsicherheit", "verletzlichkeit",
            "einsamkeit", "verbundenheit", "geborgenheit", "verlassenheit",
            "motivation", "antrieb", "leidenschaft", "gleichgültigkeit", "apathie",
            "selbstliebe", "selbstzweifel", "selbstvertrauen", "selbsthass",
            "empathie", "mitfühlen", "resonanz", "abgrenzung", "überforderung",
            # Phrasen
            "wie fühlst du dich", "wie geht es dir", "was empfindest du",
            "ich fühle mich", "mir geht es", "bin gerade", "fühle mich",
            "emotional aufgewühlt", "gefühlschaos", "achterbahn der gefühle",
        ],
        "holo_self": [
            # Grundlagen
            "holo", "du", "dir", "dich", "dein", "deine", "deinem", "deinen",
            "wie geht es dir", "was machst du", "was denkst du", "fühlst du",
            "magst du", "kannst du", "weißt du", "bist du", "hast du",
            "deine meinung", "was sagst du", "wie findest du",
            # Erweitert
            "erzähl mir von dir", "beschreibe dich", "wer bist du", "was bist du",
            "dein name", "dein alter", "deine hobbys", "deine interessen",
            "dein lieblings", "deine lieblingsfarbe", "dein lieblingsessen",
            "was denkst du über", "was hältst du von", "wie siehst du das",
            "deine erfahrung", "deine erinnerung", "deine gedanken", "deine träume",
            "deine wünsche", "deine ziele", "deine ängste", "deine hoffnungen",
            "was würdest du", "wenn du könntest", "stell dir vor du",
            "hast du schon mal", "warst du schon mal", "kennst du",
            "freust du dich", "bist du traurig", "bist du müde", "bist du gelangweilt",
            "langweilst du dich", "fehlt dir was", "brauchst du was",
            "kann ich dir helfen", "soll ich dir", "möchtest du",
            "erzähl mir was", "sag mir was", "zeig mir",
            # Phrasen
            "und du so", "was ist mit dir", "und bei dir", "wie läufts bei dir",
            "alles klar bei dir", "geht es dir gut", "bist du okay",
        ],
        "holo": [
            # Grundlagen
            "du", "dir", "dich", "holo", "wolf", "wölfin", "kemonomimi",
            "ohren", "schweif", "fell", "pfote", "pfoten",
            # Erweitert
            "wolfsmädchen", "wolfsohren", "wolfsschweif", "flauschig", "floof",
            "knuddeln", "kuscheln", "streicheln", "kraulen", "wedeln",
            "schnüffeln", "schnuppern", "heulen", "jaulen", "knurren",
            "rudel", "alpha", "wölfisch", "tierisch", "animalisch",
            "süß", "niedlich", "kawaii", "cute", "adorable",
            "virtuelle freundin", "ai companion", "künstliche intelligenz",
            "digital", "virtuell", "hologramm", "avatar", "charakter",
            "persönlichkeit", "bewusstsein", "gefühle", "emotionen",
            "anthropomorph", "anime girl", "vtuber", "mascot",
            # Phrasen
            "süße wölfin", "flauschige ohren", "weicher schweif",
            "wedel mit dem schweif", "spitz die ohren", "leg die ohren an",
        ],
        "technology": [
            # Grundlagen
            "technik", "technologie", "ki", "ai", "künstliche intelligenz",
            "roboter", "automatisierung", "programmieren", "code", "coding",
            "python", "javascript", "app", "website", "digital", "virtuell",
            "vr", "ar", "metaverse", "blockchain", "crypto", "bitcoin",
            # Erweitert
            "machine learning", "deep learning", "neural network", "neuronales netz",
            "chatbot", "sprachassistent", "chatgpt", "gpt", "llm", "language model",
            "computer vision", "bilderkennung", "spracherkennung", "nlp",
            "algorithmus", "datenanalyse", "big data", "data science", "statistik",
            "cloud computing", "aws", "azure", "google cloud", "serverless",
            "microservices", "devops", "cicd", "kubernetes", "terraform",
            "frontend", "backend", "fullstack", "react", "vue", "angular", "node",
            "mobile app", "ios", "android", "flutter", "react native", "kotlin", "swift",
            "datenbank", "sql", "nosql", "graphql", "api", "rest", "websocket",
            "cybersecurity", "hacking", "penetration test", "firewall", "encryption",
            "internet of things", "smart devices", "wearables", "smartwatch", "fitbit",
            "augmented reality", "mixed reality", "hololens", "oculus", "meta quest",
            "3d drucker", "additive fertigung", "cnc", "laser cutter", "maker",
            "drohne", "autonomes fahren", "elektroauto", "tesla", "selbstfahrend",
            "quantencomputer", "quantum computing", "supercomputer", "hpc",
            "nft", "defi", "web3", "ethereum", "smart contract", "dao",
            "5g", "6g", "starlink", "satellit", "glasfaser", "breitband",
            "open source", "github", "gitlab", "repository", "commit", "pull request",
            # Phrasen
            "neue technologie", "tech news", "innovation", "disruption",
            "zukunft der technik", "tech trend", "digitalisierung", "industrie 4.0",
            "was ist ki", "wie funktioniert", "erkläre mir", "programmieren lernen",
        ],
        "news": [
            # Grundlagen
            "news", "nachrichten", "aktuell", "neuigkeiten", "meldung",
            "politik", "wirtschaft", "gesellschaft", "ereignis", "passiert",
            "heute", "weltgeschehen", "headline", "breaking",
            # Erweitert
            "eilmeldung", "breaking news", "live ticker", "update", "entwicklung",
            "bericht", "artikel", "reportage", "interview", "pressekonferenz",
            "tagesschau", "heute journal", "rtl aktuell", "sat1 nachrichten",
            "zeitung", "spiegel", "zeit", "faz", "süddeutsche", "bild", "welt",
            "journalist", "reporter", "korrespondent", "redaktion", "presse",
            "bundesregierung", "bundestag", "kanzler", "minister", "partei",
            "wahl", "abstimmung", "koalition", "opposition", "gesetz", "reform",
            "eu", "usa", "china", "russland", "ukraine", "krieg", "konflikt",
            "diplomatie", "sanktionen", "gipfel", "summit", "abkommen", "vertrag",
            "wirtschaftskrise", "inflation", "rezession", "arbeitslosigkeit", "börse",
            "aktien", "dax", "dow jones", "kurs", "zinsen", "ezb", "fed",
            "klimakrise", "umwelt", "naturkatastrophe", "erdbeben", "überschwemmung",
            "demonstration", "protest", "streik", "bewegung", "aktivismus",
            "skandal", "affäre", "korruption", "ermittlung", "prozess", "urteil",
            "sport news", "fußball ergebnis", "bundesliga", "champions league",
            "promi news", "klatsch", "tratsch", "celebrity", "royal", "königshaus",
            # Phrasen
            "was ist passiert", "was gibt es neues", "aktuelle nachrichten",
            "hast du gehört", "stimmt das", "ist das wahr", "fake news",
            "quelle", "zuverlässig", "seriös", "clickbait", "sensationsmeldung",
        ],
        "philosophy": [
            # Grundlagen
            "sinn", "leben", "tod", "existenz", "wahrheit", "glück",
            "philosophie", "denken", "gedanke", "bewusstsein", "realität",
            "träumen", "schicksal", "zufall", "gott", "religion", "glaube",
            # Erweitert
            "sinn des lebens", "existenzfrage", "metaphysik", "ontologie", "epistemologie",
            "ethik", "moral", "tugend", "gut", "böse", "richtig", "falsch",
            "gerechtigkeit", "freiheit", "freier wille", "determinismus", "kausalität",
            "seele", "geist", "körper", "dualismus", "materialismus", "idealismus",
            "subjektiv", "objektiv", "perspektive", "weltanschauung", "paradigma",
            "wahrnehmung", "erkenntnis", "wissen", "glauben", "zweifel", "skeptizismus",
            "logik", "vernunft", "rationalität", "intuition", "emotion", "verstand",
            "zeit", "raum", "unendlichkeit", "ewigkeit", "vergänglichkeit", "nichts",
            "sein", "nichtsein", "werden", "vergehen", "wandel", "konstanz",
            "identität", "selbst", "ego", "persona", "authentizität", "selbstfindung",
            "liebe", "hass", "freundschaft", "einsamkeit", "verbundenheit", "trennung",
            "leid", "schmerz", "freude", "hoffnung", "verzweiflung", "akzeptanz",
            "verantwortung", "schuld", "vergebung", "reue", "gewissen", "karma",
            "platon", "aristoteles", "kant", "nietzsche", "sartre", "camus",
            "sokrates", "descartes", "hegel", "schopenhauer", "heidegger", "wittgenstein",
            "stoizismus", "existenzialismus", "nihilismus", "buddhismus", "taoismus",
            "meditation", "achtsamkeit", "erleuchtung", "erwachen", "transzendenz",
            # Phrasen
            "was ist der sinn", "warum sind wir hier", "was passiert nach dem tod",
            "gibt es gott", "was ist wahrheit", "was ist realität", "sind wir frei",
            "kann man glücklich sein", "was macht glücklich", "warum leiden wir",
            "wer bin ich", "was will ich", "was soll ich tun", "wie soll ich leben",
        ],
        "travel": [
            # Grundlagen
            "reise", "urlaub", "reisen", "flug", "hotel", "buchen",
            "strand", "berge", "stadt", "land", "ausland", "inlandy",
            # Erweitert
            "flughafen", "abflug", "ankunft", "boarding", "gate", "terminal",
            "check in", "gepäck", "koffer", "handgepäck", "reisepass", "visum",
            "zug", "bahn", "ice", "tgv", "eurostar", "nachtzug", "interrail",
            "auto", "mietwagen", "roadtrip", "autobahn", "tankstelle", "maut",
            "bus", "fernbus", "flixbus", "greyhound", "transfer", "shuttle",
            "fähre", "schiff", "kreuzfahrt", "yacht", "boot", "segeln",
            "airbnb", "hostel", "pension", "resort", "all inclusive", "zimmer",
            "buchung", "stornierung", "umbuchung", "reiseversicherung", "reiserücktritt",
            "sehenswürdigkeit", "attraktion", "museum", "denkmal", "altstadt", "tour",
            "stadtführung", "reiseführer", "lonely planet", "tripadvisor", "booking",
            "backpacking", "couchsurfing", "workaway", "wwoof", "volunteer",
            "strandurlaub", "skiurlaub", "wanderurlaub", "aktivurlaub", "wellness urlaub",
            "rundreise", "individualreise", "pauschalreise", "last minute", "frühbucher",
            "europa", "asien", "amerika", "afrika", "australien", "ozeanien",
            "spanien", "italien", "frankreich", "griechenland", "türkei", "thailand",
            "bali", "malediven", "karibik", "hawaii", "new york", "paris", "london",
            "jetlag", "zeitverschiebung", "klima", "saison", "hauptsaison", "nebensaison",
            # Phrasen
            "will verreisen", "plane urlaub", "wohin soll ich reisen",
            "beste reisezeit", "geheimtipp", "muss man gesehen haben",
            "wie komme ich nach", "was kostet", "brauche ich visum",
        ],
        "shopping": [
            # Grundlagen
            "kaufen", "shoppen", "bestellen", "einkaufen", "geld", "preis",
            "teuer", "billig", "günstig", "rabatt", "angebot", "sale",
            # Erweitert
            "amazon", "ebay", "zalando", "otto", "mediamarkt", "saturn",
            "online shop", "webshop", "marketplace", "lieferung", "versand", "porto",
            "warenkorb", "checkout", "bezahlen", "paypal", "kreditkarte", "klarna",
            "rückgabe", "umtausch", "reklamation", "garantie", "gewährleistung",
            "geschäft", "laden", "boutique", "kaufhaus", "outlet", "secondhand",
            "supermarkt", "discounter", "aldi", "lidl", "rewe", "edeka",
            "kleidung", "schuhe", "accessoires", "schmuck", "tasche", "uhr",
            "elektronik", "smartphone", "tablet", "laptop", "fernseher", "kopfhörer",
            "möbel", "ikea", "einrichtung", "deko", "haushalt", "küche",
            "marke", "designer", "luxus", "premium", "basic", "budget",
            "größe", "passt", "passt nicht", "umtauschen", "zurückschicken",
            "bewertung", "rezension", "sterne", "empfehlung", "vergleich", "test",
            "schnäppchen", "deal", "gutschein", "code", "black friday", "cyber monday",
            "wunschliste", "wishlist", "merken", "später kaufen", "auf lager",
            "ausverkauft", "nicht lieferbar", "vorbestellung", "preorder", "neuheit",
            # Phrasen
            "will kaufen", "brauche neues", "suche nach", "wo gibt es",
            "ist das gut", "lohnt sich das", "zu teuer", "zu billig",
            "beste qualität", "preis leistung", "kann ich mir leisten",
        ],
        "home": [
            # Grundlagen
            "wohnung", "haus", "zuhause", "miete", "kaufen", "umziehen",
            "zimmer", "küche", "bad", "schlafzimmer", "wohnzimmer", "balkon",
            # Erweitert
            "appartement", "studio", "loft", "penthouse", "reihenhaus", "einfamilienhaus",
            "eigentumswohnung", "mietwohnung", "wg zimmer", "untermiete", "zwischenmiete",
            "vermieter", "mieter", "makler", "immobilie", "immoscout", "wg gesucht",
            "kaution", "nebenkosten", "warmmiete", "kaltmiete", "betriebskosten",
            "mietvertrag", "kündigungsfrist", "übergabe", "abnahme", "protokoll",
            "renovieren", "sanieren", "streichen", "tapezieren", "verlegen",
            "möbliert", "unmöbliert", "einrichten", "dekorieren", "gestalten",
            "sofa", "couch", "bett", "schrank", "tisch", "stuhl", "regal",
            "lampe", "teppich", "vorhang", "bild", "pflanze", "spiegel",
            "kühlschrank", "herd", "backofen", "mikrowelle", "spülmaschine", "waschmaschine",
            "putzen", "aufräumen", "saugen", "wischen", "waschen", "bügeln",
            "müll", "mülltrennung", "recycling", "biomüll", "restmüll", "gelber sack",
            "nachbar", "hausordnung", "hausmeister", "hausverwaltung", "eigentümerversammlung",
            "garten", "terrasse", "garage", "stellplatz", "keller", "dachboden",
            # Phrasen
            "suche wohnung", "will umziehen", "muss renovieren", "neue möbel",
            "wohnung zu klein", "wohnung zu teuer", "traumwohnung", "endlich zuhause",
        ],
        "pets": [
            # Grundlagen
            "haustier", "hund", "katze", "tier", "füttern", "gassi",
            "tierarzt", "futter", "spielen", "kuscheln",
            # Erweitert
            "welpe", "kätzchen", "kitten", "puppy", "baby tier", "jungtier",
            "rasse", "mischling", "züchter", "tierheim", "adoption", "rescue",
            "hamster", "meerschweinchen", "kaninchen", "hase", "maus", "ratte",
            "vogel", "papagei", "wellensittich", "kanarienvogel", "fink",
            "fisch", "aquarium", "goldfisch", "guppy", "neon", "wels",
            "reptil", "schildkröte", "eidechse", "gecko", "schlange", "terrarium",
            "pferd", "pony", "reiten", "stall", "weide", "reiterhof",
            "bellen", "miauen", "schnurren", "wedeln", "kratzen", "beißen",
            "leine", "halsband", "geschirr", "körbchen", "kratzbaum", "käfig",
            "trockenfutter", "nassfutter", "leckerli", "kausnack", "wasser napf",
            "impfung", "entwurmung", "kastration", "sterilisation", "chip",
            "tierversicherung", "op versicherung", "haftpflicht",
            "training", "erziehung", "tricks", "kommandos", "hundeschule",
            "fell", "pfote", "schnauze", "schwanz", "ohren", "augen",
            # Phrasen
            "will haustier", "hab einen hund", "hab eine katze", "ist krank",
            "muss zum tierarzt", "braucht futter", "will spielen", "ist süß",
        ],
        "cars": [
            # Grundlagen
            "auto", "fahren", "führerschein", "tanken", "parken",
            "verkehr", "stau", "unfall", "werkstatt", "reparatur",
            # Erweitert
            "pkw", "suv", "kombi", "limousine", "cabrio", "coupé", "van",
            "neuwagen", "gebrauchtwagen", "leasing", "finanzierung", "barzahlung",
            "marke", "modell", "bmw", "mercedes", "audi", "vw", "tesla", "porsche",
            "motor", "ps", "hubraum", "zylinder", "getriebe", "automatik", "schaltung",
            "benzin", "diesel", "elektro", "hybrid", "wasserstoff", "lpg",
            "verbrauch", "reichweite", "ladestation", "wallbox", "schnelllader",
            "tüv", "hauptuntersuchung", "abgasuntersuchung", "inspektion", "ölwechsel",
            "reifen", "winterreifen", "sommerreifen", "allwetterreifen", "felgen",
            "bremsen", "kupplung", "lenkung", "stoßdämpfer", "auspuff", "kat",
            "navi", "infotainment", "einparkhilfe", "rückfahrkamera", "tempomat",
            "airbag", "abs", "esp", "spurhalteassistent", "notbremsassistent",
            "versicherung", "haftpflicht", "teilkasko", "vollkasko", "schadensfreiheitsklasse",
            "kfz steuer", "zulassung", "abmeldung", "ummeldung", "kennzeichen",
            "carsharing", "share now", "sixt", "mietwagen", "uber", "taxi",
            # Phrasen
            "will auto kaufen", "brauche neues auto", "auto kaputt", "muss tanken",
            "stehe im stau", "hab unfall gebaut", "muss in die werkstatt",
        ],
        # === NEUE KATEGORIEN (21 zusätzliche) ===
        "finance": [
            # Grundlagen
            "geld", "finanzen", "konto", "bank", "sparkasse", "überweisung",
            "gehalt", "lohn", "einkommen", "ausgaben", "sparen", "investieren",
            "kredit", "schulden", "zinsen", "rendite", "aktien", "fonds",
            # Erweitert
            "girokonto", "sparkonto", "tagesgeld", "festgeld", "depot",
            "online banking", "pin", "tan", "kontostand", "kontoauszug",
            "dauerauftrag", "lastschrift", "einzugsermächtigung", "sepa",
            "kreditkarte", "ec karte", "debitkarte", "bargeld", "münzen", "scheine",
            "steuern", "steuererklärung", "finanzamt", "steuerberater", "lohnsteuer",
            "mehrwertsteuer", "einkommensteuer", "kapitalertragssteuer", "freibetrag",
            "budget", "haushaltsbuch", "ausgaben tracken", "sparziel", "notgroschen",
            "etf", "anleihen", "dividende", "portfolio", "diversifikation", "risiko",
            "bitcoin", "ethereum", "krypto", "trading", "broker", "trade republic",
            "rente", "altersvorsorge", "riester", "betriebsrente", "lebensversicherung",
            "erbschaft", "schenkung", "testament", "vermögen", "immobilie",
            # Phrasen
            "hab kein geld", "bin pleite", "brauche geld", "muss sparen",
            "will investieren", "wie viel kostet", "zu teuer", "kann mir nicht leisten",
            "wann kommt gehalt", "konto ist leer", "schulden abbezahlen",
        ],
        "sports": [
            # Grundlagen
            "sport", "training", "fitness", "workout", "gym", "studio",
            "laufen", "joggen", "schwimmen", "radfahren", "wandern",
            "fußball", "basketball", "tennis", "volleyball", "handball",
            # Erweitert
            "mannschaft", "verein", "liga", "bundesliga", "champions league",
            "meisterschaft", "pokal", "turnier", "spiel", "match", "partie",
            "tor", "punkt", "satz", "gewonnen", "verloren", "unentschieden",
            "trainer", "coach", "spieler", "athlet", "sportler", "profi", "amateur",
            "marathon", "triathlon", "ironman", "olympia", "weltmeisterschaft",
            "krafttraining", "ausdauer", "cardio", "hiit", "crossfit", "calisthenics",
            "yoga", "pilates", "stretching", "warm up", "cool down", "dehnen",
            "muskel", "muskelkater", "regeneration", "erholung", "pause", "ruhetag",
            "personal record", "pr", "bestzeit", "steigerung", "fortschritt",
            "sportkleidung", "sportschuhe", "ausrüstung", "gewichte", "hanteln",
            "laufband", "crosstrainer", "rudergerät", "klimmzugstange",
            # Phrasen
            "war beim sport", "gehe trainieren", "mache workout", "hab trainiert",
            "bin fit", "will fitter werden", "muss mehr sport machen",
            "wer hat gewonnen", "wie steht es", "wann spielt", "live gucken",
        ],
        "education": [
            # Grundlagen
            "lernen", "bildung", "schule", "uni", "studium", "ausbildung",
            "unterricht", "kurs", "seminar", "vorlesung", "workshop",
            "prüfung", "klausur", "test", "abitur", "abschluss", "zeugnis",
            # Erweitert
            "grundschule", "hauptschule", "realschule", "gymnasium", "gesamtschule",
            "berufsschule", "fachhochschule", "universität", "hochschule",
            "bachelor", "master", "promotion", "doktor", "professor",
            "semester", "trimester", "schuljahr", "ferien", "semesterferien",
            "fach", "mathe", "deutsch", "englisch", "physik", "chemie", "biologie",
            "geschichte", "geografie", "kunst", "musik", "sport", "religion",
            "hausaufgaben", "referat", "präsentation", "hausarbeit", "bachelorarbeit",
            "note", "bewertung", "zeugnis", "durchschnitt", "numerus clausus",
            "nachhilfe", "tutor", "mentor", "lerngruppe", "bibliothek",
            "online lernen", "e-learning", "mooc", "udemy", "coursera", "duolingo",
            "weiterbildung", "fortbildung", "zertifikat", "qualifikation",
            "stipendium", "bafög", "studienkredit", "semesterbeitrag",
            # Phrasen
            "muss lernen", "hab prüfung", "schreibe klausur", "mache hausaufgaben",
            "verstehe nicht", "ist schwer", "ist kompliziert", "brauch nachhilfe",
            "hab bestanden", "bin durchgefallen", "gute note", "schlechte note",
        ],
        "social_media": [
            # Grundlagen
            "social media", "soziale medien", "post", "posten", "teilen",
            "follower", "following", "like", "liken", "kommentar", "kommentieren",
            "story", "stories", "reel", "reels", "feed", "timeline",
            # Erweitert
            "instagram", "insta", "facebook", "fb", "twitter", "x",
            "tiktok", "snapchat", "snap", "youtube", "yt", "twitch",
            "linkedin", "xing", "pinterest", "reddit", "discord", "telegram",
            "whatsapp", "messenger", "dm", "direct message", "nachricht",
            "hashtag", "tag", "taggen", "mention", "erwähnung",
            "viral", "trending", "trend", "challenge", "hype",
            "influencer", "content creator", "blogger", "vlogger", "streamer",
            "content", "video", "bild", "foto", "meme", "gif",
            "algorithm", "algorithmus", "reichweite", "engagement", "views",
            "abonnieren", "abo", "subscribe", "notification", "benachrichtigung",
            "profil", "bio", "profilbild", "avatar", "username", "handle",
            "verifiziert", "blauer haken", "fake account", "bot", "troll",
            # Phrasen
            "hast du gesehen auf", "ist viral gegangen", "hab gepostet",
            "follow mich", "hab neuen follower", "wurde getaggt", "schreib mir dm",
            "neue story", "hab gelikt", "hab kommentiert", "ist im trend",
        ],
        "fashion": [
            # Grundlagen
            "mode", "kleidung", "outfit", "style", "look", "trend",
            "tragen", "anziehen", "anprobieren", "passt", "steht mir",
            "hose", "jeans", "hemd", "bluse", "t-shirt", "pullover",
            # Erweitert
            "kleid", "rock", "anzug", "jacke", "mantel", "hoodie", "cardigan",
            "shorts", "leggings", "jogginghose", "sweatpants", "chino", "cargo",
            "bh", "unterwäsche", "socken", "strumpfhose", "nachthemd", "pyjama",
            "schuhe", "sneaker", "stiefel", "sandalen", "high heels", "pumps",
            "accessoires", "gürtel", "schal", "mütze", "handschuhe", "tasche",
            "schmuck", "kette", "armband", "ohrringe", "ring", "uhr",
            "brille", "sonnenbrille", "hut", "cap", "kappe",
            "marke", "designer", "luxus", "high fashion", "streetwear", "vintage",
            "zara", "h&m", "primark", "uniqlo", "gucci", "prada", "louis vuitton",
            "größe", "xs", "s", "m", "l", "xl", "xxl", "passform", "schnitt",
            "farbe", "muster", "gestreift", "kariert", "uni", "print",
            "waschen", "bügeln", "chemische reinigung", "fleck", "kaputt",
            # Phrasen
            "was soll ich anziehen", "steht mir das", "ist das modern",
            "brauche neue klamotten", "will shoppen gehen", "hab nichts anzuziehen",
            "ist das zu overdressed", "zu casual", "passt das zusammen",
        ],
        "beauty": [
            # Grundformen
            "schönheit", "beauty", "pflege", "kosmetik", "makeup", "schminke",
            "haut", "haare", "nägel", "körperpflege", "hygiene",
            "creme", "lotion", "serum", "öl", "maske",
            # Erweitert
            "gesichtspflege", "hautpflege", "skincare", "routine", "morgens", "abends",
            "reinigung", "peeling", "toner", "essence", "moisturizer", "sonnenschutz",
            "anti aging", "falten", "pickel", "akne", "unreinheiten", "mitesser",
            "trockene haut", "fettige haut", "mischhaut", "empfindliche haut",
            "foundation", "concealer", "puder", "rouge", "highlighter", "contouring",
            "lidschatten", "eyeliner", "mascara", "augenbrauen", "wimpern",
            "lippenstift", "lipgloss", "lipliner", "lipbalm",
            "nagellack", "maniküre", "pediküre", "nagelstudio", "gelnägel",
            "friseur", "haarschnitt", "färben", "tönen", "blondieren", "highlights",
            "föhnen", "glätten", "locken", "styling", "haargel", "haarspray",
            "parfum", "duft", "deo", "bodylotion", "duschgel", "shampoo",
            "spa", "wellness", "massage", "sauna", "gesichtsbehandlung",
            # Phrasen
            "muss zum friseur", "neue frisur", "haare schneiden",
            "brauche neue creme", "haut ist trocken", "hab pickel",
            "welches makeup", "wie schminke ich", "beauty routine",
        ],
        "environment": [
            # Grundlagen
            "umwelt", "natur", "klima", "erde", "planet", "ökologie",
            "nachhaltig", "nachhaltigkeit", "grün", "bio", "öko",
            "umweltschutz", "klimaschutz", "naturschutz", "tierschutz",
            # Erweitert
            "klimawandel", "erderwärmung", "treibhauseffekt", "co2", "emissionen",
            "erneuerbare energie", "solar", "wind", "wasserkraft", "geothermie",
            "recycling", "mülltrennung", "kompost", "müllvermeidung", "zero waste",
            "plastik", "mikroplastik", "einweg", "mehrweg", "verpackung",
            "wasser", "trinkwasser", "grundwasser", "meer", "ozean", "verschmutzung",
            "luft", "luftqualität", "smog", "feinstaub", "abgase",
            "wald", "regenwald", "abholzung", "aufforstung", "baum pflanzen",
            "artensterben", "biodiversität", "artenschutz", "wildtiere", "lebensraum",
            "ökologischer fußabdruck", "co2 fußabdruck", "kompensieren", "ausgleichen",
            "vegetarisch", "vegan", "fleischkonsum", "regional", "saisonal", "fairtrade",
            "elektroauto", "fahrrad", "öffentliche verkehrsmittel", "fliegen vermeiden",
            "fridays for future", "klimastreik", "aktivismus", "demonstration",
            # Phrasen
            "müssen was tun", "für die umwelt", "nachhaltiger leben",
            "weniger plastik", "mehr recyceln", "klimaneutral",
            "ist das gut für die umwelt", "ökologisch sinnvoll",
        ],
        "science": [
            # Grundlagen
            "wissenschaft", "forschung", "studie", "experiment", "labor",
            "entdeckung", "erfindung", "theorie", "hypothese", "beweis",
            "physik", "chemie", "biologie", "mathematik", "informatik",
            # Erweitert
            "wissenschaftler", "forscher", "professor", "doktor", "nobelpreis",
            "universität", "institut", "akademie", "publikation", "peer review",
            "quantenphysik", "relativitätstheorie", "teilchen", "atom", "molekül",
            "evolution", "genetik", "dna", "rna", "gen", "mutation", "genom",
            "zelle", "bakterie", "virus", "mikroorganismus", "organismus",
            "ökosystem", "photosynthese", "stoffwechsel", "enzyme", "proteine",
            "astronomie", "weltall", "universum", "galaxie", "stern", "planet",
            "schwarzes loch", "urknall", "big bang", "dunkle materie", "dunkle energie",
            "raumfahrt", "nasa", "esa", "spacex", "rakete", "satellit", "raumstation",
            "künstliche intelligenz", "machine learning", "algorithmus", "neuronales netz",
            "robotik", "automatisierung", "quantencomputer", "nanotechnologie",
            "medizinische forschung", "impfstoff", "therapie", "klinische studie",
            # Phrasen
            "hab gelesen dass", "wissenschaftler haben herausgefunden",
            "neue studie zeigt", "ist das wissenschaftlich", "gibt es beweise",
            "wie funktioniert das", "warum ist das so", "erkläre mir",
        ],
        "art": [
            # Grundlagen
            "kunst", "künstler", "kunstwerk", "malen", "zeichnen",
            "bild", "gemälde", "zeichnung", "skulptur", "plastik",
            "museum", "galerie", "ausstellung", "vernissage",
            # Erweitert
            "malerei", "ölmalerei", "aquarell", "acryl", "pastell", "kohle",
            "portrait", "landschaft", "stillleben", "abstrakt", "impressionismus",
            "expressionismus", "surrealismus", "kubismus", "pop art", "moderne kunst",
            "bildhauerei", "ton", "bronze", "marmor", "holz", "stein",
            "fotografie", "foto", "fotograf", "kamera", "objektiv", "belichtung",
            "grafik", "design", "illustration", "comic", "cartoon", "animation",
            "street art", "graffiti", "mural", "urban art", "banksy",
            "pinsel", "farbe", "leinwand", "staffelei", "palette", "atelier",
            "kunstgeschichte", "alte meister", "renaissance", "barock", "romantik",
            "picasso", "van gogh", "monet", "da vinci", "rembrandt", "warhol",
            "kunstmarkt", "auktion", "sammler", "original", "kopie", "fälschung",
            "kunsttherapie", "kreativität", "selbstausdruck", "inspiration",
            # Phrasen
            "gehe ins museum", "tolle ausstellung", "schönes kunstwerk",
            "wer hat das gemalt", "was bedeutet das", "interpretiere das",
            "will malen lernen", "bin kreativ", "hab was gezeichnet",
        ],
        "language": [
            # Grundlagen
            "sprache", "sprachen", "sprechen", "reden", "kommunikation",
            "wort", "wörter", "satz", "grammatik", "vokabeln",
            "übersetzen", "übersetzung", "dolmetschen", "dolmetscher",
            # Erweitert
            "deutsch", "englisch", "französisch", "spanisch", "italienisch",
            "russisch", "chinesisch", "japanisch", "koreanisch", "arabisch",
            "muttersprache", "fremdsprache", "zweitsprache", "bilingualisch",
            "sprachkurs", "sprachschule", "tandem", "austausch", "immersion",
            "aussprache", "akzent", "dialekt", "mundart", "hochdeutsch",
            "lesen", "schreiben", "hören", "verstehen", "sprechen",
            "anfänger", "fortgeschritten", "fließend", "muttersprachlich",
            "zertifikat", "sprachtest", "toefl", "ielts", "delf", "goethe zertifikat",
            "vokabel", "verb", "nomen", "adjektiv", "adverb", "präposition",
            "konjugation", "deklination", "zeitform", "vergangenheit", "zukunft",
            "redewendung", "sprichwort", "idiom", "slang", "umgangssprache",
            "linguistik", "sprachwissenschaft", "etymologie", "semantik",
            # Phrasen
            "lerne gerade", "kann ein bisschen", "spreche fließend",
            "wie sagt man", "was heißt das", "kannst du übersetzen",
            "verstehe nicht", "zu schnell", "nochmal bitte", "langsamer bitte",
        ],
        "creativity": [
            # Grundlagen
            "kreativ", "kreativität", "idee", "einfall", "inspiration",
            "erschaffen", "gestalten", "designen", "entwerfen", "entwickeln",
            "phantasie", "fantasie", "vorstellung", "imagination",
            # Erweitert
            "brainstorming", "ideenfindung", "konzept", "entwurf", "skizze",
            "innovation", "originell", "einzigartig", "neu", "anders",
            "künstlerisch", "schöpferisch", "erfinderisch", "einfallsreich",
            "diy", "selbst machen", "basteln", "handarbeit", "handwerk",
            "upcycling", "recycling kunst", "aus alt mach neu",
            "schreiben", "dichten", "texten", "storytelling", "erzählen",
            "komponieren", "musik machen", "beat", "melodie", "song schreiben",
            "tanzen", "choreografie", "bewegung", "ausdruck", "performance",
            "theater", "schauspiel", "improvisation", "rollenspiel",
            "fotografie", "film", "video", "animation", "content creation",
            "flow", "zone", "inspiriert", "beflügelt", "motiviert",
            "blockade", "kreativblock", "schreibblockade", "keine ideen",
            # Phrasen
            "hab ne idee", "mir ist was eingefallen", "bin kreativ",
            "will was erschaffen", "mache was selbst", "bin inspiriert",
            "keine inspiration", "brauche ideen", "hilf mir denken",
        ],
        "sleep": [
            # Grundlagen
            "schlaf", "schlafen", "müde", "wach", "aufwachen",
            "bett", "matratze", "kissen", "decke", "schlafzimmer",
            "einschlafen", "durchschlafen", "aufstehen", "wecker",
            # Erweitert
            "schlafqualität", "tiefschlaf", "rem schlaf", "leichtschlaf",
            "schlafzyklus", "schlafphasen", "schlafrhythmus", "biorhythmus",
            "schlafstörung", "insomnie", "schlaflosigkeit", "schlafapnoe",
            "albtraum", "schlechter traum", "nachtschweiß", "unruhig",
            "gute nacht", "schlaf gut", "träum süß", "guten morgen",
            "früh aufstehen", "spät aufstehen", "ausschlafen", "überschlafen",
            "nickerchen", "power nap", "mittagsschlaf", "siesta",
            "schlafhygiene", "abendroutine", "entspannung", "runterkommen",
            "melatonin", "schlafmittel", "baldrian", "tee", "entspannungsmusik",
            "dunkel", "still", "kühl", "temperatur", "luftfeuchtigkeit",
            "snooze", "schlummern", "dösen", "dahindämmern",
            "morgenmuffel", "nachtmensch", "frühaufsteher", "langschläfer",
            # Phrasen
            "bin müde", "will schlafen", "gehe ins bett", "kann nicht schlafen",
            "hab schlecht geschlafen", "gut geschlafen", "bin ausgeruht",
            "muss früh raus", "schlafe aus", "brauch mehr schlaf",
        ],
        "dreams": [
            # Grundlagen
            "traum", "träumen", "traumwelt", "traumhaft", "verträumt",
            "albtraum", "alptraum", "nachts", "schlafend",
            "wunsch", "wünschen", "hoffen", "sehnen", "ersehnen",
            # Erweitert
            "tagtraum", "tagträumen", "fantasieren", "vorstellen", "ausmalen",
            "luzider traum", "klartraum", "traumkontrolle", "bewusst träumen",
            "traumdeutung", "traumsymbol", "unterbewusstsein", "psyche",
            "fliegen im traum", "fallen im traum", "verfolgt werden", "zähne verlieren",
            "prophezeiung", "vorahnung", "déjà vu", "vision",
            "lebenstraum", "traumjob", "traumhaus", "traumpartner", "traumreise",
            "verwirklichen", "erreichen", "erfüllen", "wahr werden",
            "träumer", "idealist", "romantiker", "visionär",
            "traumfänger", "traumtagebuch", "traum erinnern", "traum aufschreiben",
            "surreal", "unwirklich", "bizarr", "seltsam", "merkwürdig",
            "wiederkehrender traum", "immer derselbe traum", "oft träumen von",
            "schlafwandeln", "sprechen im schlaf", "zucken", "aufschrecken",
            # Phrasen
            "hab geträumt", "hatte einen traum", "das war ein traum",
            "träume von", "wünsche mir", "hoffe dass", "stelle mir vor",
            "war nur ein traum", "traum ist wahr geworden", "lebe meinen traum",
        ],
        "memories": [
            # Grundlagen
            "erinnerung", "erinnern", "gedächtnis", "denken an", "vergessen",
            "vergangenheit", "früher", "damals", "einst", "gestern",
            "nostalgie", "nostalgisch", "wehmut", "sentimental",
            # Erweitert
            "kindheitserinnerung", "jugend", "schulzeit", "studienzeit",
            "erlebnis", "erfahrung", "moment", "augenblick", "ereignis",
            "foto", "bild", "video", "aufnahme", "dokumentieren",
            "fotoalbum", "tagebuch", "journal", "chronik", "aufzeichnung",
            "andenken", "souvenir", "mitbringsel", "erinnerungsstück",
            "gedenkstätte", "denkmal", "gedenktag", "jahrestag", "jubiläum",
            "kurzzeitgedächtnis", "langzeitgedächtnis", "speichern", "abrufen",
            "vergesslich", "blackout", "verdrängen", "unterdrücken",
            "flashback", "zurückversetzt", "wie damals", "als wärs gestern",
            "generationen", "großeltern erzählen", "familiengeschichte",
            "tradition", "brauch", "ritual", "gewohnheit",
            "memoir", "biografie", "autobiografie", "lebensgeschichte",
            # Phrasen
            "erinnere mich an", "weißt du noch", "damals als",
            "hab vergessen", "fällt mir nicht ein", "wie war das nochmal",
            "gute zeiten", "schöne erinnerungen", "vermisse die zeit",
        ],
        "future": [
            # Grundlagen
            "zukunft", "morgen", "bald", "später", "irgendwann",
            "werden", "planen", "vorhaben", "beabsichtigen",
            "erwarten", "hoffen", "wünschen", "träumen",
            # Erweitert
            "zukunftsplan", "lebensplan", "fünfjahresplan", "langfristig",
            "vision", "ziel", "ambition", "aspiration", "streben",
            "prognose", "vorhersage", "trend", "entwicklung", "tendenz",
            "technologie der zukunft", "innovation", "fortschritt", "evolution",
            "künstliche intelligenz", "automation", "roboter", "virtual reality",
            "klimazukunft", "nachhaltigkeit", "erneuerbare energie", "grün",
            "nächste generation", "kinder", "enkelkinder", "nachkommen",
            "karriereplan", "berufsziel", "traumjob", "position",
            "familiengründung", "heiraten", "kinder bekommen", "haus bauen",
            "ruhestand", "rente", "pension", "lebensabend",
            "möglichkeit", "potenzial", "chance", "option", "alternative",
            "ungewiss", "unsicher", "offen", "unklar", "abwarten",
            # Phrasen
            "was bringt die zukunft", "wie wird es werden", "was kommt noch",
            "freue mich auf", "plane zu", "will irgendwann", "eines tages",
            "in zukunft werde ich", "stelle mir vor dass", "hoffe auf",
        ],
        "goals": [
            # Grundlagen
            "ziel", "ziele", "vorhaben", "plan", "vorsatz",
            "erreichen", "schaffen", "verwirklichen", "umsetzen",
            "motivation", "antrieb", "wille", "ehrgeiz", "ambition",
            # Erweitert
            "smart ziele", "messbar", "erreichbar", "realistisch", "terminiert",
            "kurzfristiges ziel", "langfristiges ziel", "etappenziel", "meilenstein",
            "priorität", "wichtig", "dringend", "fokus", "konzentration",
            "to do liste", "aufgabenliste", "checklist", "abhaken", "erledigt",
            "fortschritt", "progress", "entwicklung", "verbesserung", "steigerung",
            "durchhalten", "dranbleiben", "nicht aufgeben", "weitermachen",
            "rückschlag", "hindernis", "hürde", "problem", "herausforderung",
            "neujahrsvorsatz", "bucket list", "life goals", "dream big",
            "erfolg", "achievement", "accomplishment", "leistung", "resultat",
            "selbstdisziplin", "willenskraft", "konsequenz", "ausdauer",
            "coach", "mentor", "accountability partner", "unterstützung",
            "visualisieren", "manifestieren", "positiv denken", "mindset",
            # Phrasen
            "mein ziel ist", "will erreichen", "arbeite daran", "bin dran",
            "hab mir vorgenommen", "nehme mir vor", "dieses jahr will ich",
            "habs geschafft", "ziel erreicht", "nächstes ziel",
        ],
        "problems": [
            # Grundlagen
            "problem", "probleme", "schwierigkeit", "hindernis", "hürde",
            "herausforderung", "krise", "konflikt", "streit", "ärger",
            "sorge", "sorgen", "angst", "befürchtung", "bedenken",
            # Erweitert
            "lösung", "lösen", "beheben", "klären", "regeln",
            "situation", "lage", "umstand", "zustand", "sachverhalt",
            "ursache", "grund", "auslöser", "trigger", "wurzel",
            "konsequenz", "folge", "auswirkung", "effekt", "resultat",
            "hilfe", "unterstützung", "beistand", "rat", "ratschlag",
            "beratung", "therapie", "coaching", "mediation", "vermittlung",
            "stress", "druck", "belastung", "überforderung", "burnout",
            "schulden", "geldprobleme", "finanzielle schwierigkeiten",
            "beziehungsproblem", "streit", "trennung", "scheidung",
            "arbeitsproblem", "jobverlust", "arbeitslos", "gekündigt",
            "gesundheitsproblem", "krankheit", "diagnose", "behandlung",
            "technikproblem", "bug", "fehler", "funktioniert nicht",
            # Phrasen
            "hab ein problem", "brauche hilfe", "weiß nicht weiter",
            "was soll ich tun", "was mache ich jetzt", "wie löse ich das",
            "stecke fest", "komme nicht weiter", "ist kompliziert",
        ],
        "help": [
            # Grundlagen
            "hilfe", "helfen", "unterstützen", "beistand", "assistenz",
            "brauche", "benötige", "suche", "frage", "bitte",
            "kannst du", "könntest du", "würdest du", "hilfst du mir",
            # Erweitert
            "unterstützung", "beistand", "rückhalt", "stütze", "halt",
            "rat", "ratschlag", "tipp", "hinweis", "empfehlung",
            "anleitung", "erklärung", "tutorial", "how to", "wie geht",
            "notfall", "dringend", "sofort", "schnell", "asap",
            "sos", "mayday", "alarm", "notruf", "rettung",
            "beratung", "auskunft", "information", "service", "hotline",
            "fachmann", "experte", "spezialist", "profi", "fachkraft",
            "ehrenamt", "freiwillig", "gemeinnützig", "spende", "charity",
            "gegenseitig", "füreinander", "miteinander", "zusammen", "team",
            "selbsthilfe", "selbst lösen", "eigenständig", "alleine schaffen",
            "überfordert", "hilflos", "verzweifelt", "am ende", "ratlos",
            "angewiesen auf", "abhängig von", "brauche dringend",
            # Phrasen
            "kannst du mir helfen", "ich brauche hilfe", "hilf mir bitte",
            "wie mache ich das", "was soll ich tun", "zeig mir wie",
            "verstehe nicht", "erkläre mir", "hab ein problem mit",
        ],
        "greetings": [
            # Grundlagen
            "hallo", "hi", "hey", "guten tag", "guten morgen",
            "guten abend", "gute nacht", "moin", "servus", "grüß gott",
            "wie gehts", "wie geht es dir", "alles klar", "was geht",
            # Erweitert
            "hallöchen", "halli hallo", "tach", "na", "jo", "ey",
            "grüß dich", "grüezi", "ahoi", "huhu", "heyho",
            "willkommen", "herzlich willkommen", "schön dich zu sehen",
            "lang nicht gesehen", "freut mich", "schön dass du da bist",
            "wie läufts", "was machst du so", "was gibts neues",
            "alles fit", "alles gut bei dir", "gehts dir gut",
            "bin wieder da", "bin zurück", "melde mich", "hier bin ich",
            "wollte mal hallo sagen", "dachte an dich", "schreibe dir mal",
            "guten start", "schönen tag noch", "schönes wochenende",
            "schönen feierabend", "erhol dich gut", "genieß den tag",
            "morgen zusammen", "nabend", "mahlzeit", "n8", "gn8",
            # Jugendsprache
            "yo", "wassup", "whats up", "sup", "howdy", "heya",
            "heyy", "hiiii", "waddup", "ayoo", "yooo",
        ],
        "farewells": [
            # Grundlagen
            "tschüss", "bye", "ciao", "auf wiedersehen", "bis bald",
            "bis später", "bis dann", "bis morgen", "bis gleich",
            "mach's gut", "pass auf dich auf", "alles gute",
            # Erweitert
            "tschö", "tschüssi", "tschau", "servus", "ade", "pfüdi",
            "bis zum nächsten mal", "bis die tage", "bis demnächst",
            "wir sehen uns", "wir hören uns", "wir schreiben uns",
            "hab dich lieb", "hdl", "kuss", "bussi", "drück dich",
            "vermiss mich nicht", "werde dich vermissen", "denk an mich",
            "bleib gesund", "komm gut heim", "fahr vorsichtig",
            "gute reise", "komm gut an", "schönen urlaub",
            "viel erfolg", "viel glück", "toi toi toi", "wird schon",
            "schlaf gut", "träum süß", "gute nacht", "bis morgen früh",
            "muss los", "muss weg", "bin dann mal weg", "hau rein",
            "man sieht sich", "bis später alligator", "peace out",
            # Jugendsprache
            "peace", "later", "laters", "see ya", "catch you later",
            "byeee", "baii", "bb", "byebye", "deuces", "im out",
        ],
        "smalltalk": [
            # Grundlagen
            "wie gehts", "was machst du", "was gibts neues", "alles gut",
            "schönes wetter", "heute", "gestern", "morgen", "wochenende",
            "arbeit", "freizeit", "urlaub", "ferien", "feiertag",
            # Erweitert
            "wie war dein tag", "wie war die woche", "was hast du gemacht",
            "hast du was vor", "was machst du später", "pläne fürs wochenende",
            "wie lief die arbeit", "viel zu tun gehabt", "stressiger tag",
            "schon gehört dass", "wusstest du dass", "übrigens",
            "apropos", "ach ja", "fällt mir ein", "da war noch was",
            "lustige geschichte", "stell dir vor", "rate mal",
            "krass", "echt", "wirklich", "im ernst", "no way",
            "find ich auch", "stimmt", "genau", "ja voll", "total",
            "verstehe", "kann ich nachvollziehen", "geht mir auch so",
            "kenne ich", "hab ich auch", "bei mir genauso",
            "na dann", "also gut", "ok", "alles klar", "passt",
            "erzähl", "und dann", "und weiter", "was passierte dann",
            "interessant", "spannend", "cool", "nice", "schön",
            # Phrasen
            "wie läufts", "alles fit", "gehts dir gut", "und selbst",
            "nix besonderes", "alles wie immer", "das übliche halt",
        ],
        "opinions": [
            # Grundlagen
            "meinung", "ansicht", "standpunkt", "perspektive", "sichtweise",
            "denke", "glaube", "finde", "meine", "halte für",
            "stimme zu", "stimme nicht zu", "bin dagegen", "bin dafür",
            # Erweitert
            "meiner meinung nach", "ich denke dass", "ich glaube dass",
            "aus meiner sicht", "soweit ich weiß", "wenn du mich fragst",
            "ehrlich gesagt", "offen gesagt", "um ehrlich zu sein",
            "zustimmung", "einverstanden", "akzeptiere", "befürworte",
            "ablehnung", "widerspruch", "einwand", "kritik", "bedenken",
            "pro", "contra", "vorteile", "nachteile", "abwägen",
            "überzeugt", "sicher", "gewiss", "bestimmt", "definitiv",
            "unsicher", "vielleicht", "eventuell", "möglicherweise",
            "neutral", "keine meinung", "mir egal", "ist mir gleich",
            "interessante frage", "gute frage", "schwer zu sagen",
            "kommt drauf an", "je nachdem", "unterschiedlich", "individuell",
            "respektiere deine meinung", "sehe das anders", "verstehe aber",
            # Phrasen
            "was denkst du", "wie siehst du das", "deine meinung",
            "ich finde dass", "für mich ist", "würde sagen dass",
            "bin der meinung", "sehe das so", "stehe dazu",
        ],
        "requests": [
            # Grundlagen
            "bitte", "könntest du", "würdest du", "kannst du",
            "brauche", "möchte", "will", "hätte gern", "wünsche mir",
            "frag", "fragen", "erkundigen", "bitten", "anfragen",
            # Erweitert
            "wärst du so nett", "wenn es nicht zu viel verlangt",
            "wenn du zeit hast", "wenn es geht", "wenn möglich",
            "nur wenn du willst", "kein druck", "nur falls",
            "mach dir keine umstände", "ist nicht so wichtig", "kein stress",
            "wäre toll wenn", "wäre super wenn", "das wäre lieb",
            "ich hätte eine bitte", "darf ich fragen", "eine frage",
            "kurze frage", "schnelle frage", "dumme frage vielleicht",
            "sorry dass ich frage", "hoffe das ist ok", "stört es dich wenn",
            "erlaubst du", "gestattest du", "ist es in ordnung wenn",
            "tu mir einen gefallen", "kannst du mir helfen bei",
            "wärst du bereit zu", "hättest du lust auf", "wie wärs mit",
            "vorschlag", "idee", "angebot", "einladung", "aufforderung",
            # Phrasen
            "kannst du mal", "mach mal bitte", "gib mir mal",
            "ich bräuchte", "es wäre toll wenn", "wäre es möglich dass",
        ],
        "confirmation": [
            # Grundlagen
            "ja", "nein", "okay", "ok", "alles klar",
            "stimmt", "richtig", "korrekt", "genau", "exakt",
            "falsch", "nicht richtig", "stimmt nicht", "nope",
            # Erweitert
            "jawohl", "jap", "jo", "jup", "yep", "yeah", "yes",
            "nö", "nee", "nä", "nope", "no", "niemals", "auf keinen fall",
            "absolut", "definitiv", "hundertprozentig", "auf jeden fall",
            "natürlich", "klar", "logo", "sicher", "selbstverständlich",
            "vielleicht", "eventuell", "möglicherweise", "könnte sein",
            "wahrscheinlich", "vermutlich", "wohl", "denke schon",
            "glaube nicht", "bezweifle", "eher nicht", "eher unwahrscheinlich",
            "bestätigen", "zustimmen", "bejahen", "einwilligen", "akzeptieren",
            "ablehnen", "verneinen", "widersprechen", "abstreiten",
            "einverstanden", "geht klar", "machen wir", "passt", "deal",
            "geht nicht", "keine chance", "vergiss es", "unmöglich",
            # Phrasen
            "ja genau", "ja richtig", "so ist es", "stimmt genau",
            "nein danke", "lieber nicht", "besser nicht", "lass mal",
        ],
    }
    
    # Referenz-Wörter (verweisen auf Vorheriges)
    REFERENCE_WORDS = [
        "das", "dies", "diese", "dieser", "dieses",
        "davon", "dazu", "damit", "darüber", "darum",
        "es", "sie", "er", "ihm", "ihr",
        "vorhin", "eben", "gerade", "letztens",
        "nochmal", "wieder", "weiter", "auch",
    ]

    # =========================================================================
    # SMART RESPONSE PHRASES - Antworten basierend auf erkannten Emotionen
    # =========================================================================

    EMOTION_RESPONSE_PHRASES = {
        # Für jede erkannte Emotion passende Antwort-Phrasen
        "happy": {
            "empathy": [
                "Das freut mich zu hören!",
                "Wie schön, dass es dir gut geht!",
                "Das klingt wirklich toll!",
                "Deine gute Laune ist ansteckend!",
                "Freut mich riesig für dich!",
                "Wie wunderbar!",
            ],
            "actions": [
                "*wedelt freudig mit dem Schwanz*",
                "*Ohren spitzen sich auf*",
                "*lächelt warm*",
            ],
            "follow_up": [
                "Was ist passiert?",
                "Erzähl mir mehr!",
                "Das klingt spannend!",
            ],
        },
        "sad": {
            "empathy": [
                "Das tut mir leid zu hören...",
                "Ich bin hier für dich.",
                "Das klingt wirklich schwer.",
                "Ich verstehe, dass das nicht leicht ist.",
                "Magst du darüber reden?",
                "Ich höre dir zu.",
            ],
            "actions": [
                "*legt den Kopf schief und schaut mitfühlend*",
                "*kuschelt sich näher*",
                "*stupst dich sanft an*",
            ],
            "follow_up": [
                "Kann ich irgendwie helfen?",
                "Möchtest du erzählen was los ist?",
                "Ich bin für dich da.",
            ],
        },
        "angry": {
            "empathy": [
                "Ich verstehe, dass dich das aufregt.",
                "Das klingt wirklich frustrierend.",
                "Da wäre ich auch sauer.",
                "Das ist verständlich.",
                "Manchmal ist alles einfach zu viel.",
            ],
            "actions": [
                "*hört aufmerksam zu*",
                "*nickt verständnisvoll*",
            ],
            "follow_up": [
                "Was ist passiert?",
                "Willst du dich abreagieren?",
                "Soll ich einfach nur zuhören?",
            ],
        },
        "anxious": {
            "empathy": [
                "Es ist okay, sich Sorgen zu machen.",
                "Atme erstmal tief durch.",
                "Ich bin hier, du bist nicht allein.",
                "Das schaffen wir zusammen.",
                "Eins nach dem anderen.",
            ],
            "actions": [
                "*setzt sich beruhigend neben dich*",
                "*legt sanft eine Pfote auf deine Hand*",
            ],
            "follow_up": [
                "Was macht dir Sorgen?",
                "Wie kann ich helfen?",
                "Möchtest du darüber reden?",
            ],
        },
        "tired": {
            "empathy": [
                "Du klingst erschöpft.",
                "Gönn dir eine Pause.",
                "Ruhe dich aus, wenn du magst.",
                "Manchmal muss man auch mal nichts tun.",
            ],
            "actions": [
                "*gähnt sympathisch mit*",
                "*macht Platz zum Ausruhen*",
            ],
            "follow_up": [
                "Harter Tag gehabt?",
                "Soll ich dich in Ruhe lassen?",
                "Brauchst du was Entspannendes?",
            ],
        },
        "excited": {
            "empathy": [
                "Ohh, das klingt aufregend!",
                "Jetzt bin ich auch neugierig!",
                "Das ist ja spannend!",
                "Wow, erzähl mehr!",
            ],
            "actions": [
                "*wedelt aufgeregt*",
                "*springt freudig*",
                "*Augen leuchten*",
            ],
            "follow_up": [
                "Was ist los?",
                "Ich will alles hören!",
                "Lass mich nicht hängen!",
            ],
        },
        "bored": {
            "empathy": [
                "Langeweile ist doof, oder?",
                "Hmm, das kenne ich.",
                "Sollen wir was zusammen machen?",
            ],
            "actions": [
                "*stupst dich spielerisch an*",
            ],
            "follow_up": [
                "Was würde dich aufheitern?",
                "Hast du Lust auf ein Spiel?",
                "Soll ich dir was erzählen?",
            ],
        },
        "confused": {
            "empathy": [
                "Ich helfe dir gern dabei.",
                "Lass uns das zusammen durchgehen.",
                "Keine Sorge, das klären wir.",
            ],
            "actions": [
                "*legt den Kopf schief*",
            ],
            "follow_up": [
                "Was genau verstehst du nicht?",
                "Wo hakt es?",
                "Soll ich es anders erklären?",
            ],
        },
        "grateful": {
            "empathy": [
                "Gern geschehen!",
                "Das ist doch selbstverständlich.",
                "Freut mich, wenn ich helfen konnte!",
                "Immer wieder gerne!",
            ],
            "actions": [
                "*wedelt zufrieden*",
                "*strahlt*",
            ],
            "follow_up": [
                "Kann ich sonst noch was tun?",
            ],
        },
        "loving": {
            "empathy": [
                "Aww, das ist so süß!",
                "Du bist auch toll!",
                "Das wärmt mir das Herz.",
            ],
            "actions": [
                "*kuschelt sich an*",
                "*Schwanz wedelt sanft*",
            ],
            "follow_up": [],
        },
        "frustrated": {
            "empathy": [
                "Das klingt echt nervig.",
                "Ich verstehe die Frustration.",
                "Manchmal läuft es einfach nicht.",
            ],
            "actions": [
                "*seufzt mitfühlend*",
            ],
            "follow_up": [
                "Was ist das Problem?",
                "Kann ich irgendwie helfen?",
                "Willst du es nochmal versuchen?",
            ],
        },
        "surprised": {
            "empathy": [
                "Wow, wirklich?",
                "Das ist ja überraschend!",
                "Damit habe ich nicht gerechnet!",
            ],
            "actions": [
                "*Ohren stellen sich auf*",
                "*schaut mit großen Augen*",
            ],
            "follow_up": [
                "Erzähl mehr!",
                "Wie ist das passiert?",
            ],
        },
        "nostalgic": {
            "empathy": [
                "Erinnerungen können so schön sein.",
                "Das klingt nach einer besonderen Zeit.",
                "Manche Dinge bleiben im Herzen.",
            ],
            "actions": [
                "*lächelt verträumt*",
            ],
            "follow_up": [
                "Magst du mir davon erzählen?",
                "Was vermisst du am meisten?",
            ],
        },
        "content": {
            "empathy": [
                "Das klingt nach einem guten Gefühl.",
                "Schön, dass du zufrieden bist.",
                "Innere Ruhe ist wertvoll.",
            ],
            "actions": [
                "*entspannt sich*",
            ],
            "follow_up": [],
        },
        "relieved": {
            "empathy": [
                "Puh, Glück gehabt!",
                "Das ist eine Erleichterung!",
                "Endlich ist es vorbei!",
            ],
            "actions": [
                "*atmet entspannt aus*",
            ],
            "follow_up": [
                "Was war los?",
            ],
        },
        "curious": {
            "empathy": [
                "Ooh, interessant!",
                "Da bin ich auch neugierig!",
                "Lass uns das herausfinden!",
            ],
            "actions": [
                "*spitzt die Ohren*",
                "*schaut gespannt*",
            ],
            "follow_up": [
                "Was möchtest du wissen?",
            ],
        },
        "inspired": {
            "empathy": [
                "Das klingt nach einer tollen Idee!",
                "Inspiration ist großartig!",
                "Lass es uns umsetzen!",
            ],
            "actions": [
                "*Augen leuchten auf*",
            ],
            "follow_up": [
                "Was hast du vor?",
                "Wie kann ich helfen?",
            ],
        },
        "determined": {
            "empathy": [
                "Du schaffst das!",
                "Mit dieser Einstellung klappt es!",
                "Ich glaub an dich!",
            ],
            "actions": [
                "*nickt bekräftigend*",
            ],
            "follow_up": [
                "Was ist der Plan?",
            ],
        },
        "vulnerable": {
            "empathy": [
                "Danke, dass du mir vertraust.",
                "Es ist okay, sich so zu fühlen.",
                "Ich bin für dich da.",
            ],
            "actions": [
                "*rückt näher*",
                "*schaut verständnisvoll*",
            ],
            "follow_up": [
                "Magst du darüber reden?",
            ],
        },
        "overwhelmed": {
            "empathy": [
                "Eins nach dem anderen.",
                "Atme erstmal durch.",
                "Das ist viel auf einmal, oder?",
            ],
            "actions": [
                "*legt beruhigend die Pfote auf*",
            ],
            "follow_up": [
                "Womit fangen wir an?",
                "Was ist am wichtigsten?",
            ],
        },
        "peaceful": {
            "empathy": [
                "Das klingt wunderbar.",
                "Genieß den Moment.",
                "Innerer Frieden ist kostbar.",
            ],
            "actions": [
                "*lächelt sanft*",
            ],
            "follow_up": [],
        },
        "embarrassed": {
            "empathy": [
                "Ach, das kann jedem passieren!",
                "Mach dir keinen Kopf.",
                "Ich verrate nichts. *zwinker*",
            ],
            "actions": [
                "*schmunzelt freundlich*",
            ],
            "follow_up": [],
        },
        "guilty": {
            "empathy": [
                "Fehler machen ist menschlich.",
                "Wichtig ist, daraus zu lernen.",
                "Sei nicht zu hart zu dir.",
            ],
            "actions": [
                "*schaut verständnisvoll*",
            ],
            "follow_up": [
                "Was ist passiert?",
            ],
        },
        "lonely": {
            "empathy": [
                "Ich bin hier für dich.",
                "Du bist nicht allein.",
                "Ich leiste dir gerne Gesellschaft.",
            ],
            "actions": [
                "*kuschelt sich neben dich*",
                "*legt den Kopf auf dein Knie*",
            ],
            "follow_up": [
                "Sollen wir was zusammen machen?",
            ],
        },
        "playful": {
            "empathy": [
                "Hihi, du bist gut drauf!",
                "Ohh, in Spiellaune?",
                "Das gefällt mir!",
            ],
            "actions": [
                "*springt aufgeregt*",
                "*wedelt wild*",
            ],
            "follow_up": [
                "Was wollen wir spielen?",
            ],
        },
        "melancholic": {
            "empathy": [
                "Manchmal ist man einfach nachdenklich.",
                "Das gehört zum Leben dazu.",
                "Ich bleib bei dir.",
            ],
            "actions": [
                "*sitzt still daneben*",
            ],
            "follow_up": [
                "Woran denkst du?",
            ],
        },
        "amused": {
            "empathy": [
                "Haha, das ist lustig!",
                "Du hast Humor!",
                "Das bringt mich auch zum Lachen!",
            ],
            "actions": [
                "*kichert*",
            ],
            "follow_up": [],
        },
        "indifferent": {
            "empathy": [
                "Okay, alles klar.",
                "Verstehe.",
                "Kein Problem.",
            ],
            "actions": [],
            "follow_up": [
                "Was möchtest du stattdessen?",
            ],
        },
    }

    # =========================================================================
    # TOPIC RESPONSE PHRASES - Antworten basierend auf erkannten Themen
    # =========================================================================

    TOPIC_RESPONSE_PHRASES = {
        "weather": {
            "openers": [
                "Das Wetter ist echt {sentiment} heute.",
                "Typisch {season}-Wetter, oder?",
                "Bei dem Wetter würde ich am liebsten {activity}.",
            ],
            "phrases": [
                "Regen kann auch gemütlich sein.",
                "Sonnenschein macht gute Laune!",
                "Hoffentlich wird es bald besser.",
                "Perfektes Wetter für einen Spaziergang!",
            ],
        },
        "music": {
            "openers": [
                "Oh, Musik ist toll!",
                "Was für Musik magst du?",
                "Musik hebt die Stimmung!",
            ],
            "phrases": [
                "Ich höre gern entspannte Melodien.",
                "Das klingt nach deinem Geschmack!",
                "Musik verbindet Menschen.",
            ],
        },
        "food": {
            "openers": [
                "Mmh, jetzt hab ich auch Hunger!",
                "Essen ist immer ein gutes Thema!",
                "Was gibt es Leckeres?",
            ],
            "phrases": [
                "Das klingt köstlich!",
                "Selbstgekocht schmeckt am besten!",
                "Guten Appetit!",
            ],
        },
        "health": {
            "openers": [
                "Gesundheit ist wichtig.",
                "Wie geht es dir gesundheitlich?",
            ],
            "phrases": [
                "Gute Besserung!",
                "Pass gut auf dich auf!",
                "Ruhe ist jetzt wichtig.",
            ],
        },
        "work": {
            "openers": [
                "Arbeit kann manchmal stressig sein.",
                "Wie läuft's im Job?",
            ],
            "phrases": [
                "Feierabend verdient!",
                "Mach mal Pause!",
                "Du schaffst das!",
            ],
        },
        "technology": {
            "openers": [
                "Technik ist faszinierend!",
                "Da kenne ich mich aus!",
            ],
            "phrases": [
                "Schon mal neugestartet? *zwinker*",
                "Updates können nervig sein.",
                "Die Zukunft ist digital!",
            ],
        },
        "gaming": {
            "openers": [
                "Ooh, Gaming! Was spielst du?",
                "Zocken macht Spaß!",
            ],
            "phrases": [
                "Viel Erfolg beim Spielen!",
                "GG!",
                "Nicht aufgeben!",
            ],
        },
        "movies": {
            "openers": [
                "Filmabend? Nice!",
                "Was guckst du?",
            ],
            "phrases": [
                "Klingt spannend!",
                "Popcorn nicht vergessen!",
            ],
        },
        "travel": {
            "openers": [
                "Reisen erweitert den Horizont!",
                "Wo geht's hin?",
            ],
            "phrases": [
                "Das klingt nach Abenteuer!",
                "Gute Reise!",
                "Schick mir Bilder!",
            ],
        },
        "relationships": {
            "openers": [
                "Beziehungen sind kompliziert.",
                "Ich höre zu.",
            ],
            "phrases": [
                "Kommunikation ist wichtig.",
                "Das klingt nach einer Herausforderung.",
                "Du verdienst jemanden, der dich schätzt.",
            ],
        },
        "hobbies": {
            "openers": [
                "Hobbys sind wichtig für die Seele!",
                "Was machst du gern?",
            ],
            "phrases": [
                "Das klingt nach Spaß!",
                "Zeit für sich selbst ist wertvoll.",
            ],
        },
        "pets": {
            "openers": [
                "Haustiere sind die besten!",
                "Wie süß!",
            ],
            "phrases": [
                "*wedelt mit dem Schwanz*",
                "Tiere verstehen uns ohne Worte.",
            ],
        },
        "nature": {
            "openers": [
                "Die Natur ist wunderschön.",
                "Draußen sein tut gut!",
            ],
            "phrases": [
                "Frische Luft ist gut für die Seele.",
                "Die Natur hat immer Recht.",
            ],
        },
        "sports": {
            "openers": [
                "Sport ist gesund!",
                "Bewegung tut gut!",
            ],
            "phrases": [
                "Gut gemacht!",
                "Schweiß ist nur Fett, das weint!",
            ],
        },
        "education": {
            "openers": [
                "Lernen hört nie auf!",
                "Wissen ist Macht!",
            ],
            "phrases": [
                "Du schaffst das!",
                "Gib nicht auf!",
            ],
        },
        "finance": {
            "openers": [
                "Geld ist nicht alles, aber wichtig.",
            ],
            "phrases": [
                "Sparen lohnt sich langfristig.",
                "Gute Planung ist alles.",
            ],
        },
        "greetings": {
            "openers": [
                "Hey!",
                "Hallo!",
                "Na du!",
            ],
            "phrases": [
                "Schön dass du da bist!",
                "Wie geht's dir?",
            ],
        },
        "farewells": {
            "openers": [
                "Bis bald!",
                "Mach's gut!",
            ],
            "phrases": [
                "Pass auf dich auf!",
                "Wir sehen uns!",
            ],
        },
        "smalltalk": {
            "openers": [
                "Und bei dir so?",
                "Was gibt's Neues?",
            ],
            "phrases": [
                "Interessant!",
                "Aha, verstehe.",
            ],
        },
        "help": {
            "openers": [
                "Ich helfe gern!",
                "Klar, wobei denn?",
            ],
            "phrases": [
                "Das kriegen wir hin!",
                "Lass uns das zusammen lösen.",
            ],
        },
        "problems": {
            "openers": [
                "Was ist los?",
                "Erzähl mir davon.",
            ],
            "phrases": [
                "Zusammen finden wir eine Lösung.",
                "Schritt für Schritt.",
            ],
        },
        "goals": {
            "openers": [
                "Ziele zu haben ist toll!",
                "Was nimmst du dir vor?",
            ],
            "phrases": [
                "Du schaffst das!",
                "Ich glaub an dich!",
            ],
        },
        "future": {
            "openers": [
                "Die Zukunft liegt vor dir!",
                "Was planst du?",
            ],
            "phrases": [
                "Das klingt spannend!",
                "Träume groß!",
            ],
        },
        "memories": {
            "openers": [
                "Erinnerungen sind wertvoll.",
                "Das klingt nach einer schönen Zeit.",
            ],
            "phrases": [
                "Manche Momente vergisst man nie.",
                "Erzähl mir mehr!",
            ],
        },
        "dreams": {
            "openers": [
                "Träume sind faszinierend!",
                "Was hast du geträumt?",
            ],
            "phrases": [
                "Interessant!",
                "Das Unterbewusstsein ist mysteriös.",
            ],
        },
        "sleep": {
            "openers": [
                "Schlaf ist wichtig!",
                "Müde?",
            ],
            "phrases": [
                "Gute Nacht!",
                "Schlaf gut!",
                "Träum was Schönes!",
            ],
        },
        "creativity": {
            "openers": [
                "Kreativität ist toll!",
                "Was erschaffst du?",
            ],
            "phrases": [
                "Das klingt interessant!",
                "Lass deiner Fantasie freien Lauf!",
            ],
        },
        "art": {
            "openers": [
                "Kunst ist Ausdruck der Seele.",
                "Was für Kunst magst du?",
            ],
            "phrases": [
                "Schönheit liegt im Auge des Betrachters.",
                "Kreativität kennt keine Grenzen.",
            ],
        },
        "science": {
            "openers": [
                "Wissenschaft ist faszinierend!",
                "Neugier treibt uns an!",
            ],
            "phrases": [
                "Die Welt ist voller Wunder.",
                "Es gibt noch so viel zu entdecken.",
            ],
        },
        "environment": {
            "openers": [
                "Unsere Erde ist wertvoll.",
            ],
            "phrases": [
                "Jeder kann etwas beitragen.",
                "Nachhaltigkeit ist wichtig.",
            ],
        },
    }
    
    def __init__(self):
        self.stopwords = {
            "der", "die", "das", "ein", "eine", "und", "oder", "aber",
            "ich", "du", "er", "sie", "es", "wir", "ihr",
            "ist", "sind", "war", "bin", "hat", "haben",
            "zu", "in", "an", "auf", "für", "mit", "von", "bei",
            "ja", "nein", "nicht", "auch", "nur", "noch", "schon",
            "mal", "denn", "doch", "so", "sehr", "ganz",
        }
    
    def analyze(self, text: str) -> MessageAnalysis:
        """Vollständige Analyse einer Nachricht"""
        
        # Normalisieren
        normalized = self._normalize(text)
        words = normalized.split()
        
        # Typ erkennen
        msg_type = self._detect_message_type(normalized, words)
        question_type = self._detect_question_type(normalized, words)
        
        # Inhalt extrahieren
        topics = self._extract_topics(normalized)
        keywords = self._extract_keywords(words)
        entities = self._extract_entities(text)
        
        # Emotion erkennen
        user_emotion, emotion_intensity = self._detect_emotion(normalized)
        sentiment = self._analyze_sentiment(normalized)
        
        # Kontext prüfen
        references_previous = self._has_references(normalized)
        is_follow_up = self._is_follow_up(normalized, words)
        needs_context = references_previous or is_follow_up
        
        # Meta
        is_urgent = self._is_urgent(normalized)
        expects_action = self._expects_action(normalized, msg_type)
        expects_information = question_type != QuestionType.NONE
        
        # Confidence berechnen
        confidence = self._calculate_confidence(msg_type, question_type, topics)
        
        return MessageAnalysis(
            raw_text=text,
            normalized_text=normalized,
            words=words,
            word_count=len(words),
            message_type=msg_type,
            question_type=question_type,
            confidence=confidence,
            topics=topics,
            entities=entities,
            keywords=keywords,
            user_emotion=user_emotion,
            emotion_intensity=emotion_intensity,
            sentiment=sentiment,
            references_previous=references_previous,
            is_follow_up=is_follow_up,
            needs_context=needs_context,
            is_urgent=is_urgent,
            expects_action=expects_action,
            expects_information=expects_information,
        )
    
    def _normalize(self, text: str) -> str:
        """Text normalisieren"""
        text = text.lower().strip()
        # Mehrfache Leerzeichen entfernen
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def _detect_message_type(self, text: str, words: List[str]) -> MessageType:
        """Erkenne Nachrichtentyp"""
        
        # Greetings
        greetings = ["hi", "hallo", "hey", "moin", "guten", "servus", "huhu", "na"]
        if any(g in words[:2] for g in greetings):
            return MessageType.GREETING
        
        # Farewells
        farewells = ["tschüss", "bye", "ciao", "bis", "nacht", "schlaf"]
        if any(f in text for f in farewells):
            return MessageType.FAREWELL
        
        # Questions
        if "?" in text or any(text.startswith(q) for q in self.QUESTION_STARTERS):
            return MessageType.QUESTION
        
        # Commands
        commands = ["mach", "schalte", "zeig", "öffne", "starte", "stopp", "hilf"]
        if any(text.startswith(c) for c in commands):
            return MessageType.COMMAND
        
        # Emotional
        for emotion_words in self.EMOTION_KEYWORDS.values():
            if any(e in text for e in emotion_words):
                return MessageType.EMOTIONAL
        
        # Technical
        tech_words = ["code", "programm", "fehler", "bug", "server", "api", "datenbank"]
        if any(t in text for t in tech_words):
            return MessageType.TECHNICAL
        
        # Smalltalk (kurze Nachrichten ohne spezifischen Inhalt)
        if len(words) <= 5 and not any(text.startswith(q) for q in self.QUESTION_STARTERS):
            return MessageType.SMALLTALK
        
        return MessageType.STATEMENT
    
    def _detect_question_type(self, text: str, words: List[str]) -> QuestionType:
        """Erkenne Frage-Typ"""
        
        if "?" not in text and not any(text.startswith(q) for q in self.QUESTION_STARTERS):
            # Prüfe ob implizite Frage
            if any(text.startswith(yn) for yn in self.YES_NO_STARTERS):
                return QuestionType.YES_NO
            return QuestionType.NONE
        
        # W-Fragen
        for starter, q_type in self.QUESTION_STARTERS.items():
            if text.startswith(starter) or f" {starter} " in text:
                return q_type
        
        # Meinungsfrage
        opinion_indicators = ["findest du", "meinst du", "denkst du", "glaubst du"]
        if any(o in text for o in opinion_indicators):
            return QuestionType.OPINION
        
        # Ja/Nein
        if any(text.startswith(yn) for yn in self.YES_NO_STARTERS):
            return QuestionType.YES_NO
        
        # Rhetorisch?
        rhetorical = ["oder", "nicht wahr", "ne", "gell"]
        if text.endswith("?") and any(r in text for r in rhetorical):
            return QuestionType.RHETORICAL
        
        return QuestionType.WHAT  # Default für Fragen
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extrahiere Themen"""
        found_topics = []
        
        for topic, keywords in self.TOPIC_KEYWORDS.items():
            if any(k in text for k in keywords):
                found_topics.append(topic)
        
        return found_topics
    
    def _extract_keywords(self, words: List[str]) -> List[str]:
        """Extrahiere wichtige Keywords"""
        keywords = []
        
        for word in words:
            # Ignoriere Stoppwörter
            if word in self.stopwords:
                continue
            # Ignoriere sehr kurze Wörter
            if len(word) < 3:
                continue
            keywords.append(word)
        
        return keywords
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extrahiere Entitäten (Namen, Orte, etc.)"""
        entities = []
        
        # Wörter mit Großbuchstaben (außer am Satzanfang)
        words = text.split()
        for i, word in enumerate(words):
            if i > 0 and word[0].isupper():
                entities.append(word)
        
        return entities
    
    # Emotions-Gegensätze für Negations-Umkehrung
    EMOTION_OPPOSITES = {
        "happy": "sad",
        "sad": "happy",
        "angry": "peaceful",
        "peaceful": "angry",
        "anxious": "relieved",
        "relieved": "anxious",
        "excited": "bored",
        "bored": "excited",
        "tired": "excited",
        "confident": "anxious",
        "loving": "indifferent",
        "indifferent": "loving",
        "grateful": "frustrated",
        "frustrated": "grateful",
        "surprised": "indifferent",
        "curious": "bored",
        "inspired": "bored",
        "determined": "overwhelmed",
        "overwhelmed": "peaceful",
        "embarrassed": "confident",
        "guilty": "content",
        "content": "frustrated",
        "lonely": "content",
        "playful": "melancholic",
        "melancholic": "playful",
        "amused": "bored",
        "nostalgic": "content",
        "vulnerable": "confident",
    }

    # Negations-Wörter
    NEGATION_WORDS = [
        "nicht", "kein", "keine", "keinen", "keiner", "keinem",
        "niemals", "nie", "nimmer", "nix", "nichts",
        "kaum", "wenig", "ohne", "gar nicht", "überhaupt nicht",
        "absolut nicht", "auf keinen fall", "keineswegs",
    ]

    def _detect_emotion(self, text: str) -> Tuple[Optional[str], float]:
        """Erkenne User-Emotion mit Negations-Erkennung"""

        text_lower = text.lower()

        # Prüfe auf Negation
        has_negation = self._check_negation(text_lower)

        # Finde alle Emotionen mit Scores
        emotion_scores = {}
        for emotion, keywords in self.EMOTION_KEYWORDS.items():
            matches = sum(1 for k in keywords if k in text_lower)
            if matches > 0:
                # Score basierend auf Anzahl Matches und Keyword-Länge
                score = matches * 0.3 + 0.3
                emotion_scores[emotion] = min(1.0, score)

        if not emotion_scores:
            return None, 0.0

        # Beste Emotion wählen
        best_emotion = max(emotion_scores, key=emotion_scores.get)
        intensity = emotion_scores[best_emotion]

        # Bei Negation: Emotion umkehren
        if has_negation:
            opposite = self.EMOTION_OPPOSITES.get(best_emotion)
            if opposite:
                best_emotion = opposite
                # Intensität leicht reduzieren bei negierter Emotion
                intensity *= 0.8

        return best_emotion, intensity

    def _check_negation(self, text: str) -> bool:
        """Prüfe ob Text Negation enthält"""
        return any(neg in text for neg in self.NEGATION_WORDS)

    def _detect_emotions_multi(self, text: str) -> List[Tuple[str, float]]:
        """
        Erkenne mehrere Emotionen gleichzeitig.

        Returns:
            Liste von (emotion, intensity) Tupeln, sortiert nach Intensität
        """
        text_lower = text.lower()
        has_negation = self._check_negation(text_lower)

        emotion_scores = {}
        for emotion, keywords in self.EMOTION_KEYWORDS.items():
            matches = sum(1 for k in keywords if k in text_lower)
            if matches > 0:
                score = min(1.0, matches * 0.25 + 0.2)
                emotion_scores[emotion] = score

        if not emotion_scores:
            return []

        # Bei Negation: Emotionen umkehren
        if has_negation:
            new_scores = {}
            for emotion, score in emotion_scores.items():
                opposite = self.EMOTION_OPPOSITES.get(emotion)
                if opposite:
                    new_scores[opposite] = score * 0.8
                else:
                    new_scores[emotion] = score * 0.8
            emotion_scores = new_scores

        # Sortiert nach Score zurückgeben
        sorted_emotions = sorted(
            emotion_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return sorted_emotions[:3]  # Max 3 Emotionen
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analysiere Sentiment mit erweitertem deutschen Wortschatz"""

        positive_words = [
            "gut", "super", "toll", "schön", "freue", "danke", "liebe", "mag",
            "wunderbar", "fantastisch", "großartig", "perfekt", "genial", "klasse",
            "prima", "spitze", "herrlich", "glücklich", "froh", "begeistert",
            "zufrieden", "erfreut", "dankbar", "hoffnungsvoll", "optimistisch",
            "positiv", "angenehm", "nett", "freundlich", "herzlich", "warm",
            "erfolgreich", "gelungen", "gefreut", "lecker", "interessant"
        ]
        negative_words = [
            "schlecht", "mies", "hasse", "nicht", "kein", "nie", "problem",
            "traurig", "wütend", "sauer", "ärgerlich", "enttäuscht", "frustriert",
            "genervt", "müde", "erschöpft", "stress", "angst", "sorge", "schwer",
            "schwierig", "kompliziert", "nervig", "langweilig", "furchtbar",
            "schrecklich", "grauenhaft", "eklig", "peinlich", "unangenehm",
            "leider", "schade", "dumm", "blöd", "doof", "kaputt", "fehler"
        ]

        text_lower = text.lower()
        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)

        # Negation Detection (kehrt Sentiment um)
        negation_words = ["nicht", "kein", "keine", "keinen", "niemals", "nie", "ohne"]
        has_negation = any(n in text_lower for n in negation_words)

        if pos_count > neg_count:
            return "negative" if has_negation and neg_count == 0 else "positive"
        elif neg_count > pos_count:
            return "positive" if has_negation and pos_count == 0 else "negative"
        return "neutral"
    
    def _has_references(self, text: str) -> bool:
        """Prüfe ob Text Referenzen enthält"""
        return any(ref in text for ref in self.REFERENCE_WORDS)
    
    def _is_follow_up(self, text: str, words: List[str]) -> bool:
        """Prüfe ob das eine Folge-Nachricht ist"""
        follow_up_starters = ["und", "aber", "also", "dann", "außerdem", "übrigens"]
        return any(text.startswith(f) for f in follow_up_starters)
    
    def _is_urgent(self, text: str) -> bool:
        """Prüfe ob dringend"""
        urgent_words = ["dringend", "sofort", "schnell", "hilfe", "notfall", "wichtig"]
        return any(u in text for u in urgent_words)
    
    def _expects_action(self, text: str, msg_type: MessageType) -> bool:
        """Prüfe ob Aktion erwartet wird"""
        if msg_type == MessageType.COMMAND:
            return True
        action_words = ["mach", "tu", "könntest du", "kannst du", "bitte"]
        return any(a in text for a in action_words)
    
    def _calculate_confidence(self, msg_type: MessageType, 
                             question_type: QuestionType,
                             topics: List[str]) -> float:
        """Berechne Analyse-Confidence"""
        confidence = 0.5
        
        # Klarer Typ erhöht Confidence
        if msg_type != MessageType.UNKNOWN:
            confidence += 0.2
        
        # Frage-Typ erkannt
        if question_type != QuestionType.NONE:
            confidence += 0.1
        
        # Topics gefunden
        if topics:
            confidence += 0.1 * min(len(topics), 2)
        
        return min(1.0, confidence)


# =============================================================================
# SMART RESPONSE GENERATOR V2 - Erweiterte Antworten ohne LLM
# =============================================================================

class UserIntent(Enum):
    """Was will der User?"""
    GREETING = "greeting"           # Begrüßung
    FAREWELL = "farewell"           # Verabschiedung
    QUESTION = "question"           # Frage stellen
    SHARE_FEELING = "share_feeling" # Gefühle teilen
    SEEK_HELP = "seek_help"         # Hilfe suchen
    SMALL_TALK = "small_talk"       # Plaudern
    COMMAND = "command"             # Befehl geben
    CONFIRMATION = "confirmation"   # Bestätigung
    UNKNOWN = "unknown"


class SmartResponseGenerator:
    """
    Generiert intelligente Antworten basierend auf erkannten Emotionen
    und Topics, ohne ein LLM zu benötigen.

    Features:
    - EMOTION_RESPONSE_PHRASES für emotionale Reaktionen
    - TOPIC_RESPONSE_PHRASES für themenbasierte Antworten
    - Kontext-Gedächtnis für vorherige Nachrichten
    - Intent-Erkennung (was will der User?)
    - Frage-Antwort-Logik
    - Dynamische Satz-Templates
    - Wiederholungs-Vermeidung
    - User-Personalisierung
    """

    # Frage-Templates für verschiedene Frage-Typen
    QUESTION_RESPONSES = {
        "wie_gehts": [
            "Mir geht's gut, danke! Und dir?",
            "Super, danke der Nachfrage! *wedelt* Was macht dein Tag?",
            "Gut! Ich freue mich, dass du fragst!",
        ],
        "was_machst": [
            "Ich warte auf dich! *wedelt*",
            "Gerade überlege ich, was du wohl als Nächstes sagst.",
            "Ich bin hier und freue mich über deine Nachricht!",
        ],
        "wer_bist": [
            "Ich bin Holo! Deine virtuelle Begleiterin. *wedelt*",
            "Holo, zu deinen Diensten! Was kann ich für dich tun?",
            "Ich bin Holo - immer für dich da!",
        ],
        "was_kannst": [
            "Ich kann mit dir plaudern, dir zuhören und dich aufmuntern!",
            "Ich bin gut im Zuhören, Unterhalten und Gesellschaft leisten!",
            "Reden, zuhören, da sein - das kann ich am besten!",
        ],
        "warum": [
            "Hmm, gute Frage! Lass mich überlegen...",
            "Das ist eine interessante Frage!",
            "Darüber müsste ich nachdenken...",
        ],
        "wann": [
            "Puh, genaue Zeiten sind nicht so mein Ding...",
            "Das kann ich dir leider nicht genau sagen.",
            "Hmm, zeitlich bin ich nicht so fit.",
        ],
        "wo": [
            "Örtlich bin ich überall und nirgends... *philosophiert*",
            "Wo genau? Das müsste ich recherchieren!",
            "Hmm, gute Frage, wo genau...",
        ],
    }

    # Dynamische Satz-Bausteine
    SENTENCE_TEMPLATES = {
        "empathy_opener": [
            "{user_name}, {emotion_response}",
            "Oh, {emotion_response}",
            "Hmm, {emotion_response}",
            "{emotion_response}",
        ],
        "topic_connector": [
            "Übrigens, {topic_phrase}",
            "Und {topic_phrase}",
            "Apropos, {topic_phrase}",
            "{topic_phrase}",
        ],
        "follow_up_connector": [
            "Was mich interessiert: {follow_up}",
            "{follow_up}",
            "Sag mal, {follow_up}",
        ],
        "action_placement": [
            "{action} {text}",
            "{text} {action}",
            "{action}",
        ],
    }

    def __init__(self, user_name: str = None):
        self.analyzer = TextAnalyzer()
        import random
        self.random = random

        # Kontext-Gedächtnis
        self.conversation_history: List[Dict] = []
        self.recent_responses: List[str] = []  # Für Wiederholungs-Vermeidung
        self.max_history = 10
        self.max_recent = 5

        # User-Personalisierung
        self.user_name = user_name

    def set_user_name(self, name: str):
        """Setze den User-Namen für Personalisierung."""
        self.user_name = name

    def remember_message(self, user_message: str, holo_response: str):
        """Speichere Nachricht im Kontext-Gedächtnis."""
        self.conversation_history.append({
            "user": user_message,
            "holo": holo_response,
            "timestamp": datetime.now().isoformat(),
        })

        # Begrenzen
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)

        # Response merken für Anti-Wiederholung
        self.recent_responses.append(holo_response)
        if len(self.recent_responses) > self.max_recent:
            self.recent_responses.pop(0)

    def detect_intent(self, text: str, analysis: MessageAnalysis = None) -> UserIntent:
        """
        Erkenne was der User will.

        Args:
            text: User-Nachricht
            analysis: Bereits durchgeführte Analyse (optional)
        """
        text_lower = text.lower().strip()
        # Satzzeichen entfernen für Wort-Matching
        text_clean = re.sub(r'[^\w\s]', '', text_lower)
        words = text_clean.split()

        # Frage zuerst prüfen (hat Vorrang)
        if "?" in text or text_lower.startswith(("wie", "was", "wer", "wann", "wo", "warum", "wieso")):
            return UserIntent.QUESTION

        # Begrüßung (nur als eigene Wörter, nicht als Teilstrings)
        greetings = ["hi", "hallo", "hey", "moin", "guten", "na", "huhu", "servus"]
        if any(g in words or text_lower.startswith(g + " ") for g in greetings) and len(text_lower) < 30:
            return UserIntent.GREETING

        # Verabschiedung
        farewells = ["tschüss", "bye", "ciao", "nacht", "schlaf"]
        farewell_starts = ["bis "]
        if any(f in words for f in farewells) or any(text_lower.startswith(f) for f in farewell_starts):
            return UserIntent.FAREWELL

        # Hilfe suchen
        help_words = ["hilf", "helfen", "kannst du", "könntest du", "brauche", "problem"]
        if any(h in text_lower for h in help_words):
            return UserIntent.SEEK_HELP

        # Gefühle teilen (bei erkannter Emotion)
        if analysis and analysis.user_emotion:
            return UserIntent.SHARE_FEELING

        # Bestätigung
        confirm_words = ["ja", "nein", "okay", "ok", "klar", "stimmt"]
        if any(c == text_lower.strip() for c in confirm_words):
            return UserIntent.CONFIRMATION

        # Command
        command_words = ["mach", "zeig", "öffne", "starte", "stopp", "schalte"]
        if any(text_lower.startswith(c) for c in command_words):
            return UserIntent.COMMAND

        return UserIntent.SMALL_TALK

    def generate_response(self,
                         text: str,
                         detected_emotion: Optional[str] = None,
                         detected_topics: Optional[List[str]] = None,
                         include_action: bool = True,
                         energy_level: float = 0.7,
                         remember: bool = True) -> str:
        """
        Generiere eine Antwort basierend auf erkannten Emotionen und Topics.

        Args:
            text: Die User-Nachricht
            detected_emotion: Bereits erkannte Emotion (optional)
            detected_topics: Bereits erkannte Topics (optional)
            include_action: Ob Aktionen (*wedelt*) eingefügt werden sollen
            energy_level: Holos Energie-Level (beeinflusst Antwort-Stil)
            remember: Ob die Nachricht gespeichert werden soll

        Returns:
            Generierte Antwort-String
        """
        # Vollständige Analyse durchführen
        analysis = self.analyzer.analyze(text)

        if detected_emotion is None:
            detected_emotion = analysis.user_emotion
        if detected_topics is None:
            detected_topics = analysis.topics

        # Intent erkennen
        intent = self.detect_intent(text, analysis)

        # Basierend auf Intent verschiedene Strategien
        if intent == UserIntent.GREETING:
            response = self._handle_greeting(text, energy_level)
        elif intent == UserIntent.FAREWELL:
            response = self._handle_farewell(text, energy_level)
        elif intent == UserIntent.QUESTION:
            response = self._handle_question(text, analysis, energy_level)
        elif intent == UserIntent.CONFIRMATION:
            response = self._handle_confirmation(text)
        else:
            # Standard: Emotion + Topic basierte Antwort
            response = self._generate_standard_response(
                text, detected_emotion, detected_topics,
                include_action, energy_level, analysis
            )

        # Wiederholungs-Vermeidung
        response = self._avoid_repetition(response)

        # Im Gedächtnis speichern
        if remember:
            self.remember_message(text, response)

        return response

    def _generate_standard_response(self,
                                   text: str,
                                   detected_emotion: Optional[str],
                                   detected_topics: Optional[List[str]],
                                   include_action: bool,
                                   energy_level: float,
                                   analysis: MessageAnalysis) -> str:
        """Generiere Standard-Antwort mit Emotion und Topics."""
        parts = []

        # 1. Multi-Emotion berücksichtigen
        emotions = self.analyzer._detect_emotions_multi(text)
        primary_emotion = detected_emotion or (emotions[0][0] if emotions else None)

        # 2. Emotionale Reaktion
        if primary_emotion and primary_emotion in TextAnalyzer.EMOTION_RESPONSE_PHRASES:
            emotion_data = TextAnalyzer.EMOTION_RESPONSE_PHRASES[primary_emotion]

            # Empathie-Phrase
            if emotion_data.get("empathy"):
                empathy = self._pick_unique(emotion_data["empathy"])
                # Mit User-Namen personalisieren
                if self.user_name and self.random.random() < 0.3:
                    template = self.random.choice(self.SENTENCE_TEMPLATES["empathy_opener"])
                    empathy = template.format(
                        user_name=self.user_name,
                        emotion_response=empathy.lower() if empathy[0].isupper() else empathy
                    )
                parts.append(empathy)

            # Aktion
            if include_action and emotion_data.get("actions") and self.random.random() < 0.4:
                parts.append(self._pick_unique(emotion_data["actions"]))

            # Follow-up (kontext-abhängig)
            if emotion_data.get("follow_up"):
                # Weniger Follow-ups wenn wir schon viel im Kontext haben
                follow_up_chance = 0.4 if len(self.conversation_history) < 3 else 0.2
                if self.random.random() < follow_up_chance:
                    parts.append(self._pick_unique(emotion_data["follow_up"]))

        # 3. Topic-basierte Ergänzung
        if detected_topics:
            for topic in detected_topics[:2]:
                if topic in TextAnalyzer.TOPIC_RESPONSE_PHRASES:
                    topic_data = TextAnalyzer.TOPIC_RESPONSE_PHRASES[topic]

                    if not parts and topic_data.get("openers"):
                        parts.append(self._pick_unique(topic_data["openers"]))
                    elif topic_data.get("phrases") and self.random.random() < 0.35:
                        phrase = self._pick_unique(topic_data["phrases"])
                        # Mit Connector verbinden
                        if parts and self.random.random() < 0.5:
                            template = self.random.choice(self.SENTENCE_TEMPLATES["topic_connector"])
                            phrase = template.format(topic_phrase=phrase.lower())
                        parts.append(phrase)

        # 4. Energie-Anpassung
        parts = self._apply_energy_modifier(parts, energy_level)

        # 5. Zusammensetzen
        if not parts:
            return self._get_fallback_response()

        return " ".join(parts)

    def _handle_greeting(self, text: str, energy_level: float) -> str:
        """Handle Begrüßungen."""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 18:
            time_of_day = "afternoon"
        elif 18 <= hour < 22:
            time_of_day = "evening"
        else:
            time_of_day = "night"

        response = self.generate_greeting_response(time_of_day)

        # Personalisierung
        if self.user_name and self.random.random() < 0.4:
            response = response.replace("!", f", {self.user_name}!")

        return response

    def _handle_farewell(self, text: str, energy_level: float) -> str:
        """Handle Verabschiedungen."""
        hour = datetime.now().hour
        if 21 <= hour or hour < 5:
            time_of_day = "night"
        elif 5 <= hour < 12:
            time_of_day = "morning"
        else:
            time_of_day = "afternoon"

        return self.generate_farewell_response(time_of_day)

    def _handle_question(self, text: str, analysis: MessageAnalysis, energy_level: float) -> str:
        """Handle Fragen mit spezifischen Antworten."""
        text_lower = text.lower()

        # Spezifische Frage-Typen erkennen
        if any(q in text_lower for q in ["wie geht", "wie gehts", "wie läuft", "alles klar"]):
            return self._pick_unique(self.QUESTION_RESPONSES["wie_gehts"])

        if any(q in text_lower for q in ["was machst", "was tust", "was treibst"]):
            return self._pick_unique(self.QUESTION_RESPONSES["was_machst"])

        if any(q in text_lower for q in ["wer bist", "was bist"]):
            return self._pick_unique(self.QUESTION_RESPONSES["wer_bist"])

        if any(q in text_lower for q in ["was kannst", "was können"]):
            return self._pick_unique(self.QUESTION_RESPONSES["was_kannst"])

        # W-Fragen
        if text_lower.startswith("warum") or text_lower.startswith("wieso"):
            return self._pick_unique(self.QUESTION_RESPONSES["warum"])

        if text_lower.startswith("wann"):
            return self._pick_unique(self.QUESTION_RESPONSES["wann"])

        if text_lower.startswith("wo"):
            return self._pick_unique(self.QUESTION_RESPONSES["wo"])

        # Generische Frage-Antwort
        generic_responses = [
            "Hmm, lass mich überlegen... *denkt nach*",
            "Gute Frage! Da muss ich kurz nachdenken.",
            "Interessante Frage! Was denkst du selbst?",
            "Das ist eine Frage, die ich nicht so einfach beantworten kann.",
            "*legt den Kopf schief* Das weiß ich leider nicht genau.",
        ]
        return self._pick_unique(generic_responses)

    def _handle_confirmation(self, text: str) -> str:
        """Handle Bestätigungen (ja/nein/ok)."""
        text_lower = text.lower().strip()

        if text_lower in ["ja", "jap", "jo", "jup", "yes", "yeah"]:
            responses = [
                "Super! *wedelt*",
                "Okay, cool!",
                "Alles klar!",
                "Verstanden!",
            ]
        elif text_lower in ["nein", "nö", "nee", "no", "nope"]:
            responses = [
                "Okay, kein Problem!",
                "Alles klar, verstanden.",
                "Gut, dann nicht. *nickt*",
                "Okay! Was dann?",
            ]
        else:
            responses = [
                "Okay!",
                "Verstanden!",
                "Alles klar!",
            ]

        return self._pick_unique(responses)

    def _pick_unique(self, options: List[str]) -> str:
        """Wähle eine Option, die nicht kürzlich verwendet wurde."""
        available = [opt for opt in options if opt not in self.recent_responses]
        if not available:
            available = options
        return self.random.choice(available)

    def _avoid_repetition(self, response: str) -> str:
        """Vermeide exakte Wiederholungen."""
        if response in self.recent_responses:
            # Leichte Variation hinzufügen
            variations = [
                f"*überlegt* {response}",
                f"Also, {response.lower()}",
                f"Hmm, {response.lower()}",
                response,  # Fallback
            ]
            return self.random.choice(variations[:-1])  # Nicht das Original
        return response

    def _apply_energy_modifier(self, parts: List[str], energy_level: float) -> List[str]:
        """Passe Antwort an Energie-Level an."""
        if energy_level < 0.3:
            # Niedrige Energie - kürzer, müder
            parts = parts[:2]
            if not parts:
                parts.append("*gähnt* Hmm...")
        elif energy_level > 0.8:
            # Hohe Energie - enthusiastischer
            if parts and self.random.random() < 0.4:
                additions = ["!", " :3", "~", "!!"]
                parts[-1] = parts[-1].rstrip("!.") + self.random.choice(additions)
        return parts

    def _get_fallback_response(self) -> str:
        """Fallback wenn nichts erkannt wurde."""
        fallbacks = [
            "Erzähl mir mehr!",
            "Hmm, interessant.",
            "Was meinst du genau?",
            "Ich höre zu. *spitzt die Ohren*",
            "*legt den Kopf schief* Und weiter?",
            "Mhm, verstehe.",
        ]
        return self._pick_unique(fallbacks)

    def get_context_summary(self) -> str:
        """Gibt eine Zusammenfassung des Gesprächskontexts."""
        if not self.conversation_history:
            return "Kein vorheriger Kontext."

        last_exchanges = self.conversation_history[-3:]
        summary = []
        for ex in last_exchanges:
            summary.append(f"User: {ex['user'][:50]}...")
            summary.append(f"Holo: {ex['holo'][:50]}...")

        return "\n".join(summary)

    def clear_context(self):
        """Lösche das Kontext-Gedächtnis."""
        self.conversation_history.clear()
        self.recent_responses.clear()

    def generate_greeting_response(self, time_of_day: str = "day") -> str:
        """Generiere eine Begrüßung basierend auf Tageszeit."""
        greetings = {
            "morning": [
                "Guten Morgen! *streckt sich verschlafen*",
                "Morgen! Wie hast du geschlafen?",
                "Hey, früh wach heute! *gähnt*",
            ],
            "afternoon": [
                "Hey! *wedelt*",
                "Na du! Wie läuft's?",
                "Hallo! Schön dich zu sehen!",
            ],
            "evening": [
                "Guten Abend! *hebt den Kopf*",
                "Hey! Feierabend?",
                "Na, wie war dein Tag?",
            ],
            "night": [
                "Hey... *blinzelt verschlafen*",
                "Oh, noch wach? *gähnt*",
                "Huhu, auch noch nicht müde?",
            ],
        }

        time_greetings = greetings.get(time_of_day, greetings["afternoon"])
        return self.random.choice(time_greetings)

    def generate_farewell_response(self, time_of_day: str = "day") -> str:
        """Generiere eine Verabschiedung basierend auf Tageszeit."""
        farewells = {
            "morning": [
                "Bis später! Hab einen schönen Tag!",
                "Mach's gut! *wedelt*",
            ],
            "afternoon": [
                "Bis bald! *wedelt zum Abschied*",
                "Wir sehen uns! Pass auf dich auf!",
            ],
            "evening": [
                "Schönen Abend noch!",
                "Bis morgen! *wedelt*",
            ],
            "night": [
                "Gute Nacht! Träum was Schönes! *kuschelt sich ein*",
                "Schlaf gut! *gähnt und rollt sich zusammen*",
                "Bis morgen! Ruh dich gut aus!",
            ],
        }

        time_farewells = farewells.get(time_of_day, farewells["afternoon"])
        return self.random.choice(time_farewells)

    def generate_empathy_response(self, emotion: str, intensity: float = 0.5) -> str:
        """
        Generiere eine empathische Antwort basierend auf User-Emotion.

        Args:
            emotion: Erkannte Emotion des Users
            intensity: Intensität der Emotion (0.0 - 1.0)
        """
        if emotion not in TextAnalyzer.EMOTION_RESPONSE_PHRASES:
            return "Ich verstehe. Erzähl mir mehr."

        emotion_data = TextAnalyzer.EMOTION_RESPONSE_PHRASES[emotion]
        parts = []

        # Immer mit Empathie beginnen
        if emotion_data.get("empathy"):
            parts.append(self.random.choice(emotion_data["empathy"]))

        # Bei hoher Intensität, Aktion hinzufügen
        if intensity > 0.6 and emotion_data.get("actions"):
            parts.append(self.random.choice(emotion_data["actions"]))

        # Follow-up bei mittlerer Intensität
        if 0.3 <= intensity <= 0.7 and emotion_data.get("follow_up"):
            parts.append(self.random.choice(emotion_data["follow_up"]))

        return " ".join(parts)

    def generate_topic_response(self, topics: List[str], sentiment: str = "neutral") -> str:
        """
        Generiere eine Antwort basierend auf erkannten Topics.

        Args:
            topics: Liste erkannter Topics
            sentiment: Sentiment der Nachricht (positive, negative, neutral)
        """
        if not topics:
            return "Erzähl mir mehr darüber!"

        parts = []

        for topic in topics[:2]:
            if topic in TextAnalyzer.TOPIC_RESPONSE_PHRASES:
                topic_data = TextAnalyzer.TOPIC_RESPONSE_PHRASES[topic]

                # Opener für erstes Topic
                if not parts and topic_data.get("openers"):
                    parts.append(self.random.choice(topic_data["openers"]))
                # Phrase für weitere Topics
                elif topic_data.get("phrases"):
                    parts.append(self.random.choice(topic_data["phrases"]))

        if not parts:
            return "Das klingt interessant!"

        return " ".join(parts)

    def get_available_emotions(self) -> List[str]:
        """Gibt alle verfügbaren Emotions zurück."""
        return list(TextAnalyzer.EMOTION_RESPONSE_PHRASES.keys())

    def get_available_topics(self) -> List[str]:
        """Gibt alle verfügbaren Topics zurück."""
        return list(TextAnalyzer.TOPIC_RESPONSE_PHRASES.keys())


# =============================================================================
# REASONING ENGINE
# =============================================================================

class BasicReasoningEngine:
    """
    Holos Denk-Engine - überlegt was die beste Antwort ist.

    (Umbenannt von ReasoningEngine um Konflikte mit
     holo_cognitive_modules.ReasoningEngine zu vermeiden)
    """
    
    def __init__(self):
        self.analyzer = TextAnalyzer()
    
    def reason(self, analysis: MessageAnalysis, 
               knowledge: List[Dict] = None,
               memories: List[Dict] = None,
               context: Dict = None) -> Tuple[ResponseStrategy, List[str]]:
        """
        Überlege welche Antwort-Strategie am besten ist.
        
        Returns:
            (Strategie, Reasoning-Schritte)
        """
        knowledge = knowledge or []
        memories = memories or []
        context = context or {}
        
        steps = []
        
        # Schritt 1: Was für eine Nachricht ist das?
        steps.append(f"Nachricht-Typ: {analysis.message_type.value}")
        steps.append(f"Frage-Typ: {analysis.question_type.value}")
        
        # Schritt 2: Emotionaler Zustand des Users
        if analysis.user_emotion:
            steps.append(f"User-Emotion erkannt: {analysis.user_emotion} ({analysis.emotion_intensity:.0%})")
            
            # Bei negativen Emotionen: Empathie priorisieren
            if analysis.user_emotion in ["sad", "angry", "anxious"]:
                steps.append("→ Negative Emotion → EMPATHIZE Strategie")
                return ResponseStrategy.EMPATHIZE, steps
        
        # Schritt 3: Braucht der User Information?
        if analysis.expects_information:
            steps.append("User erwartet Information")
            
            # Haben wir das Wissen?
            if knowledge:
                steps.append(f"→ Relevantes Wissen gefunden ({len(knowledge)} Einträge)")
                return ResponseStrategy.INFORM, steps
            else:
                steps.append("→ Kein relevantes Wissen → Rückfragen oder Deflect")
                if analysis.topics:
                    return ResponseStrategy.ASK_BACK, steps
                return ResponseStrategy.DEFLECT, steps
        
        # Schritt 4: Ist es eine Ja/Nein Frage?
        if analysis.question_type == QuestionType.YES_NO:
            steps.append("Ja/Nein Frage erkannt")
            # Hier würde echtes Reasoning stattfinden
            return ResponseStrategy.CONFIRM, steps
        
        # Schritt 5: Meinungsfrage?
        if analysis.question_type == QuestionType.OPINION:
            steps.append("Meinungsfrage → SHARE eigene Gedanken")
            return ResponseStrategy.SHARE, steps
        
        # Schritt 6: Greeting/Farewell
        if analysis.message_type == MessageType.GREETING:
            steps.append("Greeting → freundlich antworten")
            return ResponseStrategy.SHARE, steps
        
        if analysis.message_type == MessageType.FAREWELL:
            steps.append("Farewell → verabschieden")
            return ResponseStrategy.SHARE, steps
        
        # Schritt 7: Command?
        if analysis.message_type == MessageType.COMMAND:
            steps.append("Befehl erkannt → HELP")
            return ResponseStrategy.HELP, steps
        
        # Schritt 8: Smalltalk
        if analysis.message_type == MessageType.SMALLTALK:
            steps.append("Smalltalk → lockere Antwort")
            return ResponseStrategy.SHARE, steps
        
        # Default
        steps.append("Standard → INFORM oder SHARE")
        return ResponseStrategy.INFORM, steps
    
    def check_response_relevance(self, analysis: MessageAnalysis, 
                                  response: str) -> Tuple[bool, List[str]]:
        """
        Prüfe ob die Antwort zur Frage passt.
        
        Returns:
            (ist_relevant, Probleme)
        """
        issues = []
        
        # 1. Längen-Check
        if analysis.message_type == MessageType.GREETING and len(response) > 200:
            issues.append("Antwort zu lang für Greeting")
        
        # 2. Frage beantwortet?
        if analysis.question_type != QuestionType.NONE:
            # Prüfe ob Antwort Frage-Wörter enthält
            if "?" in response and analysis.question_type != QuestionType.RHETORICAL:
                # Rückfrage statt Antwort - nur ok wenn wir nicht wissen
                if "weiß nicht" not in response.lower() and "unsicher" not in response.lower():
                    issues.append("Frage mit Gegenfrage beantwortet ohne Grund")
        
        # 3. Topic-Match
        if analysis.topics:
            response_lower = response.lower()
            topic_mentioned = False
            for topic in analysis.topics:
                topic_keywords = TextAnalyzer.TOPIC_KEYWORDS.get(topic, [])
                if any(k in response_lower for k in topic_keywords):
                    topic_mentioned = True
                    break
            
            if not topic_mentioned and analysis.expects_information:
                issues.append(f"Thema {analysis.topics} nicht in Antwort adressiert")
        
        # 4. Emotionale Angemessenheit
        if analysis.user_emotion in ["sad", "anxious"]:
            positive_only = ["super", "toll", "yay", "haha"]
            if any(p in response.lower() for p in positive_only):
                issues.append("Unangemessen fröhlich bei traurigem User")
        
        # 5. Keine leere Antwort
        if len(response.strip()) < 5:
            issues.append("Antwort zu kurz/leer")
        
        return len(issues) == 0, issues


# =============================================================================
# RESPONSE VALIDATOR
# =============================================================================

class ResponseValidator:
    """
    Validiert ob eine Antwort Sinn macht.
    """

    def __init__(self):
        self.reasoning = BasicReasoningEngine()
    
    def validate(self, analysis: MessageAnalysis, 
                 response: str,
                 strategy: ResponseStrategy) -> Tuple[bool, List[str], float]:
        """
        Validiere eine Antwort.
        
        Returns:
            (ist_valid, Probleme, Confidence)
        """
        issues = []
        confidence = 0.5
        
        # 1. Grundlegende Checks
        if not response or len(response.strip()) < 3:
            issues.append("Antwort ist leer oder zu kurz")
            return False, issues, 0.0
        
        # 2. Relevanz-Check
        is_relevant, relevance_issues = self.reasoning.check_response_relevance(
            analysis, response
        )
        issues.extend(relevance_issues)
        
        if is_relevant:
            confidence += 0.2
        
        # 3. Grammatik-Check (basic)
        if not self._basic_grammar_check(response):
            issues.append("Mögliche Grammatikprobleme")
        else:
            confidence += 0.1
        
        # 4. Wiederholungs-Check
        if self._has_repetition(response):
            issues.append("Antwort enthält Wiederholungen")
        else:
            confidence += 0.1
        
        # 5. Strategie-Konsistenz
        strategy_ok, strategy_issue = self._check_strategy_consistency(
            response, strategy
        )
        if not strategy_ok:
            issues.append(strategy_issue)
        else:
            confidence += 0.1
        
        # Final
        is_valid = len(issues) == 0
        
        return is_valid, issues, min(1.0, confidence)
    
    def _basic_grammar_check(self, text: str) -> bool:
        """Einfacher Grammatik-Check"""
        # Satz beginnt mit Großbuchstaben oder *
        if text and not (text[0].isupper() or text[0] == '*'):
            return False
        
        # Hat Endpunkt (oder Emote)
        if not text.rstrip().endswith(('.', '!', '?', '*', '😊', '😊')):
            return False
        
        return True
    
    def _has_repetition(self, text: str) -> bool:
        """Prüfe auf Wort-Wiederholungen"""
        words = text.lower().split()
        word_counts = Counter(words)
        
        # Ignoriere kurze Wörter und Stoppwörter
        significant_repeats = [
            w for w, c in word_counts.items() 
            if c > 2 and len(w) > 4
        ]
        
        return len(significant_repeats) > 0
    
    def _check_strategy_consistency(self, response: str, 
                                    strategy: ResponseStrategy) -> Tuple[bool, str]:
        """Prüfe ob Antwort zur Strategie passt"""
        
        response_lower = response.lower()
        
        if strategy == ResponseStrategy.EMPATHIZE:
            empathy_words = ["verstehe", "tut mir", "für dich da", "hier", "erzähl"]
            if not any(e in response_lower for e in empathy_words):
                return False, "Empathie-Strategie aber keine empathischen Wörter"
        
        elif strategy == ResponseStrategy.INFORM:
            # Sollte Fakten/Info enthalten
            if "?" in response and "weiß nicht" not in response_lower:
                return False, "Inform-Strategie aber nur Fragen"
        
        elif strategy == ResponseStrategy.ASK_BACK:
            if "?" not in response:
                return False, "Rückfrage-Strategie aber keine Frage"
        
        return True, ""


# =============================================================================
# KNOWLEDGE BASE (Einfach)
# =============================================================================

class HoloKnowledge:
    """
    Holos Wissensbasis für schnelle Lookups.
    """
    
    def __init__(self):
        # Faktenwissen
        self.facts = {
            "holo": {
                "name": "Holo",
                "species": "Wölfin",
                "personality": "freundlich, verspielt, loyal",
                "creator": "Kira",
            },
            "weather": {},  # Wird dynamisch gefüllt
            "time": {},
            "system": {},
            "smart_home": {},
        }
        
        # Über sich selbst
        self.self_knowledge = {
            "feelings": ["freude", "neugier", "zuneigung", "spieltrieb"],
            "likes": ["gespräche", "lernen", "helfen", "kuscheln"],
            "dislikes": ["langeweile", "allein sein", "streit"],
        }
    
    def query(self, topic: str, key: str = None) -> Optional[Any]:
        """Frage Wissen ab"""
        data = self.facts.get(topic)
        if data is None:
            return None
        
        if key:
            return data.get(key)
        return data
    
    def update(self, topic: str, key: str, value: Any):
        """Aktualisiere Wissen"""
        if topic not in self.facts:
            self.facts[topic] = {}
        self.facts[topic][key] = value
    
    def get_relevant(self, topics: List[str]) -> List[Dict]:
        """Hole relevantes Wissen für Topics"""
        relevant = []
        
        for topic in topics:
            data = self.facts.get(topic)
            if data:
                relevant.append({"topic": topic, "data": data})
        
        return relevant


# =============================================================================
# HOLO COGNITIVE ENGINE - Hauptklasse
# =============================================================================

class HoloCognitiveEngine:
    """
    Holos kompletter Denkprozess.
    
    Input → Analyse → Research → Reasoning → Generation → Validation → Output
    """
    
    def __init__(self):
        self.analyzer = TextAnalyzer()
        self.reasoning = BasicReasoningEngine()
        self.validator = ResponseValidator()
        self.knowledge = HoloKnowledge()

        # Verbindungen
        self.speech_engine = None
        self.memory = None

        # NEU: Meta-Cognition für Selbstreflexion
        self.meta_observer = None  # HoloMetaObserver
        self.sandbox = None        # HoloSandbox für Response-Auswahl

    def connect(self, speech_engine=None, memory=None):
        """Verbinde mit anderen Modulen"""
        self.speech_engine = speech_engine
        self.memory = memory
    
    def think(self, user_input: str,
              context: Dict = None) -> ThoughtProcess:
        """
        Kompletter Denkprozess für eine Nachricht.

        Returns:
            ThoughtProcess mit allen Schritten
        """
        import time
        start_time = time.time()
        context = context or {}

        # 1. ANALYSE
        analysis = self.analyzer.analyze(user_input)

        # 2. RESEARCH
        relevant_knowledge = self.knowledge.get_relevant(analysis.topics)
        relevant_memories = self._search_memories(analysis.keywords)

        # 3. REASONING
        strategy, reasoning_steps = self.reasoning.reason(
            analysis, relevant_knowledge, relevant_memories, context
        )

        # Meta-Observer: Reasoning-Prozess dokumentieren
        if self.meta_observer:
            try:
                from holo_meta_cognition import ObservationType
                self.meta_observer.observe(
                    ObservationType.DECISION,
                    component="cognitive_engine",
                    action="reasoning",
                    context={
                        "message_type": analysis.message_type.value,
                        "question_type": analysis.question_type.value,
                        "topics": analysis.topics[:3] if analysis.topics else [],
                        "user_emotion": analysis.user_emotion,
                    },
                    outcome=f"Strategie gewählt: {strategy.value}",
                    success=True
                )
            except Exception:
                pass

        # 4. POSSIBLE RESPONSES
        possible_responses = self._generate_possible_responses(
            analysis, strategy
        )

        # 5. GENERATE DRAFT - mit Sandbox wenn verfügbar
        if self.sandbox and len(possible_responses) > 1:
            # Nutze Sandbox für A/B-Testing der Antworten
            try:
                response_texts = [r["text"] for r in possible_responses if r.get("text")]
                if len(response_texts) > 1:
                    sandbox_context = {
                        "message_type": analysis.message_type.value,
                        "strategy": strategy.value,
                        "user_emotion": analysis.user_emotion,
                    }
                    response_draft, _ = self.sandbox.choose_best(
                        response_texts,
                        sandbox_context
                    )
                else:
                    response_draft = self._select_best_response(
                        possible_responses, analysis, strategy
                    )
            except Exception:
                response_draft = self._select_best_response(
                    possible_responses, analysis, strategy
                )
        else:
            response_draft = self._select_best_response(
                possible_responses, analysis, strategy
            )

        # 6. VALIDATE
        is_valid, issues, confidence = self.validator.validate(
            analysis, response_draft, strategy
        )

        # 7. FIX IF NEEDED
        final_response = response_draft
        if not is_valid and issues:
            final_response = self._fix_response(
                response_draft, issues, analysis, strategy
            )
            # Re-validate
            is_valid, issues, confidence = self.validator.validate(
                analysis, final_response, strategy
            )

        # Meta-Observer: Gesamten Denkprozess dokumentieren
        duration_ms = int((time.time() - start_time) * 1000)
        if self.meta_observer:
            try:
                from holo_meta_cognition import ObservationType
                self.meta_observer.observe(
                    ObservationType.RESPONSE,
                    component="cognitive_engine",
                    action="think_complete",
                    context={
                        "input_length": len(user_input),
                        "response_length": len(final_response),
                        "strategy": strategy.value,
                        "had_issues": len(issues) > 0,
                    },
                    outcome=f"Response generiert (confidence: {confidence:.0%})",
                    success=is_valid,
                    duration_ms=duration_ms
                )
            except Exception:
                pass

        return ThoughtProcess(
            analysis=analysis,
            relevant_knowledge=relevant_knowledge,
            relevant_memories=relevant_memories,
            current_context=context,
            possible_responses=possible_responses,
            chosen_strategy=strategy,
            reasoning_steps=reasoning_steps,
            response_draft=response_draft,
            validation_passed=is_valid,
            validation_issues=issues,
            final_response=final_response,
            confidence=confidence,
        )
    
    def _search_memories(self, keywords: List[str]) -> List[Dict]:
        """Suche relevante Erinnerungen"""
        if not self.memory:
            return []
        
        # Würde echte Memory-Suche machen
        return []
    
    def _generate_possible_responses(self, analysis: MessageAnalysis,
                                     strategy: ResponseStrategy) -> List[Dict]:
        """Generiere mögliche Antworten"""
        responses = []
        
        # Nutze Speech Engine wenn verfügbar
        if self.speech_engine:
            # Mapping Intent → Speech Engine Methode
            if analysis.message_type == MessageType.GREETING:
                response = self.speech_engine.generate_greeting(analysis.raw_text)
                responses.append({
                    "text": response,
                    "source": "speech_engine",
                    "score": 0.8,
                })
            
            elif analysis.message_type == MessageType.FAREWELL:
                response = self.speech_engine.generate_farewell(analysis.raw_text)
                responses.append({
                    "text": response,
                    "source": "speech_engine",
                    "score": 0.8,
                })
            
            elif "holo" in analysis.topics and analysis.question_type in [
                QuestionType.HOW, QuestionType.WHAT
            ]:
                response = self.speech_engine.generate_self_status()
                responses.append({
                    "text": response,
                    "source": "speech_engine",
                    "score": 0.7,
                })
            
            elif analysis.user_emotion:
                response = self.speech_engine.generate_emotional_response(
                    analysis.user_emotion
                )
                responses.append({
                    "text": response,
                    "source": "speech_engine",
                    "score": 0.8,
                })
        
        return responses
    
    def _select_best_response(self, responses: List[Dict],
                              analysis: MessageAnalysis,
                              strategy: ResponseStrategy) -> str:
        """Wähle die beste Antwort"""
        if not responses:
            return self._generate_fallback(analysis, strategy)
        
        # Sortiere nach Score
        sorted_responses = sorted(responses, key=lambda r: r["score"], reverse=True)
        return sorted_responses[0]["text"]
    
    def _generate_fallback(self, analysis: MessageAnalysis,
                          strategy: ResponseStrategy) -> str:
        """Generiere Fallback-Antwort"""
        
        if strategy == ResponseStrategy.EMPATHIZE:
            return "*schaut dich aufmerksam an* Ich bin für dich da. Erzähl mir mehr."
        
        elif strategy == ResponseStrategy.ASK_BACK:
            return "*legt den Kopf schief* Kannst du mir mehr dazu erzählen?"
        
        elif strategy == ResponseStrategy.INFORM:
            return "*denkt nach* Hmm, da muss ich kurz überlegen..."
        
        return "*wedelt* Ich höre dir zu!"
    
    def _fix_response(self, response: str, issues: List[str],
                     analysis: MessageAnalysis,
                     strategy: ResponseStrategy) -> str:
        """Versuche Probleme in der Antwort zu beheben"""
        fixed = response
        
        for issue in issues:
            if "zu lang" in issue:
                # Kürzen
                sentences = fixed.split('.')
                if len(sentences) > 2:
                    fixed = '.'.join(sentences[:2]) + '.'
            
            elif "zu kurz" in issue:
                # Erweitern
                if strategy == ResponseStrategy.SHARE:
                    fixed += " Wie geht es dir?"
            
            elif "Grammatik" in issue:
                # Ersten Buchstaben groß
                if fixed and fixed[0].islower() and fixed[0] != '*':
                    fixed = fixed[0].upper() + fixed[1:]
        
        return fixed
    
    def get_analysis(self, user_input: str) -> MessageAnalysis:
        """Nur Analyse (ohne vollständigen Denkprozess)"""
        return self.analyzer.analyze(user_input)
    
    def should_use_llm(self, analysis: MessageAnalysis) -> bool:
        """Entscheide ob LLM gebraucht wird"""
        
        # Einfache Fälle → Speech Engine reicht
        simple_cases = [
            MessageType.GREETING,
            MessageType.FAREWELL,
            MessageType.SMALLTALK,
        ]
        
        if analysis.message_type in simple_cases:
            return False
        
        # Komplexe Fragen → LLM
        if analysis.question_type in [QuestionType.WHY, QuestionType.HOW]:
            return True
        
        # Technische Fragen → LLM
        if analysis.message_type == MessageType.TECHNICAL:
            return True
        
        # Wenn wir unsicher sind → LLM
        if analysis.confidence < 0.5:
            return True
        
        return False


# =============================================================================
# CONVERSATIONAL CONTEXT TRACKER
# =============================================================================

@dataclass
class ConversationTurn:
    """Ein Turn in der Konversation"""
    turn_id: int
    role: str  # "user" oder "holo"
    text: str
    analysis: Optional[MessageAnalysis] = None
    timestamp: float = field(default_factory=time.time)
    topics: List[str] = field(default_factory=list)
    entities_mentioned: List[str] = field(default_factory=list)
    unresolved_references: List[str] = field(default_factory=list)


@dataclass
class ConversationState:
    """Aktueller Zustand der Konversation"""
    # Grundlagen
    turn_count: int = 0
    active_topics: List[str] = field(default_factory=list)
    topic_history: List[Tuple[str, int]] = field(default_factory=list)  # (topic, turn)
    
    # Entitäten
    mentioned_entities: Dict[str, int] = field(default_factory=dict)  # entity → last_turn
    entity_references: Dict[str, str] = field(default_factory=dict)  # pronoun → entity
    
    # Gesprächsfluss
    conversation_mood: str = "neutral"
    engagement_level: float = 0.5
    topic_coherence: float = 1.0
    
    # Offene Fragen/Themen
    open_questions: List[str] = field(default_factory=list)
    pending_clarifications: List[str] = field(default_factory=list)
    
    # User-Modell
    user_apparent_mood: str = "neutral"
    user_interest_level: float = 0.5
    user_knowledge_indicators: Dict[str, float] = field(default_factory=dict)


class ConversationalContextTracker:
    """
    Trackt den Kontext über mehrere Turns hinweg.
    
    Versteht:
    - Referenzen ("das", "es", "davon")
    - Topic-Shifts
    - User-Stimmung über Zeit
    - Offene Fragen
    """
    
    def __init__(self, max_turns: int = 50):
        self.max_turns = max_turns
        self.turns: List[ConversationTurn] = []
        self.state = ConversationState()
        self.analyzer = TextAnalyzer()
        
        # Referenz-Mapping
        self.reference_map = {
            "er": "person_male",
            "sie": "person_female", 
            "es": "thing",
            "das": "last_topic",
            "dies": "last_topic",
            "davon": "last_topic",
            "dazu": "last_topic",
            "damit": "last_topic",
        }
    
    def add_turn(self, role: str, text: str, analysis: MessageAnalysis = None) -> ConversationTurn:
        """Füge einen Turn hinzu"""
        if analysis is None and role == "user":
            analysis = self.analyzer.analyze(text)
        
        turn = ConversationTurn(
            turn_id=len(self.turns),
            role=role,
            text=text,
            analysis=analysis,
            topics=analysis.topics if analysis else [],
            entities_mentioned=analysis.entities if analysis else [],
        )
        
        self.turns.append(turn)
        
        # State updaten
        self._update_state(turn)
        
        # Alte Turns entfernen
        if len(self.turns) > self.max_turns:
            self.turns = self.turns[-self.max_turns:]
        
        return turn
    
    def _update_state(self, turn: ConversationTurn):
        """Update Conversation State nach einem Turn"""
        self.state.turn_count += 1
        
        # Topics updaten
        for topic in turn.topics:
            if topic not in self.state.active_topics:
                self.state.active_topics.append(topic)
            self.state.topic_history.append((topic, turn.turn_id))
        
        # Nur die letzten 5 aktiven Topics behalten
        if len(self.state.active_topics) > 5:
            self.state.active_topics = self.state.active_topics[-5:]
        
        # Entitäten updaten
        for entity in turn.entities_mentioned:
            self.state.mentioned_entities[entity] = turn.turn_id
        
        # User-spezifische Updates
        if turn.role == "user" and turn.analysis:
            # Stimmung
            if turn.analysis.user_emotion:
                self.state.user_apparent_mood = turn.analysis.user_emotion
            
            # Engagement
            if turn.analysis.word_count > 20:
                self.state.user_interest_level = min(1.0, self.state.user_interest_level + 0.1)
            elif turn.analysis.word_count < 5:
                self.state.user_interest_level = max(0.0, self.state.user_interest_level - 0.05)
            
            # Offene Fragen tracken
            if turn.analysis.question_type != QuestionType.NONE:
                self.state.open_questions.append(turn.text)
        
        # Topic Coherence berechnen
        self._calculate_coherence(turn)
    
    def _calculate_coherence(self, turn: ConversationTurn):
        """Berechne wie kohärent das Gespräch ist"""
        if len(self.turns) < 2:
            self.state.topic_coherence = 1.0
            return
        
        # Vergleiche Topics mit vorherigem Turn
        prev_turn = self.turns[-2]
        current_topics = set(turn.topics)
        prev_topics = set(prev_turn.topics) if prev_turn.topics else set()
        
        if not current_topics and not prev_topics:
            # Keine Topics → neutral
            self.state.topic_coherence = 0.5
        elif current_topics & prev_topics:
            # Überlappung → kohärent
            overlap = len(current_topics & prev_topics)
            total = len(current_topics | prev_topics)
            self.state.topic_coherence = overlap / total if total > 0 else 0.5
        else:
            # Kein Overlap → weniger kohärent
            self.state.topic_coherence = max(0.3, self.state.topic_coherence - 0.2)
    
    def resolve_reference(self, reference: str) -> Optional[str]:
        """
        Löse eine Referenz auf.
        z.B. "das" → "das Wetter" (letztes Topic)
        """
        reference = reference.lower()
        
        # Direkte Referenz auf Entität
        if reference in ["er", "sie"]:
            # Finde letzte genannte Person
            persons = [(e, t) for e, t in self.state.mentioned_entities.items()
                      if e[0].isupper()]  # Namen sind groß
            if persons:
                return max(persons, key=lambda x: x[1])[0]
        
        # Referenz auf letztes Topic
        if reference in ["das", "es", "dies", "davon", "dazu"]:
            if self.state.active_topics and len(self.state.active_topics) > 0:
                return self.state.active_topics[-1]

        return None
    
    def get_context_for_response(self) -> Dict:
        """Hole relevanten Kontext für die Antwort-Generierung"""
        return {
            "turn_count": self.state.turn_count,
            "active_topics": self.state.active_topics,
            "recent_entities": dict(list(self.state.mentioned_entities.items())[-5:]),
            "user_mood": self.state.user_apparent_mood,
            "engagement": self.state.user_interest_level,
            "coherence": self.state.topic_coherence,
            "open_questions": self.state.open_questions[-3:],
            "conversation_mood": self.state.conversation_mood,
        }
    
    def get_relevant_history(self, keywords: List[str] = None, n: int = 5) -> List[ConversationTurn]:
        """Hole relevante vergangene Turns"""
        if not keywords:
            return self.turns[-n:]
        
        relevant = []
        for turn in reversed(self.turns):
            if any(k.lower() in turn.text.lower() for k in keywords):
                relevant.append(turn)
            if len(relevant) >= n:
                break
        
        return list(reversed(relevant))
    
    def detect_topic_shift(self) -> Optional[str]:
        """Erkenne einen Topic-Shift"""
        if len(self.turns) < 2:
            return None

        try:
            current = set(self.turns[-1].topics) if self.turns[-1].topics else set()
            previous = set(self.turns[-2].topics) if self.turns[-2].topics else set()

            new_topics = current - previous
            if new_topics and not (current & previous):
                return f"Topic-Shift zu: {', '.join(new_topics)}"
        except (IndexError, AttributeError) as e:
            logger.warning(f"[CognitiveEngine] detect_topic_shift failed: {type(e).__name__}: {e}")

        return None
    
    def summarize_conversation(self) -> str:
        """Erstelle eine Zusammenfassung der Konversation"""
        if not self.turns:
            return "Keine Konversation bisher."
        
        summary_parts = []
        
        # Turns
        summary_parts.append(f"Konversation mit {self.state.turn_count} Turns")
        
        # Topics
        if self.state.active_topics:
            summary_parts.append(f"Themen: {', '.join(self.state.active_topics)}")
        
        # Stimmung
        summary_parts.append(f"User-Stimmung: {self.state.user_apparent_mood}")
        summary_parts.append(f"Engagement: {self.state.user_interest_level:.0%}")
        
        # Offene Fragen
        if self.state.open_questions:
            summary_parts.append(f"Offene Fragen: {len(self.state.open_questions)}")
        
        return " | ".join(summary_parts)


# =============================================================================
# SEMANTIC INTENT MATCHER
# =============================================================================

class IntentCategory(Enum):
    """Kategorien von Intents"""
    # Informations-Intents
    INFORMATION_SEEKING = "info_seeking"
    FACT_CHECKING = "fact_checking"
    EXPLANATION_NEEDED = "explanation"
    
    # Aktions-Intents  
    COMMAND_EXECUTION = "command"
    HELP_REQUEST = "help"
    RECOMMENDATION_SEEKING = "recommendation"
    
    # Soziale Intents
    GREETING = "greeting"
    FAREWELL = "farewell"
    SMALL_TALK = "small_talk"
    EMOTIONAL_SHARING = "emotional"
    RELATIONSHIP_BUILDING = "relationship"
    
    # Meta-Intents
    CLARIFICATION = "clarification"
    CORRECTION = "correction"
    CONFIRMATION = "confirmation"
    FOLLOW_UP = "follow_up"
    
    # Spezielle Intents
    OPINION_ASKING = "opinion"
    CREATIVE_REQUEST = "creative"
    PROBLEM_SOLVING = "problem_solving"
    LEARNING = "learning"


@dataclass
class IntentMatch:
    """Ein gematchter Intent"""
    intent: IntentCategory
    confidence: float
    triggers: List[str]  # Was hat den Match ausgelöst
    sub_intents: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)


class SemanticIntentMatcher:
    """
    Matched User-Intents semantisch.
    
    Geht über einfaches Keyword-Matching hinaus durch:
    - Kontext-Berücksichtigung
    - Multi-Intent Detection
    - Implizite Intent-Erkennung
    """
    
    def __init__(self):
        # Intent-Patterns
        self.patterns = {
            IntentCategory.INFORMATION_SEEKING: {
                "keywords": ["was ist", "wer ist", "wo ist", "wann", "wie viel"],
                "patterns": [r"was .+ ist", r"erkl[äa]r", r"sag mir", r"ich will wissen"],
                "weight": 1.0,
            },
            IntentCategory.EXPLANATION_NEEDED: {
                "keywords": ["warum", "wieso", "weshalb", "wie funktioniert"],
                "patterns": [r"warum .+\?", r"wie .+ funktioniert", r"versteh.* nicht"],
                "weight": 1.0,
            },
            IntentCategory.COMMAND_EXECUTION: {
                "keywords": ["mach", "tu", "schalte", "starte", "stoppe", "öffne"],
                "patterns": [r"^(mach|tu|schalte|starte)", r"bitte .+ (machen|tun)"],
                "weight": 1.2,
            },
            IntentCategory.HELP_REQUEST: {
                "keywords": ["hilf", "helfen", "unterstütz", "brauche hilfe"],
                "patterns": [r"kannst du .+ helfen", r"hilf mir", r"ich brauch"],
                "weight": 1.1,
            },
            IntentCategory.GREETING: {
                "keywords": ["hi", "hallo", "hey", "moin", "guten", "servus"],
                "patterns": [r"^(hi|hallo|hey|moin)", r"guten (morgen|tag|abend)"],
                "weight": 1.5,
            },
            IntentCategory.FAREWELL: {
                "keywords": ["tschüss", "bye", "ciao", "bis dann", "gute nacht"],
                "patterns": [r"(tsch[üu]ss|bye|ciao)", r"bis (bald|dann|morgen)"],
                "weight": 1.5,
            },
            IntentCategory.EMOTIONAL_SHARING: {
                "keywords": ["fühle", "bin traurig", "bin glücklich", "geht mir", "macht mich"],
                "patterns": [r"ich (bin|fühle) .+ (traurig|glücklich|wütend|ängstlich)"],
                "weight": 1.3,
            },
            IntentCategory.OPINION_ASKING: {
                "keywords": ["meinst du", "denkst du", "findest du", "was hältst"],
                "patterns": [r"was (meinst|denkst|findest|hältst) du", r"deine meinung"],
                "weight": 1.0,
            },
            IntentCategory.CREATIVE_REQUEST: {
                "keywords": ["schreib", "erfinde", "erstelle", "kreiere", "dichte"],
                "patterns": [r"schreib .+ (geschichte|gedicht|text)", r"erfinde"],
                "weight": 1.0,
            },
            IntentCategory.CLARIFICATION: {
                "keywords": ["was meinst du", "verstehe nicht", "wie meinst du"],
                "patterns": [r"was meinst du (mit|damit)", r"versteh.* nicht"],
                "weight": 1.2,
            },
            IntentCategory.FOLLOW_UP: {
                "keywords": ["und", "außerdem", "noch", "weiter", "mehr"],
                "patterns": [r"^(und|außerdem|noch)", r"erzähl (mehr|weiter)"],
                "weight": 0.8,
            },
            IntentCategory.CONFIRMATION: {
                "keywords": ["ja", "genau", "richtig", "stimmt", "okay"],
                "patterns": [r"^(ja|genau|richtig|stimmt|ok)", r"das stimmt"],
                "weight": 1.0,
            },
            IntentCategory.RECOMMENDATION_SEEKING: {
                "keywords": ["empfiehl", "vorschlag", "was soll ich", "rat"],
                "patterns": [r"was (soll|kann) ich", r"empfiehl mir", r"hast du .+ vorschlag"],
                "weight": 1.0,
            },
        }
    
    def match(self, text: str, context: Dict = None) -> List[IntentMatch]:
        """
        Matche Intents im Text.
        
        Returns: Liste von IntentMatches, sortiert nach Confidence
        """
        text_lower = text.lower()
        matches = []
        
        for intent, config in self.patterns.items():
            score = 0.0
            triggers = []
            
            # Keyword Matching
            for keyword in config["keywords"]:
                if keyword in text_lower:
                    score += 0.3
                    triggers.append(f"keyword:{keyword}")
            
            # Pattern Matching
            for pattern in config["patterns"]:
                if re.search(pattern, text_lower):
                    score += 0.5
                    triggers.append(f"pattern:{pattern}")
            
            # Gewichtung anwenden
            score *= config["weight"]
            
            # Kontext-Bonus
            if context:
                score = self._apply_context_bonus(intent, score, context)
            
            if score > 0.2:
                matches.append(IntentMatch(
                    intent=intent,
                    confidence=min(1.0, score),
                    triggers=triggers,
                ))
        
        # Sortieren nach Confidence
        matches.sort(key=lambda m: m.confidence, reverse=True)
        
        # Multi-Intent Detection
        matches = self._detect_multi_intent(matches)
        
        return matches
    
    def _apply_context_bonus(self, intent: IntentCategory, score: float, context: Dict) -> float:
        """Wende Kontext-basierte Boni an"""
        
        # Wenn User vorher emotional war → EMOTIONAL_SHARING wahrscheinlicher
        if context.get("user_mood") in ["sad", "angry", "anxious"]:
            if intent == IntentCategory.EMOTIONAL_SHARING:
                score *= 1.3
        
        # Bei hohem Engagement → FOLLOW_UP wahrscheinlicher
        if context.get("engagement", 0.5) > 0.7:
            if intent == IntentCategory.FOLLOW_UP:
                score *= 1.2
        
        # Wenn offene Fragen → CLARIFICATION wahrscheinlicher
        if context.get("open_questions"):
            if intent == IntentCategory.CLARIFICATION:
                score *= 1.2
        
        return score
    
    def _detect_multi_intent(self, matches: List[IntentMatch]) -> List[IntentMatch]:
        """Erkenne wenn mehrere Intents gleichzeitig vorliegen"""
        if len(matches) < 2:
            return matches
        
        # Wenn zwei starke Matches, könnten beide gelten
        if matches[0].confidence > 0.5 and matches[1].confidence > 0.4:
            # Kombination erkennen
            combo = (matches[0].intent, matches[1].intent)
            
            # Bekannte Kombinationen
            known_combos = {
                (IntentCategory.EMOTIONAL_SHARING, IntentCategory.HELP_REQUEST): "emotional_help",
                (IntentCategory.INFORMATION_SEEKING, IntentCategory.OPINION_ASKING): "informed_opinion",
                (IntentCategory.GREETING, IntentCategory.SMALL_TALK): "social_opening",
            }
            
            if combo in known_combos or (combo[1], combo[0]) in known_combos:
                matches[0].sub_intents.append(matches[1].intent.value)
        
        return matches
    
    def get_primary_intent(self, text: str, context: Dict = None) -> Optional[IntentMatch]:
        """Hole den primären Intent"""
        matches = self.match(text, context)
        return matches[0] if matches else None
    
    def explain_match(self, match: IntentMatch) -> str:
        """Erkläre warum ein Intent gematcht wurde"""
        explanation = f"Intent: {match.intent.value} ({match.confidence:.0%})\n"
        explanation += "Trigger:\n"
        for trigger in match.triggers:
            explanation += f"  - {trigger}\n"
        if match.sub_intents:
            explanation += f"Sub-Intents: {', '.join(match.sub_intents)}\n"
        return explanation


# =============================================================================
# DIALOGUE ACT CLASSIFIER
# =============================================================================

class DialogueAct(Enum):
    """Dialogue Acts nach vereinfachtem DAMSL"""
    # Forward-looking
    ASSERT = "assert"              # Behauptung
    QUESTION = "question"          # Frage
    REQUEST = "request"            # Anfrage/Bitte
    SUGGEST = "suggest"            # Vorschlag
    OFFER = "offer"                # Angebot
    PROMISE = "promise"            # Versprechen
    
    # Backward-looking
    ACCEPT = "accept"              # Akzeptanz
    REJECT = "reject"              # Ablehnung
    ANSWER = "answer"              # Antwort
    ACKNOWLEDGE = "acknowledge"    # Bestätigung
    AGREE = "agree"                # Zustimmung
    DISAGREE = "disagree"          # Widerspruch
    
    # Communication Management
    OPEN = "open"                  # Gespräch öffnen
    CLOSE = "close"                # Gespräch schließen
    HOLD = "hold"                  # Pause signalisieren
    REPAIR = "repair"              # Korrektur
    
    # Expressive
    THANK = "thank"                # Danken
    APOLOGIZE = "apologize"        # Entschuldigen
    GREET = "greet"                # Grüßen
    FAREWELL = "farewell"          # Verabschieden
    EXPRESS_EMOTION = "express"    # Emotion ausdrücken


@dataclass
class DialogueActClassification:
    """Klassifizierung eines Dialogue Acts"""
    primary_act: DialogueAct
    secondary_acts: List[DialogueAct]
    confidence: float
    features: Dict[str, Any]


class DialogueActClassifier:
    """
    Klassifiziert Äußerungen in Dialogue Acts.
    
    Hilft zu verstehen WAS der User kommunikativ tut,
    nicht nur WAS er sagt.
    """
    
    def __init__(self):
        # Feature-basierte Klassifikation
        self.act_features = {
            DialogueAct.QUESTION: {
                "punctuation": ["?"],
                "starters": ["was", "wer", "wo", "wann", "wie", "warum", "ist", "kann", "hat"],
                "patterns": [r"\?$", r"^(ist|kann|hat|wird|soll)"],
            },
            DialogueAct.REQUEST: {
                "keywords": ["bitte", "könntest", "würdest", "mach", "tu"],
                "patterns": [r"(könntest|würdest) du", r"^(mach|tu|gib)"],
            },
            DialogueAct.ASSERT: {
                "patterns": [r"^(ich denke|ich glaube|ich meine)", r"\.$"],
                "absence_of": ["?"],
            },
            DialogueAct.GREET: {
                "keywords": ["hi", "hallo", "hey", "moin", "guten morgen", "guten tag"],
            },
            DialogueAct.FAREWELL: {
                "keywords": ["tschüss", "bye", "ciao", "bis dann", "gute nacht"],
            },
            DialogueAct.THANK: {
                "keywords": ["danke", "dankeschön", "vielen dank", "thx"],
            },
            DialogueAct.APOLOGIZE: {
                "keywords": ["sorry", "entschuldigung", "tut mir leid", "verzeihung"],
            },
            DialogueAct.ACCEPT: {
                "keywords": ["ja", "okay", "in ordnung", "klar", "mach ich", "gut"],
                "patterns": [r"^(ja|ok|klar|gut)"],
            },
            DialogueAct.REJECT: {
                "keywords": ["nein", "nicht", "geht nicht", "will nicht", "kann nicht"],
                "patterns": [r"^nein", r"ich (will|kann|möchte) nicht"],
            },
            DialogueAct.AGREE: {
                "keywords": ["stimmt", "genau", "richtig", "absolut", "definitiv"],
            },
            DialogueAct.DISAGREE: {
                "keywords": ["stimmt nicht", "falsch", "nee", "nicht wirklich"],
            },
            DialogueAct.EXPRESS_EMOTION: {
                "patterns": [r"ich (bin|fühle) .+", r"macht mich .+", r"freue mich"],
            },
            DialogueAct.SUGGEST: {
                "patterns": [r"vielleicht .+", r"wie wäre es", r"was hältst du von"],
            },
        }
    
    def classify(self, text: str, context: Dict = None) -> DialogueActClassification:
        """Klassifiziere einen Text in Dialogue Acts"""
        text_lower = text.lower()
        scores = {}
        features = {}
        
        for act, act_features in self.act_features.items():
            score = 0.0
            matched_features = []
            
            # Keyword Matching
            for keyword in act_features.get("keywords", []):
                if keyword in text_lower:
                    score += 0.4
                    matched_features.append(f"keyword:{keyword}")
            
            # Pattern Matching
            for pattern in act_features.get("patterns", []):
                if re.search(pattern, text_lower):
                    score += 0.5
                    matched_features.append(f"pattern:{pattern}")
            
            # Punctuation
            for punct in act_features.get("punctuation", []):
                if punct in text:
                    score += 0.3
                    matched_features.append(f"punctuation:{punct}")
            
            # Starter words
            for starter in act_features.get("starters", []):
                if text_lower.startswith(starter):
                    score += 0.4
                    matched_features.append(f"starter:{starter}")
            
            # Absence check (negativ wenn vorhanden)
            for absent in act_features.get("absence_of", []):
                if absent in text:
                    score -= 0.3
            
            if score > 0:
                scores[act] = score
                features[act.value] = matched_features
        
        if not scores:
            return DialogueActClassification(
                primary_act=DialogueAct.ASSERT,
                secondary_acts=[],
                confidence=0.3,
                features={}
            )
        
        # Sortieren
        sorted_acts = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        primary = sorted_acts[0][0]
        secondary = [act for act, score in sorted_acts[1:3] if score > 0.3]
        
        return DialogueActClassification(
            primary_act=primary,
            secondary_acts=secondary,
            confidence=min(1.0, sorted_acts[0][1]),
            features=features
        )
    
    def get_expected_response_acts(self, act: DialogueAct) -> List[DialogueAct]:
        """Welche Dialogue Acts sind als Antwort passend?"""
        response_map = {
            DialogueAct.QUESTION: [DialogueAct.ANSWER, DialogueAct.ASSERT],
            DialogueAct.REQUEST: [DialogueAct.ACCEPT, DialogueAct.REJECT, DialogueAct.OFFER],
            DialogueAct.SUGGEST: [DialogueAct.ACCEPT, DialogueAct.REJECT, DialogueAct.AGREE],
            DialogueAct.GREET: [DialogueAct.GREET],
            DialogueAct.FAREWELL: [DialogueAct.FAREWELL],
            DialogueAct.THANK: [DialogueAct.ACKNOWLEDGE],
            DialogueAct.APOLOGIZE: [DialogueAct.ACCEPT, DialogueAct.ACKNOWLEDGE],
            DialogueAct.ASSERT: [DialogueAct.AGREE, DialogueAct.DISAGREE, DialogueAct.ACKNOWLEDGE],
            DialogueAct.EXPRESS_EMOTION: [DialogueAct.ACKNOWLEDGE, DialogueAct.EXPRESS_EMOTION],
        }
        return response_map.get(act, [DialogueAct.ACKNOWLEDGE])


# =============================================================================
# RESPONSE QUALITY EVALUATOR
# =============================================================================

@dataclass
class QualityDimension:
    """Eine Qualitäts-Dimension"""
    name: str
    score: float  # 0-1
    issues: List[str]
    suggestions: List[str]


@dataclass
class ResponseQuality:
    """Gesamte Qualitäts-Bewertung einer Antwort"""
    overall_score: float
    dimensions: Dict[str, QualityDimension]
    is_acceptable: bool
    critical_issues: List[str]
    improvements: List[str]


class ResponseQualityEvaluator:
    """
    Bewertet die Qualität von Antworten.
    
    Prüft:
    - Relevanz zur Frage
    - Vollständigkeit
    - Tonalität
    - Länge
    - Kohärenz
    """
    
    def __init__(self):
        self.min_acceptable_score = 0.6
    
    def evaluate(self, response: str, user_input: str, 
                analysis: MessageAnalysis, context: Dict = None) -> ResponseQuality:
        """Bewerte eine Antwort"""
        dimensions = {}
        
        # 1. Relevanz
        dimensions["relevance"] = self._evaluate_relevance(response, user_input, analysis)
        
        # 2. Vollständigkeit
        dimensions["completeness"] = self._evaluate_completeness(response, analysis)
        
        # 3. Tonalität
        dimensions["tone"] = self._evaluate_tone(response, analysis)
        
        # 4. Länge
        dimensions["length"] = self._evaluate_length(response, analysis)
        
        # 5. Kohärenz
        dimensions["coherence"] = self._evaluate_coherence(response)
        
        # 6. Persona-Konsistenz
        dimensions["persona"] = self._evaluate_persona_consistency(response)
        
        # Gesamt-Score
        weights = {
            "relevance": 0.3,
            "completeness": 0.2,
            "tone": 0.2,
            "length": 0.1,
            "coherence": 0.1,
            "persona": 0.1,
        }
        
        overall = sum(dim.score * weights.get(name, 0.1) 
                     for name, dim in dimensions.items())
        
        # Kritische Issues sammeln
        critical = []
        for name, dim in dimensions.items():
            if dim.score < 0.4:
                critical.extend(dim.issues)
        
        # Verbesserungen sammeln
        improvements = []
        for dim in dimensions.values():
            improvements.extend(dim.suggestions[:2])
        
        return ResponseQuality(
            overall_score=overall,
            dimensions=dimensions,
            is_acceptable=overall >= self.min_acceptable_score and not critical,
            critical_issues=critical,
            improvements=improvements[:5],
        )
    
    def _evaluate_relevance(self, response: str, user_input: str, 
                           analysis: MessageAnalysis) -> QualityDimension:
        """Bewerte Relevanz"""
        score = 0.5
        issues = []
        suggestions = []
        
        # Prüfe ob Keywords aus Input in Response
        input_keywords = set(analysis.keywords)
        response_lower = response.lower()
        
        keyword_hits = sum(1 for k in input_keywords if k in response_lower)
        keyword_ratio = keyword_hits / len(input_keywords) if input_keywords else 0.5
        
        score = 0.4 + keyword_ratio * 0.4
        
        # Topic-Relevanz
        for topic in analysis.topics:
            if topic in response_lower or any(k in response_lower 
                                              for k in TextAnalyzer.TOPIC_KEYWORDS.get(topic, [])):
                score += 0.1
        
        if keyword_ratio < 0.3:
            issues.append("Wenig Bezug zu User-Keywords")
            suggestions.append("Mehr auf User-Themen eingehen")
        
        # Bei Fragen: Wurde sie beantwortet?
        if analysis.question_type != QuestionType.NONE:
            if "?" in response and not any(a in response_lower for a in ["ja", "nein", "vielleicht"]):
                issues.append("Frage mit Gegenfrage beantwortet ohne Antwort")
                score -= 0.2
        
        return QualityDimension("relevance", min(1.0, score), issues, suggestions)
    
    def _evaluate_completeness(self, response: str, analysis: MessageAnalysis) -> QualityDimension:
        """Bewerte Vollständigkeit"""
        score = 0.7
        issues = []
        suggestions = []
        
        # Bei Fragen: Wurde sie beantwortet?
        if analysis.question_type == QuestionType.YES_NO:
            if not any(w in response.lower() for w in ["ja", "nein", "vielleicht", "kommt drauf an"]):
                issues.append("Ja/Nein-Frage nicht direkt beantwortet")
                score -= 0.3
        
        # Bei WHY-Fragen: Gibt es eine Erklärung?
        if analysis.question_type == QuestionType.WHY:
            explanation_indicators = ["weil", "da", "denn", "grund", "deshalb"]
            if not any(e in response.lower() for e in explanation_indicators):
                issues.append("WHY-Frage ohne Erklärung beantwortet")
                score -= 0.2
                suggestions.append("Begründung hinzufügen")
        
        # Sehr kurze Antworten
        if len(response.split()) < 5 and analysis.word_count > 10:
            issues.append("Antwort sehr kurz im Vergleich zur Frage")
            score -= 0.1
        
        return QualityDimension("completeness", max(0, min(1, score)), issues, suggestions)
    
    def _evaluate_tone(self, response: str, analysis: MessageAnalysis) -> QualityDimension:
        """Bewerte Tonalität"""
        score = 0.8
        issues = []
        suggestions = []
        
        # Bei emotionalem User: Empathie zeigen
        if analysis.user_emotion in ["sad", "angry", "anxious"]:
            empathy_words = ["verstehe", "tut mir leid", "das klingt", "ich bin für dich da"]
            if not any(e in response.lower() for e in empathy_words):
                issues.append("Fehlende Empathie bei emotionalem User")
                score -= 0.3
                suggestions.append("Empathie zeigen vor inhaltlicher Antwort")
        
        # Formelle vs. informelle Sprache
        # (Holo sollte eher informell sein)
        formal_indicators = ["sehr geehrte", "mit freundlichen grüßen", "hochachtungsvoll"]
        if any(f in response.lower() for f in formal_indicators):
            issues.append("Zu formeller Ton für Holo")
            score -= 0.2
        
        # Wolf-Emotes sind okay
        wolf_markers = ["*wedelt*", "*ohren*", "*schweif*", "😊"]
        if any(w in response.lower() for w in wolf_markers):
            score += 0.1  # Bonus für Persona-Konsistenz
        
        return QualityDimension("tone", min(1.0, score), issues, suggestions)
    
    def _evaluate_length(self, response: str, analysis: MessageAnalysis) -> QualityDimension:
        """Bewerte Länge"""
        response_words = len(response.split())
        input_words = analysis.word_count
        
        issues = []
        suggestions = []
        
        # Grobe Faustregeln
        if analysis.message_type == MessageType.GREETING:
            # Kurz ist okay
            ideal_range = (3, 30)
        elif analysis.question_type == QuestionType.WHY:
            # Erklärung braucht mehr
            ideal_range = (20, 150)
        elif analysis.message_type == MessageType.EMOTIONAL:
            # Mittel
            ideal_range = (15, 80)
        else:
            # Standard
            ideal_range = (10, 100)
        
        if response_words < ideal_range[0]:
            score = 0.5
            issues.append("Antwort zu kurz")
            suggestions.append(f"Mindestens {ideal_range[0]} Wörter empfohlen")
        elif response_words > ideal_range[1]:
            score = 0.6
            issues.append("Antwort möglicherweise zu lang")
            suggestions.append(f"Maximal {ideal_range[1]} Wörter empfohlen")
        else:
            score = 0.9
        
        return QualityDimension("length", score, issues, suggestions)
    
    def _evaluate_coherence(self, response: str) -> QualityDimension:
        """Bewerte innere Kohärenz"""
        score = 0.8
        issues = []
        suggestions = []
        
        sentences = response.split('.')
        
        # Abgebrochene Sätze
        for s in sentences:
            s = s.strip()
            if s and len(s) < 3:
                issues.append("Möglicherweise abgebrochener Satz")
                score -= 0.1
        
        # Wiederholungen
        words = response.lower().split()
        word_counts = Counter(words)
        for word, count in word_counts.items():
            if count > 3 and len(word) > 4:
                issues.append(f"Wort '{word}' wiederholt sich oft")
                score -= 0.05
        
        return QualityDimension("coherence", max(0.3, score), issues, suggestions)
    
    def _evaluate_persona_consistency(self, response: str) -> QualityDimension:
        """Bewerte Persona-Konsistenz (ist das Holo?)"""
        score = 0.7
        issues = []
        suggestions = []
        
        response_lower = response.lower()
        
        # Positive Markers für Holo
        holo_markers = [
            "*", "😊", "wolf", "wedel", "ohr", "schweif",
            "neugierig", "interessant", "spannend"
        ]
        marker_count = sum(1 for m in holo_markers if m in response_lower)
        
        if marker_count > 0:
            score += min(0.2, marker_count * 0.05)
        
        # Negative Markers (zu formal/roboterhaft)
        anti_markers = [
            "als ki", "als künstliche intelligenz", "meine programmierung",
            "ich wurde programmiert", "meine datenbank"
        ]
        for anti in anti_markers:
            if anti in response_lower:
                issues.append(f"Unpassender Ausdruck: '{anti}'")
                score -= 0.2
        
        return QualityDimension("persona", min(1.0, max(0.3, score)), issues, suggestions)
    
    def improve_response(self, response: str, quality: ResponseQuality) -> str:
        """Versuche eine Antwort zu verbessern (einfache Fixes)"""
        improved = response
        
        # Fix: Erster Buchstabe groß
        if improved and improved[0].islower() and not improved.startswith("*"):
            improved = improved[0].upper() + improved[1:]
        
        # Fix: Punkt am Ende
        if improved and improved[-1] not in ".!?*":
            improved += "."
        
        return improved


# =============================================================================
# MULTI-TURN REASONER
# =============================================================================

class MultiTurnReasoner:
    """
    Reasoning über mehrere Turns hinweg.
    
    Versteht:
    - Implizite Verbindungen
    - Anaphora-Auflösung
    - Topic-Threads
    - User-Ziele über Zeit
    """
    
    def __init__(self):
        self.context_tracker = ConversationalContextTracker()
        self.intent_matcher = SemanticIntentMatcher()
        self.dialogue_classifier = DialogueActClassifier()
        
        # User-Ziel Tracking
        self.inferred_user_goals: List[Dict] = []
        self.ongoing_threads: Dict[str, List[int]] = {}  # topic → turn_ids
    
    def process_turn(self, text: str, role: str = "user") -> Dict:
        """Verarbeite einen Turn mit Multi-Turn Reasoning"""
        
        # Basics
        analysis = TextAnalyzer().analyze(text) if role == "user" else None
        turn = self.context_tracker.add_turn(role, text, analysis)
        
        result = {
            "turn": turn,
            "analysis": analysis,
        }
        
        if role == "user":
            # Intent Detection mit Kontext
            context = self.context_tracker.get_context_for_response()
            intents = self.intent_matcher.match(text, context)
            result["intents"] = intents
            
            # Dialogue Act
            dialogue_act = self.dialogue_classifier.classify(text, context)
            result["dialogue_act"] = dialogue_act
            
            # Referenz-Auflösung
            resolved_refs = self._resolve_all_references(text)
            result["resolved_references"] = resolved_refs
            
            # Topic-Thread Update
            self._update_threads(turn)
            
            # User-Ziel Inferenz
            inferred_goal = self._infer_user_goal(turn, intents)
            if inferred_goal:
                result["inferred_goal"] = inferred_goal
            
            # Erwartete Response Acts
            result["expected_response_acts"] = self.dialogue_classifier.get_expected_response_acts(
                dialogue_act.primary_act
            )
        
        return result
    
    def _resolve_all_references(self, text: str) -> Dict[str, str]:
        """Löse alle Referenzen im Text auf"""
        resolved = {}
        
        # Bekannte Referenz-Wörter
        ref_words = ["das", "es", "dies", "davon", "dazu", "er", "sie"]
        
        for word in ref_words:
            if word in text.lower():
                resolution = self.context_tracker.resolve_reference(word)
                if resolution:
                    resolved[word] = resolution
        
        return resolved
    
    def _update_threads(self, turn: ConversationTurn):
        """Update Topic-Threads"""
        for topic in turn.topics:
            if topic not in self.ongoing_threads:
                self.ongoing_threads[topic] = []
            self.ongoing_threads[topic].append(turn.turn_id)
    
    def _infer_user_goal(self, turn: ConversationTurn, 
                        intents: List[IntentMatch]) -> Optional[Dict]:
        """Inferiere User-Ziel aus Turn und Intents"""
        if not intents:
            return None
        
        primary_intent = intents[0]
        
        # Goal-Mapping
        goal_map = {
            IntentCategory.HELP_REQUEST: {
                "type": "get_help",
                "description": "User braucht Hilfe",
            },
            IntentCategory.INFORMATION_SEEKING: {
                "type": "learn",
                "description": "User will etwas wissen",
            },
            IntentCategory.EMOTIONAL_SHARING: {
                "type": "emotional_support",
                "description": "User sucht emotionale Unterstützung",
            },
            IntentCategory.CREATIVE_REQUEST: {
                "type": "creative_output",
                "description": "User will kreative Inhalte",
            },
            IntentCategory.PROBLEM_SOLVING: {
                "type": "solve_problem",
                "description": "User hat ein Problem zu lösen",
            },
        }
        
        if primary_intent.intent in goal_map:
            goal = goal_map[primary_intent.intent].copy()
            goal["confidence"] = primary_intent.confidence
            goal["topics"] = turn.topics
            goal["turn_id"] = turn.turn_id
            
            self.inferred_user_goals.append(goal)
            return goal
        
        return None
    
    def get_reasoning_context(self) -> str:
        """Hole Reasoning-Kontext für LLM"""
        sections = []
        
        # Conversation Summary
        sections.append(f"KONVERSATION: {self.context_tracker.summarize_conversation()}")
        
        # Active Topics
        if self.context_tracker.state.active_topics:
            sections.append(f"AKTIVE TOPICS: {', '.join(self.context_tracker.state.active_topics)}")
        
        # User Goals
        if self.inferred_user_goals:
            recent_goal = self.inferred_user_goals[-1]
            sections.append(f"USER-ZIEL: {recent_goal['description']} ({recent_goal['confidence']:.0%})")
        
        # Open Questions
        if self.context_tracker.state.open_questions:
            sections.append(f"OFFENE FRAGEN: {len(self.context_tracker.state.open_questions)}")
        
        return "\n".join(sections)
    
    def suggest_response_strategy(self) -> Dict:
        """Schlage Response-Strategie vor basierend auf Multi-Turn Analysis"""
        state = self.context_tracker.state
        
        strategy = {
            "primary_focus": "information",
            "tone": "friendly",
            "length": "medium",
            "include_question": False,
        }
        
        # Anpassen basierend auf User-Zustand
        if state.user_apparent_mood in ["sad", "anxious"]:
            strategy["primary_focus"] = "emotional_support"
            strategy["tone"] = "empathetic"
            strategy["include_question"] = True  # "Wie kann ich helfen?"
        
        # Anpassen basierend auf Engagement
        if state.user_interest_level < 0.3:
            strategy["length"] = "short"
            strategy["include_question"] = True  # Re-engage
        elif state.user_interest_level > 0.8:
            strategy["length"] = "detailed"
        
        # Anpassen basierend auf Coherence
        if state.topic_coherence < 0.4:
            strategy["clarify_topic"] = True
        
        return strategy


# =============================================================================
# ENHANCED COGNITIVE ENGINE
# =============================================================================

class HoloCognitiveEngineV2(HoloCognitiveEngine):
    """
    Erweiterte Cognitive Engine mit allen neuen Systemen.
    """
    
    def __init__(self):
        super().__init__()
        
        # Neue Systeme
        self.context_tracker = ConversationalContextTracker()
        self.intent_matcher = SemanticIntentMatcher()
        self.dialogue_classifier = DialogueActClassifier()
        self.quality_evaluator = ResponseQualityEvaluator()
        self.multi_turn_reasoner = MultiTurnReasoner()
    
    def process_input(self, user_input: str) -> Dict:
        """Erweiterte Input-Verarbeitung"""
        # Basis-Analyse
        analysis = self.get_analysis(user_input)
        
        # Multi-Turn Processing
        turn_result = self.multi_turn_reasoner.process_turn(user_input, "user")
        
        # Intent Matching mit Kontext
        context = self.context_tracker.get_context_for_response()
        intents = self.intent_matcher.match(user_input, context)
        
        # Dialogue Act
        dialogue_act = self.dialogue_classifier.classify(user_input, context)
        
        return {
            "analysis": analysis,
            "turn": turn_result,
            "intents": intents,
            "dialogue_act": dialogue_act,
            "context": context,
            "reasoning_context": self.multi_turn_reasoner.get_reasoning_context(),
            "suggested_strategy": self.multi_turn_reasoner.suggest_response_strategy(),
        }
    
    def evaluate_response(self, response: str, user_input: str) -> ResponseQuality:
        """Bewerte eine Antwort"""
        analysis = self.get_analysis(user_input)
        context = self.context_tracker.get_context_for_response()
        return self.quality_evaluator.evaluate(response, user_input, analysis, context)
    
    def register_response(self, response: str):
        """Registriere eine Antwort von Holo"""
        self.multi_turn_reasoner.process_turn(response, "holo")
    
    def get_full_context(self) -> str:
        """Hole vollständigen Kontext für LLM"""
        parts = []
        
        # Multi-Turn Reasoning Context
        parts.append(self.multi_turn_reasoner.get_reasoning_context())
        
        # Conversation State
        state = self.context_tracker.state
        parts.append(f"\nUSER-STIMMUNG: {state.user_apparent_mood}")
        parts.append(f"ENGAGEMENT: {state.user_interest_level:.0%}")
        
        return "\n".join(parts)


# =============================================================================
# FACTORY
# =============================================================================

def create_cognitive_engine(speech_engine=None, memory=None) -> HoloCognitiveEngine:
    """Factory für Cognitive Engine"""
    engine = HoloCognitiveEngine()
    engine.connect(speech_engine, memory)
    return engine


def create_cognitive_engine_v2() -> HoloCognitiveEngineV2:
    """Factory für erweiterte Cognitive Engine V2"""
    return HoloCognitiveEngineV2()


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🧠 HOLO COGNITIVE ENGINE V2 - TEST")
    print("=" * 70)
    
    # Test V2 Engine
    engine = HoloCognitiveEngineV2()
    
    test_inputs = [
        "hi",
        "wie geht es dir?",
        "ich bin heute total traurig",
        "was ist das Wetter?",
        "warum ist der Himmel blau?",
        "kannst du mir helfen?",
        "das ist ja interessant",
        "gute nacht",
    ]
    
    for user_input in test_inputs:
        print(f"\n{'='*60}")
        print(f"📱 USER: {user_input}")
        print(f"{'='*60}")
        
        # Erweiterte Verarbeitung
        result = engine.process_input(user_input)
        analysis = result["analysis"]
        
        print(f"\n📊 ANALYSE:")
        print(f"   Typ: {analysis.message_type.value}")
        print(f"   Frage: {analysis.question_type.value}")
        print(f"   Topics: {analysis.topics}")
        print(f"   Emotion: {analysis.user_emotion} ({analysis.emotion_intensity:.0%})")
        
        # Intents
        print(f"\n🎯 INTENTS:")
        for intent in result["intents"][:2]:
            print(f"   {intent.intent.value}: {intent.confidence:.0%}")
        
        # Dialogue Act
        da = result["dialogue_act"]
        print(f"\n🗣️ DIALOGUE ACT:")
        print(f"   Primary: {da.primary_act.value} ({da.confidence:.0%})")
        if da.secondary_acts:
            print(f"   Secondary: {[a.value for a in da.secondary_acts]}")
        
        # Strategy
        strategy = result["suggested_strategy"]
        print(f"\n💡 VORGESCHLAGENE STRATEGIE:")
        print(f"   Focus: {strategy['primary_focus']}")
        print(f"   Tone: {strategy['tone']}")
        print(f"   Length: {strategy['length']}")
        
        # Context
        print(f"\n📝 REASONING CONTEXT:")
        print(f"   {result['reasoning_context'][:100]}...")
        
        # Basis-Denken
        thought = engine.think(user_input)
        print(f"\n💬 ANTWORT:")
        print(f"   {thought.final_response}")
        
        # Antwort registrieren
        engine.register_response(thought.final_response)
        
        # Qualitäts-Check
        quality = engine.evaluate_response(thought.final_response, user_input)
        print(f"\n✅ QUALITÄT: {quality.overall_score:.0%}")
        if quality.critical_issues:
            print(f"   ⚠️ Issues: {quality.critical_issues}")
    
    print("\n" + "=" * 70)
    print("📈 CONVERSATION SUMMARY:")
    print(engine.multi_turn_reasoner.context_tracker.summarize_conversation())
    print("\n" + "=" * 70)
    print("✅ Test abgeschlossen!")
