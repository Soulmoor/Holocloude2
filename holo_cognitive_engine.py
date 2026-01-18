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
    EMOTION_KEYWORDS = {
        "happy": ["freue", "glücklich", "toll", "super", "geil", "nice", "cool",
                  "yay", "hurra", "fantastisch", "wunderbar", "großartig", "perfekt",
                  "herrlich", "genial", "klasse", "prima", "spitze", "mega", "hammer",
                  "freut mich", "bin froh", "macht spaß", "liebe es", "begeistert"],
        "sad": ["traurig", "schlecht", "mies", "down", "depri", "unglücklich",
                "einsam", "allein", "verletzt", "enttäuscht", "niedergeschlagen",
                "bedrückt", "weinen", "tränen", "schmerzt", "tut weh", "vermisse",
                "hoffnungslos", "leer", "schwer ums herz", "melancholisch"],
        "angry": ["wütend", "sauer", "genervt", "frustriert", "verärgert",
                  "kotzt mich an", "nervt", "hasse", "aggressiv", "zornig",
                  "stinksauer", "aufgebracht", "empört", "entrüstet", "rasend",
                  "zum kotzen", "unfassbar", "unverschämt", "frechheit"],
        "anxious": ["angst", "sorge", "nervös", "unsicher", "ängstlich",
                    "beunruhigt", "gestresst", "stress", "panik", "befürchte",
                    "mache mir sorgen", "besorgt", "unruhig", "aufgewühlt",
                    "überfordert", "überwältigt", "angespannt", "bange"],
        "tired": ["müde", "erschöpft", "kaputt", "fertig", "platt", "ko",
                  "ausgelaugt", "schlapp", "energielos", "kraftlos", "matt",
                  "todmüde", "hundemüde", "am ende", "ausgebrannt", "burnout"],
        "excited": ["aufgeregt", "gespannt", "kann nicht warten", "hyped",
                    "kribbelt", "zappelig", "ungeduldig", "freue mich riesig",
                    "kann es kaum erwarten", "total gespannt", "elektrisiert"],
        "confused": ["verwirrt", "verstehe nicht", "kapier nicht", "hä", "was",
                     "irritiert", "ratlos", "perplex", "durcheinander", "lost",
                     "keinen plan", "keine ahnung", "check ich nicht", "unklar"],
        "grateful": ["danke", "dankbar", "lieb von dir", "nett", "wertschätze",
                     "bedeutet mir viel", "bin dir dankbar", "schätze es"],
        "loving": ["liebe dich", "mag dich", "hab dich lieb", "gern", "vermisse dich",
                   "bist mir wichtig", "schätze dich", "zuneigung", "verbunden"],
        "hopeful": ["hoffe", "hoffnung", "zuversichtlich", "optimistisch",
                    "wird schon", "glaube daran", "positiv gestimmt"],
        "bored": ["langweilig", "öde", "fade", "nichts los", "gelangweilt",
                  "langweile mich", "monoton", "eintönig", "stumpfsinnig"],
    }
    
    # Topic Keywords - Erweitert für bessere Erkennung
    TOPIC_KEYWORDS = {
        "weather": ["wetter", "regen", "sonne", "warm", "kalt", "temperatur", "grad",
                    "schnee", "wolken", "sturm", "gewitter", "nebel", "wind", "frost",
                    "sonnig", "bewölkt", "regnerisch", "schwül", "feucht", "trocken"],
        "time": ["uhr", "zeit", "spät", "früh", "datum", "tag", "woche", "monat",
                 "jahr", "stunde", "minute", "morgen", "abend", "nacht", "mittag",
                 "wochenende", "feiertag", "termin", "kalender", "deadline"],
        "system": ["nas", "server", "cpu", "ram", "system", "computer", "pc",
                   "festplatte", "speicher", "backup", "update", "netzwerk", "wifi",
                   "internet", "verbindung", "download", "upload", "software"],
        "smart_home": ["licht", "lampe", "temperatur", "heizung", "steckdose",
                       "rollladen", "jalousie", "sensor", "schalter", "dimmen",
                       "automation", "szene", "timer", "bewegung", "alarm"],
        "health": ["gesund", "krank", "schmerz", "arzt", "medizin", "kopfschmerzen",
                   "erkältet", "fieber", "müdigkeit", "sport", "fitness", "training",
                   "ernährung", "schlaf", "stress", "entspannung", "wellness"],
        "work": ["arbeit", "job", "projekt", "meeting", "chef", "kollege", "büro",
                 "homeoffice", "deadline", "aufgabe", "task", "präsentation",
                 "besprechung", "termin", "karriere", "gehalt", "urlaub"],
        "food": ["essen", "hunger", "kochen", "rezept", "lecker", "frühstück",
                 "mittagessen", "abendessen", "snack", "getränk", "trinken",
                 "restaurant", "bestellen", "liefern", "backen", "grillen"],
        "entertainment": ["film", "serie", "musik", "spiel", "buch", "lesen",
                          "anime", "manga", "gaming", "stream", "youtube", "netflix",
                          "konzert", "kino", "theater", "podcast", "hörbuch"],
        "relationships": ["freund", "familie", "partner", "liebe", "beziehung",
                          "eltern", "geschwister", "kind", "hochzeit", "trennung",
                          "streit", "versöhnung", "vertrauen", "zusammen"],
        "hobbies": ["hobby", "basteln", "malen", "zeichnen", "fotografieren",
                    "gärtnern", "sammeln", "wandern", "reisen", "kreativ"],
        "emotions": ["gefühl", "emotion", "stimmung", "laune", "herz", "seele"],
        "holo_self": ["holo", "du", "dir", "dich", "dein", "wie geht es dir",
                      "was machst du", "was denkst du", "fühlst du"],
        "holo": ["du", "dir", "dich", "holo", "wolf", "wölfin"],
    }
    
    # Referenz-Wörter (verweisen auf Vorheriges)
    REFERENCE_WORDS = [
        "das", "dies", "diese", "dieser", "dieses",
        "davon", "dazu", "damit", "darüber", "darum",
        "es", "sie", "er", "ihm", "ihr",
        "vorhin", "eben", "gerade", "letztens",
        "nochmal", "wieder", "weiter", "auch",
    ]
    
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
    
    def _detect_emotion(self, text: str) -> Tuple[Optional[str], float]:
        """Erkenne User-Emotion"""
        
        for emotion, keywords in self.EMOTION_KEYWORDS.items():
            matches = sum(1 for k in keywords if k in text)
            if matches > 0:
                intensity = min(1.0, matches * 0.3 + 0.3)
                return emotion, intensity
        
        return None, 0.0
    
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
