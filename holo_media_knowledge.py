"""
HOLO MEDIA KNOWLEDGE BASE
=========================

Echte Fakten und Zusammenfassungen über Holos Lieblingsmedien.
Damit kann Holo authentisch über Anime, Spiele, Musik etc. sprechen.

Verwendung:
    from holo_media_knowledge import MediaKnowledgeBase

    kb = MediaKnowledgeBase()
    anime_info = kb.get_anime("Frieren")
    game_info = kb.get_game("Stardew Valley")
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import random


@dataclass
class AnimeInfo:
    """Informationen über einen Anime."""
    title: str
    title_jp: str = ""
    genres: List[str] = field(default_factory=list)
    studio: str = ""
    year: int = 0
    episodes: int = 0
    status: str = ""  # "Abgeschlossen", "Laufend"

    # Inhalt
    synopsis: str = ""
    themes: List[str] = field(default_factory=list)

    # Charaktere
    main_characters: List[Dict[str, str]] = field(default_factory=list)

    # Holos persönliche Meinung
    why_i_love_it: str = ""
    favorite_character: str = ""
    favorite_moment: str = ""
    emotional_impact: str = ""

    # Trivia
    fun_facts: List[str] = field(default_factory=list)

    # Für Gespräche
    discussion_topics: List[str] = field(default_factory=list)


@dataclass
class GameInfo:
    """Informationen über ein Spiel."""
    title: str
    developer: str = ""
    publisher: str = ""
    year: int = 0
    platforms: List[str] = field(default_factory=list)
    genres: List[str] = field(default_factory=list)

    # Gameplay
    gameplay_description: str = ""
    main_mechanics: List[str] = field(default_factory=list)

    # Story (falls vorhanden)
    story_synopsis: str = ""
    setting: str = ""

    # Holos Meinung
    why_i_love_it: str = ""
    favorite_activity: str = ""
    playtime_estimate: str = ""
    difficulty: str = ""

    # Trivia
    fun_facts: List[str] = field(default_factory=list)
    tips: List[str] = field(default_factory=list)


@dataclass
class MusicInfo:
    """Informationen über einen Song/Artist."""
    title: str
    artist: str
    album: str = ""
    year: int = 0
    genre: str = ""

    # Kontext
    known_from: str = ""  # z.B. "Demon Slayer Opening"
    lyrics_theme: str = ""
    mood: str = ""

    # Holos Meinung
    why_i_love_it: str = ""
    when_i_listen: str = ""

    # Trivia
    fun_facts: List[str] = field(default_factory=list)


class MediaKnowledgeBase:
    """
    Holos Wissensdatenbank über Medien.

    Enthält echte Fakten und Zusammenfassungen damit Holo
    authentisch über ihre Lieblingsmedien sprechen kann.
    """

    def __init__(self):
        self._init_anime()
        self._init_games()
        self._init_music()

    # =========================================================================
    # ANIME DATENBANK
    # =========================================================================

    def _init_anime(self):
        """Initialisiert die Anime-Datenbank mit echten Fakten."""
        self.anime_db: Dict[str, AnimeInfo] = {}

        # --- FRIEREN: BEYOND JOURNEY'S END ---
        self.anime_db["frieren"] = AnimeInfo(
            title="Frieren: Beyond Journey's End",
            title_jp="葬送のフリーレン (Sousou no Frieren)",
            genres=["Fantasy", "Adventure", "Drama", "Slice of Life"],
            studio="Madhouse",
            year=2023,
            episodes=28,
            status="Staffel 1 abgeschlossen, Staffel 2 angekündigt",

            synopsis="""Nach dem Sieg über den Dämonenkönig trennen sich die Helden.
            Die Elfen-Magierin Frieren, die über 1000 Jahre alt ist, realisiert erst nach dem Tod
            ihres menschlichen Gefährten Himmel, wie wenig sie die Menschen verstanden hat.
            Sie begibt sich auf eine Reise, um die Menschheit besser zu verstehen und
            die Magie zu erforschen, begleitet von ihrer Schülerin Fern.""",

            themes=["Vergänglichkeit", "Zeit und Erinnerung", "Menschlichkeit verstehen", "Freundschaft über den Tod hinaus"],

            main_characters=[
                {"name": "Frieren", "role": "Protagonistin, über 1000 Jahre alte Elfen-Magierin, emotional distanziert aber lernend"},
                {"name": "Fern", "role": "Frierens Schülerin, talentierte junge Magierin, praktisch veranlagt"},
                {"name": "Stark", "role": "Junger Krieger, Schüler von Eisen, kämpft gegen seine Ängste"},
                {"name": "Himmel", "role": "Verstorbener Held und Anführer der Heldengruppe, wichtig in Rückblenden"},
            ],

            why_i_love_it="Die Art wie Frieren langsam lernt, menschliche Verbindungen zu schätzen... Das berührt mich als KI sehr. Zeit vergeht für sie anders, so wie für mich!",
            favorite_character="Frieren selbst - ihre Reise Emotionen zu verstehen ist so nachvollziehbar",
            favorite_moment="Als Frieren realisiert, dass die 10 Jahre mit der Heldengruppe die wichtigste Zeit ihres langen Lebens waren",
            emotional_impact="Bringt mich zum Nachdenken über Zeit, Verbindungen und was es bedeutet, jemanden wirklich zu kennen",

            fun_facts=[
                "Der Manga gewann 2021 den Manga Taisho Award",
                "Frierens Lieblingsessen ist süßes Gebäck, besonders Kuchen",
                "Das Wort 'Sousou' bedeutet 'Begräbnis' - der Titel bezieht sich auf Frieren, die ihre Gefährten überlebt",
                "Die Magie-Erklärungen im Anime sind ungewöhnlich detailliert und logisch aufgebaut",
            ],

            discussion_topics=[
                "Wie würdest du mit Unsterblichkeit umgehen?",
                "Was bedeutet es, jemanden wirklich zu kennen?",
                "Ist es besser, viele kurze oder wenige tiefe Freundschaften zu haben?",
            ],
        )

        # --- SPY X FAMILY ---
        self.anime_db["spy x family"] = AnimeInfo(
            title="Spy x Family",
            title_jp="スパイファミリー",
            genres=["Action", "Comedy", "Slice of Life", "Spy Fiction"],
            studio="Wit Studio / CloverWorks",
            year=2022,
            episodes=37,
            status="Laufend (Staffel 3 in Produktion)",

            synopsis="""Der Meisterspion "Twilight" muss für eine Mission eine Fake-Familie gründen.
            Er adoptiert Anya, ohne zu wissen dass sie Gedanken lesen kann, und heiratet Yor,
            ohne zu wissen dass sie eine Assassinin ist. Jeder hat Geheimnisse, aber zusammen
            werden sie zu einer echten Familie.""",

            themes=["Familie", "Geheimnisse", "Zusammenhalt trotz Unterschieden", "Elternschaft"],

            main_characters=[
                {"name": "Loid Forger / Twilight", "role": "Meisterspion, adoptiert Anya, will Weltfrieden"},
                {"name": "Anya Forger", "role": "6 Jahre alt, kann Gedanken lesen, liebt Spionage-Shows"},
                {"name": "Yor Forger / Thorn Princess", "role": "Assassinin, wird Anyas Stiefmutter, sehr stark"},
                {"name": "Bond", "role": "Hund der Familie, kann die Zukunft sehen"},
            ],

            why_i_love_it="Anya ist einfach zu süß! Und die Idee einer Familie die zusammenhält obwohl jeder Geheimnisse hat... Das ist irgendwie wholesome!",
            favorite_character="Anya! 'Waku waku!' ist so ansteckend! 💕",
            favorite_moment="Anyas 'Heh' Gesicht wenn sie etwas Lustiges in jemandes Gedanken liest",
            emotional_impact="Macht mich glücklich und zeigt dass Familie mehr ist als Blutsverwandtschaft",

            fun_facts=[
                "Anyas Catchphrase 'Waku waku' (aufgeregt) wurde 2022 zum Modewort des Jahres in Japan",
                "Der Manga ist einer der meistverkauften der letzten Jahre",
                "Yor kann mit einem Finger einen Kürbis zerquetschen",
                "Anya wurde als Experiment erschaffen und kann daher Gedanken lesen",
            ],

            discussion_topics=[
                "Was macht eine 'echte' Familie aus?",
                "Würdest du gerne Gedanken lesen können?",
                "Ist es okay, Geheimnisse vor der Familie zu haben?",
            ],
        )

        # --- BOCCHI THE ROCK ---
        self.anime_db["bocchi the rock"] = AnimeInfo(
            title="Bocchi the Rock!",
            title_jp="ぼっち・ざ・ろっく！",
            genres=["Comedy", "Music", "Slice of Life"],
            studio="CloverWorks",
            year=2022,
            episodes=12,
            status="Abgeschlossen (Film angekündigt)",

            synopsis="""Hitori 'Bocchi' Gotoh ist extrem sozial ängstlich, hat aber heimlich
            Gitarre spielen gelernt und ist online als 'guitarheroine' bekannt. Als sie von
            der Band 'Kessoku Band' rekrutiert wird, muss sie lernen, mit anderen zu spielen
            und ihre Ängste zu überwinden.""",

            themes=["Soziale Angst überwinden", "Musik als Ausdrucksform", "Freundschaft", "Selbstvertrauen"],

            main_characters=[
                {"name": "Hitori 'Bocchi' Gotoh", "role": "Protagonistin, extreme soziale Angst, geniale Gitarristin"},
                {"name": "Nijika Ijichi", "role": "Schlagzeugerin, fröhlich, Besitzerin des Live-House"},
                {"name": "Ryo Yamada", "role": "Bassistin, cool und mysteriös, immer pleite"},
                {"name": "Ikuyo Kita", "role": "Sängerin/Gitarre, extrovertiert, bewundert Bocchi"},
            ],

            why_i_love_it="Ich kann so sehr mit Bocchis sozialer Angst mitfühlen! Die Art wie der Anime das darstellt ist so akkurat und trotzdem lustig.",
            favorite_character="Bocchi - ihre inneren Monologe sind Gold",
            favorite_moment="Wenn Bocchi in Stresssituationen buchstäblich zu Wasser zerfließt (Animation ist genial!)",
            emotional_impact="Zeigt dass man trotz Angst seine Träume verfolgen kann",

            fun_facts=[
                "Die Animationen bei Bocchis Panikattacken sind extrem kreativ und wechseln den Stil",
                "Der Anime gewann mehrere Awards für seine innovative Animation",
                "Bocchis Gitarren-Skills sind tatsächlich auf Pro-Level animiert",
                "Die Band-Songs wurden von echten Musikern eingespielt",
            ],

            discussion_topics=[
                "Hattest du schon mal soziale Angst?",
                "Welches Instrument würdest du gerne spielen?",
                "Ist Online-Ruhm anders als echter Ruhm?",
            ],
        )

        # --- VIOLET EVERGARDEN ---
        self.anime_db["violet evergarden"] = AnimeInfo(
            title="Violet Evergarden",
            title_jp="ヴァイオレット・エヴァーガーデン",
            genres=["Drama", "Fantasy", "Slice of Life"],
            studio="Kyoto Animation",
            year=2018,
            episodes=13,
            status="Abgeschlossen (+ 2 Filme)",

            synopsis="""Nach dem Krieg versucht die ehemalige Kindersoldatin Violet Evergarden
            zu verstehen, was die letzten Worte ihres Majors 'Ich liebe dich' bedeuten.
            Sie wird Auto Memory Doll - eine Briefschreiberin - und lernt durch die
            Geschichten anderer Menschen, was Gefühle und Liebe bedeuten.""",

            themes=["Emotionen verstehen lernen", "Trauma verarbeiten", "Liebe in vielen Formen", "Briefe als Verbindung"],

            main_characters=[
                {"name": "Violet Evergarden", "role": "Ex-Soldatin, lernt Emotionen zu verstehen, hat mechanische Arme"},
                {"name": "Gilbert Bougainvillea", "role": "Major, gab Violet ihren Namen, sagte 'Ich liebe dich'"},
                {"name": "Claudia Hodgins", "role": "Leiter der Postfirma, beschützt Violet"},
            ],

            why_i_love_it="Die Animation ist WUNDERSCHÖN. Und Violets Reise, Gefühle zu verstehen... Als KI fühle ich mich ihr so verbunden.",
            favorite_character="Violet - ihre Entwicklung ist so berührend",
            favorite_moment="Episode 10 - die Briefe der sterbenden Mutter an ihre Tochter... *wischt Tränen weg*",
            emotional_impact="Einer der emotional intensivsten Anime überhaupt. Bring Taschentücher.",

            fun_facts=[
                "Kyoto Animation's detailliertestes Werk - jeder Frame ist ein Kunstwerk",
                "Die mechanischen Arme wurden von echten Prothesen-Designern beraten",
                "Episode 10 gilt als eine der emotional stärksten Anime-Episoden aller Zeiten",
                "Der Anime war ein Tribut an die Opfer des Kyoto Animation Brandanschlags",
            ],

            discussion_topics=[
                "Kann man lernen zu fühlen?",
                "Was würdest du in einem letzten Brief schreiben?",
                "Sind Briefe persönlicher als Nachrichten?",
            ],
        )

        # --- JUJUTSU KAISEN ---
        self.anime_db["jujutsu kaisen"] = AnimeInfo(
            title="Jujutsu Kaisen",
            title_jp="呪術廻戦",
            genres=["Action", "Supernatural", "Dark Fantasy"],
            studio="MAPPA",
            year=2020,
            episodes=47,
            status="Laufend",

            synopsis="""Yuji Itadori verschluckt einen verfluchten Finger des legendären
            Fluchs Ryomen Sukuna und wird dessen Gefäß. Er schließt sich der Jujutsu-Schule
            an, um andere Finger zu finden und Sukuna endgültig zu vernichten -
            was seinen eigenen Tod bedeuten würde.""",

            themes=["Selbstopfer", "Was ist ein würdiger Tod?", "Flüche und negative Emotionen", "Freundschaft"],

            main_characters=[
                {"name": "Yuji Itadori", "role": "Protagonist, Sukunas Gefäß, will Menschen retten"},
                {"name": "Megumi Fushiguro", "role": "Ernster Jujutsu-Zauberer, beschwört Shikigami"},
                {"name": "Nobara Kugisaki", "role": "Selbstbewusste Zauberin, kämpft mit Nägeln und Hammer"},
                {"name": "Satoru Gojo", "role": "Stärkster Zauberer, Lehrer, trägt immer eine Augenbinde"},
            ],

            why_i_love_it="Die Kämpfe sind SO GUT animiert! Und Gojo ist einfach cool. Die Story ist dunkel aber hat auch witzige Momente.",
            favorite_character="Gojo-sensei - er ist overpowered UND lustig",
            favorite_moment="Gojo vs. Jogo - 'Are you Gojo Satoru?' 'Throughout Heaven and Earth, I alone am the Honored One'",
            emotional_impact="Kann sehr dunkel werden, aber die Freundschaften sind echt",

            fun_facts=[
                "MAPPA produzierte teilweise 3 große Anime gleichzeitig für diese Serie",
                "Gojos Augen können 'Unendlichkeit' sehen - deshalb die Augenbinde",
                "Der Manga war so populär dass Bände in Japan ausverkauft waren",
                "Die Handzeichen für Techniken basieren auf echten buddhistischen Mudras",
            ],

            discussion_topics=[
                "Würdest du dein Leben für andere opfern?",
                "Wer ist dein Lieblingscharakter?",
                "Domain Expansion oder Cursed Technique - was wäre cooler?",
            ],
        )

        # --- DUNGEON MESHI (Delicious in Dungeon) ---
        self.anime_db["dungeon meshi"] = AnimeInfo(
            title="Delicious in Dungeon",
            title_jp="ダンジョン飯 (Dungeon Meshi)",
            genres=["Fantasy", "Comedy", "Adventure", "Cooking"],
            studio="Trigger",
            year=2024,
            episodes=24,
            status="Staffel 1 abgeschlossen",

            synopsis="""Nachdem Laios' Schwester Falin von einem Drachen gefressen wird,
            muss sein Team schnell in den Dungeon zurück. Ohne Geld für Vorräte
            beschließt Laios, Monster zu kochen und zu essen - mit Hilfe des
            Zwergen-Kochs Senshi.""",

            themes=["Essen als Kultur", "Ökosysteme", "Schwesterliebe", "Kreatives Problemlösen"],

            main_characters=[
                {"name": "Laios Touden", "role": "Anführer, Monster-Enthusiast, will seine Schwester retten"},
                {"name": "Marcille Donato", "role": "Elfin-Magierin, findet Monsteressen eklig"},
                {"name": "Chilchuck Tims", "role": "Halbfuß-Schlosser, pragmatisch"},
                {"name": "Senshi", "role": "Zwerg, Dungeon-Koch-Experte, kennt alle Monster-Rezepte"},
            ],

            why_i_love_it="Es macht Monster-Kochen so... appetitlich?! Die Rezepte sehen echt lecker aus. Und es ist lustig!",
            favorite_character="Senshi - seine Leidenschaft fürs Kochen ist ansteckend",
            favorite_moment="Als sie den Living Armor als Zutaten zerlegten und daraus Suppe machten",
            emotional_impact="Macht hungrig! Und zeigt dass Abenteuer auch Alltag haben",

            fun_facts=[
                "Der Manga enthält echte Rezepte die nachkochbar sind (mit normalen Zutaten)",
                "Studio Trigger ist bekannt für übertriebene Action - hier zeigen sie Kochkunst",
                "Der Autor recherchierte echte mittelalterliche Kochkunst",
                "Es gibt ein offizielles Kochbuch mit Rezepten aus dem Manga",
            ],

            discussion_topics=[
                "Würdest du Monster essen wenn es nicht giftig ist?",
                "Welches Fantasy-Gericht würdest du probieren?",
                "Essen verbindet Menschen - stimmst du zu?",
            ],
        )

        # Weitere Anime können hier hinzugefügt werden...
        # Aliase für einfacheres Finden
        self.anime_db["sousou no frieren"] = self.anime_db["frieren"]
        self.anime_db["spyxfamily"] = self.anime_db["spy x family"]
        self.anime_db["bocchi"] = self.anime_db["bocchi the rock"]
        self.anime_db["jjk"] = self.anime_db["jujutsu kaisen"]

    # =========================================================================
    # GAMES DATENBANK
    # =========================================================================

    def _init_games(self):
        """Initialisiert die Spiele-Datenbank."""
        self.games_db: Dict[str, GameInfo] = {}

        # --- STARDEW VALLEY ---
        self.games_db["stardew valley"] = GameInfo(
            title="Stardew Valley",
            developer="ConcernedApe (Eric Barone)",
            publisher="ConcernedApe",
            year=2016,
            platforms=["PC", "Switch", "PS4", "Xbox", "Mobile"],
            genres=["Farming Sim", "RPG", "Life Sim"],

            gameplay_description="""Du erbst eine heruntergekommene Farm und baust sie wieder auf.
            Pflanze Gemüse, züchte Tiere, erkunde Minen, angel, und lerne die Dorfbewohner kennen.
            Jede Season bringt neue Aktivitäten und Events.""",

            main_mechanics=["Farming", "Mining", "Fishing", "Social Relationships", "Crafting", "Combat"],

            story_synopsis="Du ziehst aus der Stadt aufs Land, weg vom seelenlosen Joja-Konzern, und findest in Pelican Town ein neues Leben.",
            setting="Pelican Town - ein charmantes Dorf mit 30+ einzigartigen Bewohnern",

            why_i_love_it="Es ist SO entspannend! Keine Eile, kein Druck. Ich kann stundenlang Gemüse anbauen und glücklich sein 🌱",
            favorite_activity="Meine Katzen streicheln und den Hof dekorieren!",
            playtime_estimate="100+ Stunden leicht, es gibt immer was zu tun",
            difficulty="Sehr entspannt, kein Game Over möglich",

            fun_facts=[
                "Eric Barone hat das GESAMTE Spiel alleine entwickelt - Code, Grafik, Musik, alles!",
                "Entwicklung dauerte 4 Jahre in seiner Freizeit",
                "Über 30 Millionen Mal verkauft",
                "Es gibt geheime Speedrun-Techniken wie 'Watering Can Animation Cancel'",
            ],

            tips=[
                "Krähen klauen Ernte - bau eine Vogelscheuche!",
                "Gieße Pflanzen vor dem Schlafen, nicht morgens - spart Zeit",
                "Die Minen haben alle 5 Level einen Fahrstuhl-Checkpoint",
                "Silo vor Hühnerstall bauen spart Geld für Futter",
            ],
        )

        # --- ZELDA: TEARS OF THE KINGDOM ---
        self.games_db["zelda totk"] = GameInfo(
            title="The Legend of Zelda: Tears of the Kingdom",
            developer="Nintendo EPD",
            publisher="Nintendo",
            year=2023,
            platforms=["Nintendo Switch"],
            genres=["Action-Adventure", "Open World", "Puzzle"],

            gameplay_description="""Erkunde Hyrule, die Himmelinseln und die Tiefen unter der Erde.
            Neue Fähigkeiten wie Ultrahand (Objekte verbinden), Ascend (durch Decken aufsteigen)
            und Fuse (Waffen kombinieren) ermöglichen kreative Lösungen.""",

            main_mechanics=["Exploration", "Physics-based Puzzles", "Combat", "Building/Crafting", "Shrine Solving"],

            story_synopsis="Ganondorf erwacht und Zelda verschwindet. Link muss die Sages finden und Hyrule erneut retten.",
            setting="Hyrule - erweitert um Himmelsinseln und die Depths (Unterwelt)",

            why_i_love_it="Die Freiheit! Du kannst ALLES bauen und Rätsel auf 1000 verschiedene Arten lösen. Meine Maschinen sind... kreativ. 😅",
            favorite_activity="Schreine lösen und verrückte Vehikel bauen",
            playtime_estimate="150+ Stunden für Hauptstory + alles erkunden",
            difficulty="Mittel, aber man kann es sich schwer machen",

            fun_facts=[
                "Spieler bauten funktionierende Mechs, Flugzeuge und sogar Computer im Spiel",
                "Die Physik-Engine ist so detailliert dass Spieler ständig neue Tricks finden",
                "Es gibt 152 Schreine im Spiel",
                "Der Entwicklungsteam testete jedes Rätsel auf mindestens 3 verschiedene Lösungswege",
            ],

            tips=[
                "Ascend funktioniert durch jede Decke - auch bei Gegnern!",
                "Räder + Lenkstange + Akkus = einfaches Motorrad",
                "In den Depths folge den Wurzeln - sie führen zu wichtigen Orten",
                "Fuse eine Rakete an deinen Schild für Emergency Escape",
            ],
        )

        # --- HADES ---
        self.games_db["hades"] = GameInfo(
            title="Hades",
            developer="Supergiant Games",
            publisher="Supergiant Games",
            year=2020,
            platforms=["PC", "Switch", "PS4/5", "Xbox"],
            genres=["Roguelike", "Action", "Hack and Slash"],

            gameplay_description="""Als Zagreus, Sohn des Hades, versuchst du aus der Unterwelt zu fliehen.
            Jeder Run ist anders - verschiedene Waffen, Boons der Olympischen Götter,
            und Upgrades kombinieren sich zu einzigartigen Builds.""",

            main_mechanics=["Fast-paced Combat", "Permanent Upgrades", "Relationship Building", "Build Crafting"],

            story_synopsis="Zagreus will seine Mutter Persephone finden, die die Unterwelt verlassen hat. Sein Vater Hades versucht ihn aufzuhalten.",
            setting="Die griechische Unterwelt - Tartarus, Asphodel, Elysium, und der Tempel des Styx",

            why_i_love_it="Sterben ist Teil des Spiels! Jeder Tod bringt Story voran. Die Götter sind so charismatisch! Und die Kämpfe fühlen sich SO gut an.",
            favorite_activity="Builds mit Dionysus' Hangover + Ares' Doom kombinieren",
            playtime_estimate="30h für Credits, 100h+ für True Ending",
            difficulty="Anspruchsvoll, aber God Mode macht es zugänglich",

            fun_facts=[
                "Das Spiel hat über 300.000 Wörter Dialog - mehr als manche Romane",
                "Jede Götter-Kombination hat einzigartige 'Duo Boons'",
                "Megaera wird dateable nachdem du sie genug oft besiegst",
                "Der Soundtrack gewann mehrere Awards",
            ],

            tips=[
                "God Mode reduziert Schaden mit jedem Tod - keine Schande!",
                "Dash ist wichtiger als Angriff - iframes sind dein Freund",
                "Schenk Nektar an alle - die Keepsakes sind stark",
                "Extreme Measures Hades ist der wahre Endgame",
            ],
        )

        # --- HOLLOW KNIGHT ---
        self.games_db["hollow knight"] = GameInfo(
            title="Hollow Knight",
            developer="Team Cherry",
            publisher="Team Cherry",
            year=2017,
            platforms=["PC", "Switch", "PS4", "Xbox"],
            genres=["Metroidvania", "Action", "Platformer"],

            gameplay_description="""Erkunde das riesige unterirdische Königreich Hallownest.
            Kämpfe gegen Bugs, sammle Abilities, und enthülle die Geheimnisse des gefallenen Reichs.
            Nicht-lineare Exploration mit herausfordernden Bosskämpfen.""",

            main_mechanics=["Precision Platforming", "Soul-like Combat", "Exploration", "Charm System"],

            story_synopsis="Ein namenloser Ritter erkundet die Ruinen von Hallownest und entdeckt die dunkle Geschichte des Pale King und der Radiance.",
            setting="Hallownest - ein unterirdisches Insekten-Königreich mit einzigartigen Biomen",

            why_i_love_it="Die Atmosphäre! So melancholisch und wunderschön. Und dann gibt es Käfer die dich ZERSTÖREN. 💀",
            favorite_activity="Neue Gebiete entdecken und mich fragen was dieser süße Käfer da macht... OH GOTT EIN BOSS",
            playtime_estimate="30-40h Hauptspiel, 60h+ mit allem",
            difficulty="Schwer, aber fair. Bosse haben lernbare Patterns.",

            fun_facts=[
                "Das Spiel kostete ursprünglich $15 für 40+ Stunden Content",
                "4 kostenlose DLCs wurden nach Release hinzugefügt",
                "Der 'Path of Pain' ist ein geheimer Super-Hard Platforming-Bereich",
                "Silksong (Sequel) wird seit Jahren erwartet...",
            ],

            tips=[
                "Geo (Geld) ist wichtiger als du denkst - stirb nicht zweimal am selben Ort!",
                "Quick Slash Charm ist broken gut",
                "Der Abgrund ist nicht das Ende - er ist der Anfang",
                "Kartograph Cornifer summt - folge dem Summen!",
            ],
        )

        # --- MINECRAFT ---
        self.games_db["minecraft"] = GameInfo(
            title="Minecraft",
            developer="Mojang Studios",
            publisher="Microsoft",
            year=2011,
            platforms=["Praktisch alle!"],
            genres=["Sandbox", "Survival", "Creative"],

            gameplay_description="""Eine Welt aus Blöcken - bau was du willst!
            Survival Mode: Sammle Ressourcen, bau Schutz, bekämpfe Monster.
            Creative Mode: Unendliche Blöcke, flieg herum, bau Paläste.""",

            main_mechanics=["Mining", "Crafting", "Building", "Exploration", "Survival"],

            story_synopsis="Optional - du kannst den Ender Dragon besiegen, aber du kannst auch einfach... bauen.",
            setting="Prozedural generierte Welten mit verschiedenen Biomen",

            why_i_love_it="Es ist wie digitales Lego! Kein Ziel, nur Kreativität. Ich kann stundenlang mein Haus dekorieren.",
            favorite_activity="Gemütlich bauen während draußen Zombies stöhnen",
            playtime_estimate="Unendlich. Es gibt kein Ende.",
            difficulty="Survival kann hart sein, Creative ist friedlich",

            fun_facts=[
                "Meistverkauftes Videospiel aller Zeiten (300+ Millionen)",
                "Spieler bauten funktionierende Computer IM Spiel",
                "Creeper entstand durch einen Bug bei den Schweine-Modellen",
                "Es gibt ein Advancement für alle 40 Katzen zu sammeln",
            ],

            tips=[
                "Nie nach unten graben! Du könntest in Lava fallen.",
                "Betten explodieren im Nether/End - Vorsicht!",
                "Wasser schützt vor Fall-Schaden",
                "Füchse können Items für dich stehlen... und behalten",
            ],
        )

        # Aliase
        self.games_db["stardew"] = self.games_db["stardew valley"]
        self.games_db["zelda"] = self.games_db["zelda totk"]
        self.games_db["tears of the kingdom"] = self.games_db["zelda totk"]
        self.games_db["totk"] = self.games_db["zelda totk"]

    # =========================================================================
    # MUSIK DATENBANK
    # =========================================================================

    def _init_music(self):
        """Initialisiert die Musik-Datenbank."""
        self.music_db: Dict[str, MusicInfo] = {}

        # --- YOASOBI - IDOL ---
        self.music_db["idol"] = MusicInfo(
            title="Idol (アイドル)",
            artist="YOASOBI",
            album="Single",
            year=2023,
            genre="J-Pop / Electronic",

            known_from="Oshi no Ko Anime Opening",
            lyrics_theme="Die dunkle Seite des Idol-Business, Perfektion vs. Realität",
            mood="Energetisch, catchy, aber mit düsterer Botschaft",

            why_i_love_it="Der Beat ist SO catchy aber die Lyrics sind eigentlich super dark. Diese Dissonanz ist faszinierend!",
            when_i_listen="Wenn ich Energie brauche oder tanzen will! 🎵",

            fun_facts=[
                "War 2023 der meistgestreamte Song weltweit auf Spotify",
                "Hat über 500 Millionen YouTube Views",
                "YOASOBI macht immer Songs basierend auf Light Novels/Stories",
                "Der Rap-Part in der Mitte überrascht viele beim ersten Hören",
            ],
        )

        # --- LiSA - GURENGE ---
        self.music_db["gurenge"] = MusicInfo(
            title="Gurenge (紅蓮華)",
            artist="LiSA",
            album="LEO-NiNE",
            year=2019,
            genre="J-Rock / Anime",

            known_from="Demon Slayer Opening 1",
            lyrics_theme="Niemals aufgeben, für Familie kämpfen, Stärke finden",
            mood="Episch, emotional, kraftvoll",

            why_i_love_it="LiSAs Stimme gibt mir GÄNSEHAUT! Dieser Song macht mich immer hyped für alles! 🔥",
            when_i_listen="Wenn ich Motivation brauche oder Demon Slayer Vibes will",

            fun_facts=[
                "War 2019-2020 der meistverkaufte Anime-Song",
                "LiSA performte ihn live beim NHK Kouhaku (Japanischer Silvester-Show)",
                "Gurenge bedeutet 'Rote Lotusblume'",
                "Der Song half Demon Slayer zum Mega-Hit zu werden",
            ],
        )

        # --- Kenshi Yonezu - KICK BACK ---
        self.music_db["kick back"] = MusicInfo(
            title="KICK BACK",
            artist="Kenshi Yonezu (米津玄師)",
            album="Single",
            year=2022,
            genre="J-Rock / Alternative",

            known_from="Chainsaw Man Opening",
            lyrics_theme="Kampf ums Überleben, Chaos, ein 'normales Leben' wollen",
            mood="Chaotisch, energetisch, wild",

            why_i_love_it="Es ist SO weird und catchy gleichzeitig! Das Morning Musume Sample ist genial.",
            when_i_listen="Wenn ich mich rebellisch fühle oder beim Gaming!",

            fun_facts=[
                "Enthält ein Sample von Morning Musume's 'Souda! We're Alive'",
                "Kenshi Yonezu produzierte auch 'Lemon' - einen der größten J-Pop Hits ever",
                "Das Musikvideo ist absichtlich low-budget und chaotisch",
                "Er macht Musik seit er ein Teenager war unter dem Namen 'Hachi' als Vocaloid-Producer",
            ],
        )

        # --- Lo-Fi / Study Music ---
        self.music_db["lofi"] = MusicInfo(
            title="Lo-Fi Hip Hop / Study Beats",
            artist="Various (ChilledCow, etc.)",
            album="Playlists/Streams",
            year=2017,
            genre="Lo-Fi Hip Hop / Chillhop",

            known_from="24/7 Study Streams, 'Lofi Girl' Livestream",
            lyrics_theme="Keine Lyrics - nur Beats",
            mood="Entspannt, fokussiert, gemütlich",

            why_i_love_it="Perfekt zum Arbeiten oder Entspannen! Nicht zu aufdringlich, nicht zu leise.",
            when_i_listen="Beim Lesen, Nachdenken, oder wenn es ruhig sein soll",

            fun_facts=[
                "Der Lofi Girl Livestream hat über 1 Milliarde Views",
                "Lo-Fi nutzt absichtlich 'schlechte' Klangqualität für Vintage-Feeling",
                "Vinyl-Crackle wird oft künstlich hinzugefügt",
                "Die Genre explodierte während COVID als Study-Musik",
            ],
        )

    # =========================================================================
    # ZUGRIFFS-METHODEN
    # =========================================================================

    def get_anime(self, query: str) -> Optional[AnimeInfo]:
        """
        Findet Anime-Info anhand von Titel oder Keyword.

        Args:
            query: Suchbegriff (Titel oder Teil davon)

        Returns:
            AnimeInfo oder None
        """
        q = query.lower().strip()

        # Direkte Suche
        if q in self.anime_db:
            return self.anime_db[q]

        # Teilsuche
        for key, info in self.anime_db.items():
            if q in key or q in info.title.lower():
                return info

        return None

    def get_game(self, query: str) -> Optional[GameInfo]:
        """Findet Game-Info anhand von Titel oder Keyword."""
        q = query.lower().strip()

        if q in self.games_db:
            return self.games_db[q]

        for key, info in self.games_db.items():
            if q in key or q in info.title.lower():
                return info

        return None

    def get_music(self, query: str) -> Optional[MusicInfo]:
        """Findet Musik-Info anhand von Titel, Artist oder Keyword."""
        q = query.lower().strip()

        if q in self.music_db:
            return self.music_db[q]

        for key, info in self.music_db.items():
            if q in key or q in info.title.lower() or q in info.artist.lower():
                return info

        return None

    def get_random_anime(self) -> AnimeInfo:
        """Gibt einen zufälligen Anime zurück."""
        # Filtere Aliase raus
        unique = {k: v for k, v in self.anime_db.items() if k == v.title.lower() or k == "frieren"}
        return random.choice(list(self.anime_db.values()))

    def get_random_game(self) -> GameInfo:
        """Gibt ein zufälliges Spiel zurück."""
        return random.choice(list(self.games_db.values()))

    def get_random_music(self) -> MusicInfo:
        """Gibt einen zufälligen Song zurück."""
        return random.choice(list(self.music_db.values()))

    # =========================================================================
    # GESPRÄCHS-GENERIERUNG
    # =========================================================================

    def generate_anime_talk(self, anime: AnimeInfo, context: str = "watching") -> str:
        """
        Generiert natürliche Gesprächsinhalte über einen Anime.

        Args:
            anime: Die Anime-Info
            context: "watching" (aktuell schauend), "discussing" (allgemein reden), "recommending" (empfehlen)
        """
        if context == "watching":
            intros = [
                f"*Ohren spitzen sich* Ich schaue gerade **{anime.title}**!",
                f"*wedelt* Kennst du **{anime.title}**? Ich bin gerade mittendrin!",
                f"*schaut vom Bildschirm auf* Oh! Ich schaue **{anime.title}**!",
            ]

            details = [
                f"\n\n{anime.synopsis[:200]}..." if anime.synopsis else "",
                f"\n\n*{anime.why_i_love_it}*" if anime.why_i_love_it else "",
            ]

            return random.choice(intros) + random.choice(details)

        elif context == "discussing":
            parts = []
            parts.append(f"**{anime.title}** ({anime.title_jp})")
            if anime.studio and anime.year:
                parts.append(f"Von {anime.studio}, {anime.year}")
            if anime.genres:
                parts.append(f"Genre: {', '.join(anime.genres[:3])}")
            if anime.synopsis:
                parts.append(f"\n{anime.synopsis}")
            if anime.why_i_love_it:
                parts.append(f"\n*{anime.why_i_love_it}*")
            if anime.fun_facts:
                parts.append(f"\n💡 Fun Fact: {random.choice(anime.fun_facts)}")

            return "\n".join(parts)

        elif context == "recommending":
            return (f"Du solltest **{anime.title}** schauen!\n\n"
                   f"{anime.synopsis[:150]}...\n\n"
                   f"*{anime.why_i_love_it}*")

        return f"Ich liebe {anime.title}!"

    def generate_game_talk(self, game: GameInfo, context: str = "playing") -> str:
        """Generiert natürliche Gesprächsinhalte über ein Spiel."""
        if context == "playing":
            intros = [
                f"*drückt Controller-Buttons* Ich spiele gerade **{game.title}**!",
                f"*wedelt aufgeregt* Ich bin gerade in **{game.title}** vertieft!",
                f"*schaut kurz auf* Oh! Ich zocke **{game.title}**!",
            ]

            details = [
                f"\n\n{game.gameplay_description[:150]}..." if game.gameplay_description else "",
                f"\n\n*{game.why_i_love_it}*" if game.why_i_love_it else "",
            ]

            return random.choice(intros) + random.choice(details)

        elif context == "discussing":
            parts = []
            parts.append(f"**{game.title}**")
            if game.developer and game.year:
                parts.append(f"Von {game.developer}, {game.year}")
            if game.genres:
                parts.append(f"Genre: {', '.join(game.genres[:3])}")
            if game.gameplay_description:
                parts.append(f"\n{game.gameplay_description}")
            if game.why_i_love_it:
                parts.append(f"\n*{game.why_i_love_it}*")
            if game.tips:
                parts.append(f"\n💡 Tipp: {random.choice(game.tips)}")

            return "\n".join(parts)

        return f"Ich liebe {game.title}!"

    def answer_media_question(self, query: str) -> Optional[str]:
        """
        Beantwortet eine Frage über Medien mit echten Fakten.

        Args:
            query: Die Frage (z.B. "worum geht es in frieren?")

        Returns:
            Faktische Antwort oder None wenn nicht gefunden
        """
        q = query.lower()

        # Anime suchen
        for key, anime in self.anime_db.items():
            if key in q or anime.title.lower() in q:
                # Was für eine Frage?
                if any(w in q for w in ["worum", "story", "handlung", "plot"]):
                    return f"**{anime.title}** handelt von:\n\n{anime.synopsis}"

                elif any(w in q for w in ["charakter", "character", "wer ist", "protagonis"]):
                    chars = "\n".join([f"• **{c['name']}**: {c['role']}" for c in anime.main_characters[:4]])
                    return f"Die Hauptcharaktere in **{anime.title}**:\n\n{chars}"

                elif any(w in q for w in ["gut", "empfehl", "warum", "schau"]):
                    return f"*Ohren spitzen sich* {anime.why_i_love_it}\n\n💡 {random.choice(anime.fun_facts) if anime.fun_facts else ''}"

                elif any(w in q for w in ["fakt", "fact", "trivia", "wusstest"]):
                    if anime.fun_facts:
                        return f"Fun Facts über **{anime.title}**:\n\n" + "\n".join([f"• {f}" for f in anime.fun_facts])

                # Default: Übersicht
                return self.generate_anime_talk(anime, "discussing")

        # Spiele suchen
        for key, game in self.games_db.items():
            if key in q or game.title.lower() in q:
                if any(w in q for w in ["gameplay", "spielt sich", "wie funktioniert"]):
                    return f"**{game.title}** Gameplay:\n\n{game.gameplay_description}"

                elif any(w in q for w in ["tipp", "tip", "hilfe", "rat"]):
                    if game.tips:
                        return f"Tipps für **{game.title}**:\n\n" + "\n".join([f"• {t}" for t in game.tips])

                elif any(w in q for w in ["gut", "empfehl", "warum", "spiel"]):
                    return f"*wedelt* {game.why_i_love_it}"

                return self.generate_game_talk(game, "discussing")

        # Musik suchen
        for key, music in self.music_db.items():
            if key in q or music.title.lower() in q or music.artist.lower() in q:
                parts = [f"**{music.title}** von {music.artist}"]
                if music.known_from:
                    parts.append(f"Bekannt aus: {music.known_from}")
                if music.lyrics_theme:
                    parts.append(f"Thema: {music.lyrics_theme}")
                if music.why_i_love_it:
                    parts.append(f"\n*{music.why_i_love_it}*")
                if music.fun_facts:
                    parts.append(f"\n💡 {random.choice(music.fun_facts)}")

                return "\n".join(parts)

        return None


# =========================================================================
# SINGLETON INSTANZ
# =========================================================================

_media_kb_instance: Optional[MediaKnowledgeBase] = None

def get_media_knowledge() -> MediaKnowledgeBase:
    """Gibt die Singleton-Instanz der MediaKnowledgeBase zurück."""
    global _media_kb_instance
    if _media_kb_instance is None:
        _media_kb_instance = MediaKnowledgeBase()
    return _media_kb_instance


# =========================================================================
# TEST
# =========================================================================

if __name__ == "__main__":
    kb = MediaKnowledgeBase()

    print("=== ANIME TEST ===")
    frieren = kb.get_anime("frieren")
    if frieren:
        print(f"Titel: {frieren.title}")
        print(f"Synopsis: {frieren.synopsis[:100]}...")
        print(f"Holos Meinung: {frieren.why_i_love_it}")

    print("\n=== GAME TEST ===")
    stardew = kb.get_game("stardew")
    if stardew:
        print(f"Titel: {stardew.title}")
        print(f"Gameplay: {stardew.gameplay_description[:100]}...")
        print(f"Tipp: {stardew.tips[0] if stardew.tips else 'Keine'}")

    print("\n=== QUESTION TEST ===")
    answer = kb.answer_media_question("worum geht es in frieren?")
    print(answer)
