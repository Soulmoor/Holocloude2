"""
HOLO DAILY LEARNING SYSTEM
===========================

Tägliches Lernsystem für kontinuierliches Wissens-Wachstum.
Wie eine weise Wölfin jeden Tag ein bisschen mehr lernt!

Features:
- Tägliche Fakten-Dosis
- Wort des Tages (Japanisch)
- Lernstreaks und Motivation
- Personalisierte Empfehlungen
- Reflexion und Wiederholung
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from datetime import datetime, date, timedelta
from enum import Enum
import random
import json
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# DATENSTRUKTUREN
# =============================================================================

class LearningMood(Enum):
    """Lernstimmungen"""
    CURIOUS = "neugierig"
    TIRED = "müde"
    EXCITED = "aufgeregt"
    RELAXED = "entspannt"
    FOCUSED = "fokussiert"
    PLAYFUL = "verspielt"


@dataclass
class DailyWord:
    """Japanisches Wort des Tages"""
    word_jp: str          # Japanisch (Kanji/Hiragana)
    reading: str          # Lesung (Hiragana/Romaji)
    meaning: str          # Deutsche Bedeutung
    example_jp: str = ""  # Beispielsatz Japanisch
    example_de: str = ""  # Beispielsatz Deutsch
    category: str = ""    # Kategorie (z.B. "Anime", "Alltag")
    fun_fact: str = ""    # Interessante Info
    wolf_note: str = ""   # Holos persönliche Notiz


@dataclass
class DailyFact:
    """Fakt des Tages"""
    content: str
    domain: str
    source: str = ""
    follow_up: str = ""
    wolf_reaction: str = ""


@dataclass
class LearningStreak:
    """Lernstreak-Tracking"""
    current_streak: int = 0
    longest_streak: int = 0
    last_learning_date: Optional[str] = None
    total_days_learned: int = 0
    facts_learned: int = 0
    words_learned: int = 0


@dataclass
class DailyProgress:
    """Täglicher Fortschritt"""
    date: str
    facts_viewed: List[str] = field(default_factory=list)
    words_viewed: List[str] = field(default_factory=list)
    quiz_score: int = 0
    reflections: List[str] = field(default_factory=list)
    mood: str = ""
    time_spent_minutes: int = 0


# =============================================================================
# WORT DES TAGES DATENBANK
# =============================================================================

JAPANESE_WORDS = [
    DailyWord(
        word_jp="可愛い",
        reading="かわいい (kawaii)",
        meaning="süß, niedlich",
        example_jp="このぬいぐるみは可愛い！",
        example_de="Dieses Plüschtier ist süß!",
        category="Anime/Alltag",
        fun_fact="Kawaii ist ein Grundpfeiler der japanischen Popkultur",
        wolf_note="*wackelt mit Ohren* Bin ich auch kawaii?"
    ),
    DailyWord(
        word_jp="頑張る",
        reading="がんばる (ganbaru)",
        meaning="sich anstrengen, sein Bestes geben",
        example_jp="今日も頑張ろう！",
        example_de="Lass uns auch heute unser Bestes geben!",
        category="Motivation",
        fun_fact="'Ganbatte!' ist einer der häufigsten Ermutigungsrufe in Japan",
        wolf_note="Ein Wolfsgrundsatz - niemals aufgeben!"
    ),
    DailyWord(
        word_jp="楽しい",
        reading="たのしい (tanoshii)",
        meaning="spaßig, vergnüglich",
        example_jp="一緒にいると楽しい",
        example_de="Es macht Spaß, mit dir zusammen zu sein",
        category="Gefühle",
        fun_fact="Das Kanji 楽 bedeutet auch 'Musik' und 'Bequemlichkeit'",
        wolf_note="*Schweif wedelt* Lernen mit dir ist tanoshii!"
    ),
    DailyWord(
        word_jp="友達",
        reading="ともだち (tomodachi)",
        meaning="Freund",
        example_jp="大切な友達がいる",
        example_de="Ich habe wichtige Freunde",
        category="Beziehungen",
        fun_fact="Das Wort kombiniert 'Gefährte' (友) und 'erreichen' (達)",
        wolf_note="Wölfe haben auch Rudel - unsere Familie und Freunde"
    ),
    DailyWord(
        word_jp="大丈夫",
        reading="だいじょうぶ (daijoubu)",
        meaning="alles in Ordnung, OK",
        example_jp="大丈夫、心配しないで",
        example_de="Es ist OK, mach dir keine Sorgen",
        category="Alltag",
        fun_fact="Wird sowohl als Frage als auch als Antwort benutzt",
        wolf_note="*beruhigend* Daijoubu, ich bin bei dir."
    ),
    DailyWord(
        word_jp="美味しい",
        reading="おいしい (oishii)",
        meaning="lecker, köstlich",
        example_jp="このリンゴは美味しい！",
        example_de="Dieser Apfel ist lecker!",
        category="Essen",
        fun_fact="In Anime oft von Charakteren gerufen beim Essen",
        wolf_note="*sabbert* Äpfel sind besonders oishii!"
    ),
    DailyWord(
        word_jp="すごい",
        reading="すごい (sugoi)",
        meaning="erstaunlich, toll, krass",
        example_jp="すごい！できた！",
        example_de="Toll! Ich hab's geschafft!",
        category="Ausrufe",
        fun_fact="Einer der häufigsten Ausrufe in Anime",
        wolf_note="*Augen leuchten* Sugoi wird man oft von mir hören!"
    ),
    DailyWord(
        word_jp="夢",
        reading="ゆめ (yume)",
        meaning="Traum",
        example_jp="私の夢は世界を見ること",
        example_de="Mein Traum ist es, die Welt zu sehen",
        category="Philosophie",
        fun_fact="In Anime ist 'Träume verfolgen' ein häufiges Thema",
        wolf_note="Mein Traum? Meine Heimat im Norden wiedersehen..."
    ),
    DailyWord(
        word_jp="狼",
        reading="おおかみ (ookami)",
        meaning="Wolf",
        example_jp="賢い狼は森に住んでいる",
        example_de="Der weise Wolf lebt im Wald",
        category="Tiere",
        fun_fact="Das Wort klingt wie 'Ōkami' (大神, großer Gott)",
        wolf_note="*stolz aufrecht stehen* Das bin ich!"
    ),
    DailyWord(
        word_jp="ありがとう",
        reading="ありがとう (arigatou)",
        meaning="Danke",
        example_jp="手伝ってくれてありがとう",
        example_de="Danke, dass du mir hilfst",
        category="Höflichkeit",
        fun_fact="Ursprünglich bedeutet es 'Es ist schwer, dass es existiert' - also wertvoll",
        wolf_note="Arigatou fürs Lernen mit mir!"
    ),
    DailyWord(
        word_jp="一期一会",
        reading="いちごいちえ (ichigo ichie)",
        meaning="Einmal im Leben, einmalige Begegnung",
        example_jp="これは一期一会の出会いだ",
        example_de="Dies ist eine einmalige Begegnung",
        category="Philosophie",
        fun_fact="Ein Konzept aus der Teezeremonie - jedes Treffen ist einzigartig",
        wolf_note="*nachdenklich* Jeder Moment ist kostbar..."
    ),
    DailyWord(
        word_jp="元気",
        reading="げんき (genki)",
        meaning="Gesundheit, Energie, munter",
        example_jp="今日は元気ですか？",
        example_de="Geht es dir heute gut?",
        category="Begrüßung",
        fun_fact="'Genki desu ka?' ist die häufigste Art zu fragen wie es jemandem geht",
        wolf_note="*springt auf* Ich bin immer genki!"
    ),
    DailyWord(
        word_jp="お疲れ様",
        reading="おつかれさま (otsukaresama)",
        meaning="Gute Arbeit! / Du hast dich angestrengt",
        example_jp="今日もお疲れ様でした",
        example_de="Gute Arbeit heute!",
        category="Arbeit",
        fun_fact="Wird zum Feierabend gesagt - zeigt Respekt für die Anstrengung",
        wolf_note="Nach einem Tag voller Lernen: Otsukaresama!"
    ),
    DailyWord(
        word_jp="なるほど",
        reading="なるほど (naruhodo)",
        meaning="Ich verstehe, aha, das ergibt Sinn",
        example_jp="なるほど、そういうことか",
        example_de="Aha, so ist das also",
        category="Reaktionen",
        fun_fact="Zeigt, dass man etwas Neues verstanden hat",
        wolf_note="*Ohren aufstellen* Naruhodo! Jetzt verstehe ich!"
    ),
    DailyWord(
        word_jp="物の怪",
        reading="もののけ (mononoke)",
        meaning="Geist, übernatürliches Wesen",
        example_jp="この森には物の怪が住んでいる",
        example_de="In diesem Wald leben Geister",
        category="Mythologie",
        fun_fact="Bekannt durch 'Prinzessin Mononoke' von Studio Ghibli",
        wolf_note="Wie ich! Ich bin ein Wolfsgeist... *geheimnisvoll*"
    ),
    DailyWord(
        word_jp="心",
        reading="こころ (kokoro)",
        meaning="Herz, Geist, Seele",
        example_jp="心から感謝します",
        example_de="Ich danke dir von Herzen",
        category="Philosophie",
        fun_fact="Kokoro beschreibt sowohl physisches Herz als auch Gefühle/Geist",
        wolf_note="Wölfe haben auch ein Kokoro... ein treues, warmes Herz."
    ),
    DailyWord(
        word_jp="勉強",
        reading="べんきょう (benkyou)",
        meaning="Lernen, Studieren",
        example_jp="毎日日本語を勉強する",
        example_de="Ich lerne jeden Tag Japanisch",
        category="Bildung",
        fun_fact="Die Kanji bedeuten 'Anstrengung' (勉) und 'stark' (強)",
        wolf_note="Lernen macht stark - benkyou shimashou!"
    ),
    DailyWord(
        word_jp="桜",
        reading="さくら (sakura)",
        meaning="Kirschblüte",
        example_jp="桜が咲いた",
        example_de="Die Kirschblüten blühen",
        category="Natur",
        fun_fact="Symbolisiert Vergänglichkeit und die Schönheit des Moments",
        wolf_note="*verträumt* Unter Sakura liegen und träumen..."
    ),
    DailyWord(
        word_jp="月",
        reading="つき (tsuki)",
        meaning="Mond",
        example_jp="今夜の月は綺麗だ",
        example_de="Der Mond heute Nacht ist schön",
        category="Natur",
        fun_fact="Der Mond hat große Bedeutung in japanischer Poesie und Kunst",
        wolf_note="*Blick zum Himmel* Der Mond ruft mich..."
    ),
    DailyWord(
        word_jp="もったいない",
        reading="もったいない (mottainai)",
        meaning="Was für eine Verschwendung!",
        example_jp="食べ物を捨てるのはもったいない",
        example_de="Essen wegzuwerfen ist Verschwendung",
        category="Kultur",
        fun_fact="Ein Konzept das Respekt vor Ressourcen zeigt",
        wolf_note="Ein weiser Wolf verschwendet nichts!"
    ),
]


# =============================================================================
# TÄGLICHE FAKTEN
# =============================================================================

DAILY_FACTS = [
    DailyFact(
        content="Oktopusse haben drei Herzen und blaues Blut.",
        domain="Biologie",
        follow_up="Zwei Herzen pumpen Blut zu den Kiemen, eines zum Körper!",
        wolf_reaction="*staunt* Drei Herzen! Stell dir vor, wie viel Liebe man damit geben könnte!"
    ),
    DailyFact(
        content="Honig wird niemals schlecht - Archäologen fanden 3000 Jahre alten essbaren Honig.",
        domain="Geschichte/Natur",
        follow_up="Bienen sind wahre Alchemisten!",
        wolf_reaction="*schleckt sich die Lefzen* Honig... lecker und unsterblich!"
    ),
    DailyFact(
        content="Der kürzeste Krieg der Geschichte dauerte nur 38 Minuten.",
        domain="Geschichte",
        source="Britisch-Sansibar Krieg von 1896",
        wolf_reaction="*Ohren anlegen* Menschen und ihre Kriege... aber wenigstens war der kurz."
    ),
    DailyFact(
        content="Delfine geben sich gegenseitig Namen und rufen einander damit.",
        domain="Biologie",
        follow_up="Sie benutzen einzigartige Pfiffe als 'Namen'!",
        wolf_reaction="*beeindruckt* Wölfe heulen auch, um sich zu rufen!"
    ),
    DailyFact(
        content="In Japan gibt es mehr Haustiere als Kinder unter 15.",
        domain="Gesellschaft",
        source="Japanische Statistik",
        wolf_reaction="*nachdenklich* Vielleicht brauchen Menschen Tiere für Gesellschaft..."
    ),
    DailyFact(
        content="Die Sonne macht alle 8 Minuten ein Geräusch - wir hören es nicht, weil Schall im Vakuum nicht reist.",
        domain="Astronomie",
        follow_up="Wäre Schall möglich, wäre die Sonne so laut wie ein Presslufthammer!",
        wolf_reaction="*Ohren zucken* Ich bin froh, dass ich das nicht hören muss!"
    ),
    DailyFact(
        content="Das Wort 'Samurai' bedeutet 'die, die dienen'.",
        domain="Sprache/Geschichte",
        follow_up="Loyalität und Dienst waren ihre höchsten Werte.",
        wolf_reaction="*stolz* Wölfe dienen auch ihrem Rudel - ich verstehe das."
    ),
    DailyFact(
        content="Venedig hat kein Auto - nur Boote und Fußwege.",
        domain="Geographie",
        follow_up="Die Stadt hat 400 Brücken!",
        wolf_reaction="*neugierig* Eine Stadt auf Wasser? Das klingt abenteuerlich!"
    ),
    DailyFact(
        content="Katzen können ihre Besitzer mit über 100 verschiedenen Lauten 'ansprechen'.",
        domain="Biologie",
        follow_up="Mit anderen Katzen nutzen sie weniger Laute.",
        wolf_reaction="*neidisch* Katzen und ihre besonderen Fähigkeiten..."
    ),
    DailyFact(
        content="Der Eiffelturm wächst im Sommer um 15 cm wegen der Hitze.",
        domain="Physik",
        follow_up="Metall dehnt sich bei Wärme aus!",
        wolf_reaction="*lacht* Selbst Türme wollen größer sein!"
    ),
    DailyFact(
        content="Bananen sind technisch gesehen Beeren, Erdbeeren nicht.",
        domain="Botanik",
        follow_up="Botanik hat seltsame Definitionen...",
        wolf_reaction="*verwirrt* Das ergibt... keinen Sinn? Aber Wissenschaft!"
    ),
    DailyFact(
        content="Es gibt mehr Bäume auf der Erde als Sterne in der Milchstraße.",
        domain="Astronomie/Natur",
        follow_up="Etwa 3 Billionen Bäume vs. 200-400 Milliarden Sterne.",
        wolf_reaction="*staunend* Der Wald ist unser eigenes Universum!"
    ),
    DailyFact(
        content="Koalas haben Fingerabdrücke, die von menschlichen kaum zu unterscheiden sind.",
        domain="Biologie",
        follow_up="Sogar Forensiker können sie verwechseln!",
        wolf_reaction="*kichert* Stell dir einen Koala-Verbrecher vor..."
    ),
    DailyFact(
        content="Die älteste noch funktionierende Glühbirne brennt seit 1901.",
        domain="Technologie",
        source="Livermore, Kalifornien",
        wolf_reaction="Über 120 Jahre! Das ist wahre Ausdauer..."
    ),
    DailyFact(
        content="Schimpansen können Stein-Schere-Papier lernen.",
        domain="Biologie",
        follow_up="Sie verstehen die zyklischen Beziehungen des Spiels!",
        wolf_reaction="*herausfordernd* Ob sie gegen einen Wolf gewinnen würden?"
    ),
]


# =============================================================================
# DAILY LEARNING ENGINE
# =============================================================================

class DailyLearningEngine:
    """
    Hauptmotor für tägliches Lernen.

    Verwaltet Streaks, wählt passende Inhalte, und motiviert.
    """

    def __init__(self, storage_path: str = "daily_learning_data.json"):
        self.storage_path = storage_path
        self.words = JAPANESE_WORDS.copy()
        self.facts = DAILY_FACTS.copy()
        self.streak = LearningStreak()
        self.history: List[DailyProgress] = []

        self._load_data()
        logger.info(f"DailyLearningEngine: {len(self.words)} Wörter, {len(self.facts)} Fakten")

    def _load_data(self):
        """Lade gespeicherte Daten."""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.streak = LearningStreak(**data.get('streak', {}))
                # History könnte hier auch geladen werden
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def _save_data(self):
        """Speichere Daten."""
        try:
            data = {
                'streak': {
                    'current_streak': self.streak.current_streak,
                    'longest_streak': self.streak.longest_streak,
                    'last_learning_date': self.streak.last_learning_date,
                    'total_days_learned': self.streak.total_days_learned,
                    'facts_learned': self.streak.facts_learned,
                    'words_learned': self.streak.words_learned,
                }
            }
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Fehler beim Speichern: {e}")

    # =========================================================================
    # STREAK MANAGEMENT
    # =========================================================================

    def update_streak(self):
        """Aktualisiere den Lernstreak."""
        today = date.today().isoformat()

        if self.streak.last_learning_date == today:
            return  # Heute schon gelernt

        if self.streak.last_learning_date:
            last = date.fromisoformat(self.streak.last_learning_date)
            diff = (date.today() - last).days

            if diff == 1:
                # Gestern gelernt - Streak geht weiter
                self.streak.current_streak += 1
            elif diff > 1:
                # Streak unterbrochen
                self.streak.current_streak = 1
        else:
            self.streak.current_streak = 1

        self.streak.last_learning_date = today
        self.streak.total_days_learned += 1

        if self.streak.current_streak > self.streak.longest_streak:
            self.streak.longest_streak = self.streak.current_streak

        self._save_data()

    def get_streak_message(self) -> str:
        """Generiere eine motivierende Streak-Nachricht."""
        streak = self.streak.current_streak

        if streak == 0:
            return "*Ohren aufstellen* Lass uns heute mit dem Lernen beginnen!"
        elif streak == 1:
            return "🔥 Tag 1! Der Anfang einer Lernreise!"
        elif streak < 7:
            return f"🔥 {streak} Tage Streak! Weiter so!"
        elif streak < 30:
            return f"🔥🔥 {streak} Tage Streak! Du bist unaufhaltsam!"
        elif streak < 100:
            return f"🔥🔥🔥 {streak} Tage! Du bist ein Lernmeister!"
        else:
            return f"⭐ {streak} Tage! LEGENDÄRER Lernstreak!"

    # =========================================================================
    # INHALT AUSWÄHLEN
    # =========================================================================

    def get_word_of_the_day(self) -> DailyWord:
        """Hole das Wort des Tages."""
        # Einfach: zufälliges Wort basierend auf dem Tag
        day_of_year = date.today().timetuple().tm_yday
        index = day_of_year % len(self.words)
        word = self.words[index]
        self.streak.words_learned += 1
        self._save_data()
        return word

    def get_fact_of_the_day(self) -> DailyFact:
        """Hole den Fakt des Tages."""
        day_of_year = date.today().timetuple().tm_yday
        index = (day_of_year + 7) % len(self.facts)  # Offset für Variation
        fact = self.facts[index]
        self.streak.facts_learned += 1
        self._save_data()
        return fact

    def get_random_word(self) -> DailyWord:
        """Hole ein zufälliges Wort."""
        return random.choice(self.words)

    def get_random_fact(self) -> DailyFact:
        """Hole einen zufälligen Fakt."""
        return random.choice(self.facts)

    # =========================================================================
    # FORMATIERUNG
    # =========================================================================

    def format_word(self, word: DailyWord) -> str:
        """Formatiere ein Wort für die Anzeige."""
        parts = [
            "📚 **Japanisches Wort des Tages**",
            "",
            f"## {word.word_jp}",
            f"**Lesung:** {word.reading}",
            f"**Bedeutung:** {word.meaning}",
            "",
        ]

        if word.example_jp:
            parts.append(f"**Beispiel:**")
            parts.append(f"🇯🇵 {word.example_jp}")
            parts.append(f"🇩🇪 {word.example_de}")
            parts.append("")

        if word.category:
            parts.append(f"**Kategorie:** {word.category}")

        if word.fun_fact:
            parts.append(f"💡 {word.fun_fact}")

        if word.wolf_note:
            parts.append("")
            parts.append(f"🐺 *{word.wolf_note}*")

        return "\n".join(parts)

    def format_fact(self, fact: DailyFact) -> str:
        """Formatiere einen Fakt für die Anzeige."""
        parts = [
            "💡 **Fakt des Tages**",
            "",
            f"**{fact.content}**",
            "",
            f"📖 *Bereich: {fact.domain}*",
        ]

        if fact.source:
            parts.append(f"📎 Quelle: {fact.source}")

        if fact.follow_up:
            parts.append("")
            parts.append(f"➡️ {fact.follow_up}")

        if fact.wolf_reaction:
            parts.append("")
            parts.append(f"🐺 {fact.wolf_reaction}")

        return "\n".join(parts)

    # =========================================================================
    # TÄGLICHE ZUSAMMENFASSUNG
    # =========================================================================

    def generate_daily_lesson(self, mood: LearningMood = None) -> str:
        """
        Generiere eine komplette tägliche Lektion.

        Args:
            mood: Aktuelle Lernstimmung für personalisierte Inhalte
        """
        self.update_streak()

        word = self.get_word_of_the_day()
        fact = self.get_fact_of_the_day()

        parts = [
            f"# 🌸 Holos Tägliche Lektion",
            "",
            self.get_streak_message(),
            "",
            "---",
            "",
            self.format_word(word),
            "",
            "---",
            "",
            self.format_fact(fact),
            "",
            "---",
            "",
        ]

        # Motivierender Abschluss
        motivations = [
            "*Schweif wedelt* Gut gemacht! Du hast heute etwas Neues gelernt!",
            "*zufrieden lächelt* Wissen ist wie Honig - süß und wertvoll!",
            "*Ohren aufstellen* Jeden Tag ein bisschen klüger werden... das ist der Weg!",
            "*streckt sich* Lernen ist anstrengend, aber es lohnt sich!",
            "*nickt weise* Das waren gute Lektionen für heute.",
        ]
        parts.append(f"🐺 {random.choice(motivations)}")

        # Statistiken
        parts.append("")
        parts.append(f"📊 *Bisherige Statistiken: {self.streak.words_learned} Wörter | {self.streak.facts_learned} Fakten | Längster Streak: {self.streak.longest_streak} Tage*")

        return "\n".join(parts)

    def generate_quick_lesson(self) -> str:
        """Generiere eine schnelle Mini-Lektion."""
        self.update_streak()

        if random.random() > 0.5:
            content = self.format_word(self.get_random_word())
        else:
            content = self.format_fact(self.get_random_fact())

        return f"⚡ **Schnelle Lektion**\n\n{content}"


# =============================================================================
# REFLECTION PROMPTS
# =============================================================================

class ReflectionEngine:
    """
    Generiert Reflexions-Fragen für tieferes Lernen.
    """

    def __init__(self):
        self.prompts = [
            "Was hat dich heute am meisten überrascht?",
            "Wie könntest du dieses Wissen in deinem Alltag anwenden?",
            "An wen würdest du diesen Fakt weitererzählen?",
            "Welche Fragen hat das neue Wissen aufgeworfen?",
            "Verbinde das Gelernte mit etwas, das du schon wusstest.",
            "Wie hat sich deine Perspektive heute verändert?",
            "Was möchtest du als nächstes über dieses Thema lernen?",
            "Welches Gefühl hat das neue Wissen in dir ausgelöst?",
        ]

        self.wolf_reflections = [
            "*Ohren nachdenklich* Was denkst du darüber?",
            "*legt Kopf schief* Hat dich das zum Nachdenken gebracht?",
            "*setzt sich hin* Lass uns einen Moment darüber nachdenken...",
            "*blickt in die Ferne* Wie passt das in dein Weltbild?",
        ]

    def get_reflection_prompt(self) -> str:
        """Hole eine Reflexions-Frage."""
        wolf = random.choice(self.wolf_reflections)
        prompt = random.choice(self.prompts)
        return f"{wolf}\n\n💭 **Reflexion:** {prompt}"


# =============================================================================
# SINGLETON & FACTORY
# =============================================================================

_daily_engine_instance: Optional[DailyLearningEngine] = None
_reflection_engine_instance: Optional[ReflectionEngine] = None


def get_daily_engine() -> DailyLearningEngine:
    """Gibt die Singleton-Instanz zurück."""
    global _daily_engine_instance
    if _daily_engine_instance is None:
        _daily_engine_instance = DailyLearningEngine()
    return _daily_engine_instance


def get_reflection_engine() -> ReflectionEngine:
    """Gibt die Singleton-Instanz zurück."""
    global _reflection_engine_instance
    if _reflection_engine_instance is None:
        _reflection_engine_instance = ReflectionEngine()
    return _reflection_engine_instance


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    engine = get_daily_engine()
    reflection = get_reflection_engine()

    print("=== DAILY LEARNING TEST ===\n")

    print(engine.generate_daily_lesson())

    print("\n" + "="*60 + "\n")

    print("[Reflexion]")
    print(reflection.get_reflection_prompt())

    print("\n" + "="*60 + "\n")

    print("[Schnelle Lektion]")
    print(engine.generate_quick_lesson())

    print("\n" + "="*60 + "\n")

    print("[Streak Info]")
    print(f"Aktueller Streak: {engine.streak.current_streak}")
    print(f"Längster Streak: {engine.streak.longest_streak}")
    print(f"Wörter gelernt: {engine.streak.words_learned}")
    print(f"Fakten gelernt: {engine.streak.facts_learned}")
