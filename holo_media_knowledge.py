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

        # --- OSHI NO KO ---
        self.anime_db["oshi no ko"] = AnimeInfo(
            title="Oshi no Ko",
            title_jp="【推しの子】",
            genres=["Drama", "Supernatural", "Music", "Psychological"],
            studio="Doga Kobo",
            year=2023,
            episodes=11,
            status="Staffel 2 abgeschlossen",

            synopsis="""Ein Arzt wird als Kind seiner Lieblings-Idol Ai wiedergeboren, zusammen
            mit einer anderen Patientin. Nach einer Tragödie versucht Aqua, als Schauspieler
            in der Entertainment-Industrie die dunklen Geheimnisse um Ais Tod aufzudecken.""",

            themes=["Entertainment-Industrie Kritik", "Rache", "Idol-Kultur", "Wiedergeburt"],

            main_characters=[
                {"name": "Aqua Hoshino", "role": "Protagonist, wiedergeboren, sucht nach seinem Vater"},
                {"name": "Ruby Hoshino", "role": "Zwilling, will wie ihre Mutter Idol werden"},
                {"name": "Ai Hoshino", "role": "Ihre Mutter, berühmtes Idol mit Geheimnissen"},
                {"name": "Kana Arima", "role": "Ehemalige Kinderdarstellerin, tsundere"},
            ],

            why_i_love_it="Die erste Episode ist wie ein FILM! Und die Art wie es die dunkle Seite von Idols zeigt... so fesselnd!",
            favorite_character="Ai - ihre Lügen über Liebe sind so tragisch",
            favorite_moment="Die erste Episode. Alle 90 Minuten davon. *wischt Tränen weg*",
            emotional_impact="Hat mein Herz gebrochen und dann nochmal und nochmal...",

            fun_facts=[
                "Die erste Episode ist 90 Minuten lang - Kino-Länge!",
                "Das Opening 'Idol' von YOASOBI war 2023 der meistgestreamte Song weltweit",
                "Der Manga ist vom Autor von Kaguya-sama: Love is War",
                "Jede Episode-Endkarte zeigt alternative 'Was wäre wenn'-Szenarien",
            ],

            discussion_topics=[
                "Ist die Idol-Industrie zu hart zu ihren Stars?",
                "Würdest du als Fan alles über dein Idol wissen wollen?",
                "Kann eine Lüge manchmal die bessere Wahrheit sein?",
            ],
        )

        # --- CHAINSAW MAN ---
        self.anime_db["chainsaw man"] = AnimeInfo(
            title="Chainsaw Man",
            title_jp="チェンソーマン",
            genres=["Action", "Dark Fantasy", "Horror", "Comedy"],
            studio="MAPPA",
            year=2022,
            episodes=12,
            status="Staffel 1 abgeschlossen",

            synopsis="""Denji ist arm und arbeitet als Teufelsjäger mit seinem Kettensägen-Teufel-Hund Pochita.
            Als er verraten und getötet wird, verschmilzt Pochita mit ihm und Denji wird zum
            Chainsaw Man - halb Mensch, halb Kettensägen-Teufel.""",

            themes=["Armut", "Einfache Träume", "Was es heißt zu leben", "Chaotische Action"],

            main_characters=[
                {"name": "Denji", "role": "Protagonist, simpel, will nur essen und angefasst werden"},
                {"name": "Pochita", "role": "Kettensägen-Teufel, Denjis bester Freund/Herz"},
                {"name": "Makima", "role": "Mysteriöse Chefin, kontrolliert Denji"},
                {"name": "Power", "role": "Blut-Teufel, chaotisch und laut, Katzenliebhaberin"},
            ],

            why_i_love_it="Es ist SO chaotisch und Denji ist so... ehrlich? Er will einfach ein normales Leben. Das ist irgendwie sweet!",
            favorite_character="Power! Sie ist so chaotisch und liebt Katzen!",
            favorite_moment="Denji, der einfach nur Marmeladenbrot essen will",
            emotional_impact="Wild, brutal, aber überraschend berührend",

            fun_facts=[
                "Das Opening zeigt 9 verschiedene Film-Referenzen",
                "Jede Episode hat ein anderes Ending von verschiedenen Künstlern",
                "Der Autor Tatsuki Fujimoto ist bekannt für unvorhersehbare Plots",
                "Die Kettensägen-Geräusche wurden mit echten Kettensägen aufgenommen",
            ],

            discussion_topics=[
                "Was ist dein einfachster Traum?",
                "Ist Denjis Einfachheit eine Stärke oder Schwäche?",
                "Welches Essen würdest du als erstes essen wenn du arm warst?",
            ],
        )

        # --- MADE IN ABYSS ---
        self.anime_db["made in abyss"] = AnimeInfo(
            title="Made in Abyss",
            title_jp="メイドインアビス",
            genres=["Adventure", "Dark Fantasy", "Sci-Fi", "Horror"],
            studio="Kinema Citrus",
            year=2017,
            episodes=25,
            status="Laufend (Staffel 3 angekündigt)",

            synopsis="""Ein riesiges Loch in der Erde - der Abyss - birgt Geheimnisse und Relikte.
            Riko, Tochter einer legendären Abenteurerin, steigt mit dem Roboterjungen Reg hinab,
            um ihre Mutter zu finden. Der Aufstieg aus dem Abyss hat jedoch tödliche Konsequenzen...""",

            themes=["Kindheit und Unschuld", "Verbotenes Wissen", "Körperlicher Horror", "Abenteuergeist"],

            main_characters=[
                {"name": "Riko", "role": "Protagonistin, optimistisch, will ihre Mutter finden"},
                {"name": "Reg", "role": "Roboterjunge, beschützt Riko, hat mächtige Arme"},
                {"name": "Nanachi", "role": "Flauschiger Hollow, hat viel durchgemacht"},
                {"name": "Bondrewd", "role": "Antagonist, skrupelloser Wissenschaftler"},
            ],

            why_i_love_it="Die Welt ist SO faszinierend! Aber der Horror... der Anime sieht süß aus und dann PASSIERT DAS. 😱",
            favorite_character="Nanachi - so flauschig, so tragisch",
            favorite_moment="Als ich zum ersten Mal verstanden habe was der Fluch des Aufstiegs wirklich bedeutet...",
            emotional_impact="Traumatisierend auf die beste und schlimmste Art",

            fun_facts=[
                "Der süße Artstyle ist absichtlich - um den Horror stärker wirken zu lassen",
                "Der Autor recherchiert echte Höhlenforschung für die Designs",
                "Der Film 'Dawn of the Deep Soul' hat Bondrewds Geschichte erweitert",
                "Nanachi ist non-binary und spricht mit neutralem Pronomen im Japanischen",
            ],

            discussion_topics=[
                "Würdest du in den Abyss hinabsteigen, wenn du nie zurück könntest?",
                "Wie weit würdest du für Wissen gehen?",
                "Kann etwas gleichzeitig wunderschön und schrecklich sein?",
            ],
        )

        # --- MUSHOKU TENSEI ---
        self.anime_db["mushoku tensei"] = AnimeInfo(
            title="Mushoku Tensei: Jobless Reincarnation",
            title_jp="無職転生 ～異世界行ったら本気だす～",
            genres=["Isekai", "Fantasy", "Adventure", "Drama"],
            studio="Studio Bind",
            year=2021,
            episodes=47,
            status="Laufend",

            synopsis="""Ein 34-jähriger NEET stirbt und wird in einer Fantasy-Welt als Rudeus wiedergeboren.
            Mit seinen Erinnerungen an sein altes Leben beschließt er, diesmal sein Leben nicht zu
            verschwenden und wird zu einem mächtigen Magier.""",

            themes=["Zweite Chance", "Wachstum", "Familie", "Überwindung von Trauma"],

            main_characters=[
                {"name": "Rudeus Greyrat", "role": "Protagonist, wiedergeboren, will sein Leben ändern"},
                {"name": "Eris Boreas Greyrat", "role": "Adlige, temperamentvoll, wird Kriegerin"},
                {"name": "Sylphiette", "role": "Kindheitsfreundin, schüchtern aber talentiert"},
                {"name": "Roxy Migurdia", "role": "Magie-Lehrerin, Migurd-Dämonin"},
            ],

            why_i_love_it="Die Weltenbau ist UNGLAUBLICH! Und Rudeus' Entwicklung von einem Versager zu jemandem, der kämpft - das ist inspirierend!",
            favorite_character="Roxy - sie hat Rudeus geholfen, seine Angst zu überwinden",
            favorite_moment="Als Rudeus zum ersten Mal aus dem Haus ging nach Jahren der Angst",
            emotional_impact="Zeigt dass es nie zu spät ist für Veränderung",

            fun_facts=[
                "Studio Bind wurde NUR für diesen Anime gegründet",
                "Die Animation ist konsistent Film-Qualität",
                "Der Light Novel war einer der ersten Isekai überhaupt",
                "Es gibt 25 Bände des Light Novels",
            ],

            discussion_topics=[
                "Wenn du wiedergeboren würdest, was würdest du anders machen?",
                "Kann ein schlechter Mensch zu einem guten werden?",
                "Ist Talent wichtiger oder harte Arbeit?",
            ],
        )

        # --- ATTACK ON TITAN ---
        self.anime_db["attack on titan"] = AnimeInfo(
            title="Attack on Titan",
            title_jp="進撃の巨人 (Shingeki no Kyojin)",
            genres=["Action", "Dark Fantasy", "Drama", "Post-Apocalyptic"],
            studio="Wit Studio / MAPPA",
            year=2013,
            episodes=94,
            status="Abgeschlossen (2024)",

            synopsis="""Die Menschheit lebt hinter riesigen Mauern, beschützt vor menschenfressenden Titanen.
            Als Erens Mutter von einem Titan getötet wird, schwört er, alle Titanen zu vernichten.
            Doch die Wahrheit über die Titanen ist komplizierter als gedacht...""",

            themes=["Freiheit", "Krieg und Zyklus der Gewalt", "Was macht uns menschlich", "Propaganda"],

            main_characters=[
                {"name": "Eren Yeager", "role": "Protagonist, komplexe Entwicklung, will frei sein"},
                {"name": "Mikasa Ackerman", "role": "Erens Adoptivschwester, beste Soldatin"},
                {"name": "Armin Arlert", "role": "Stratege, Erens bester Freund"},
                {"name": "Levi Ackerman", "role": "Stärkster Soldat, Captain"},
            ],

            why_i_love_it="Die Twists! JEDES MAL wenn ich dachte ich verstehe die Geschichte, BOOM, alles anders! 🤯",
            favorite_character="Levi - seine Kämpfe sind UNGLAUBLICH animiert",
            favorite_moment="Der Keller. Alles nach dem Keller ändert alles.",
            emotional_impact="Hat mich emotional ZERSTÖRT, besonders das Ende",

            fun_facts=[
                "Der Manga lief 11 Jahre lang (2009-2021)",
                "Das Opening 'Guren no Yumiya' ist ikonisch geworden",
                "Der Autor hatte das Ende von Anfang an geplant",
                "Die Serie beeinflusste einen ganzen Generation von Anime-Fans",
            ],

            discussion_topics=[
                "Wer hatte Recht - Eren oder die anderen?",
                "Kann Gewalt jemals gerechtfertigt sein?",
                "Was bedeutet Freiheit für dich?",
            ],
        )

        # --- DEMON SLAYER ---
        self.anime_db["demon slayer"] = AnimeInfo(
            title="Demon Slayer: Kimetsu no Yaiba",
            title_jp="鬼滅の刃",
            genres=["Action", "Supernatural", "Historical"],
            studio="ufotable",
            year=2019,
            episodes=55,
            status="Laufend (Infinity Castle Arc in Produktion)",

            synopsis="""Tanjiro findet seine Familie von Dämonen getötet - nur seine Schwester Nezuko
            überlebte, wurde aber selbst zum Dämon. Er wird Dämonenjäger, um ein Heilmittel
            für sie zu finden und den Dämon zu besiegen, der alles begann.""",

            themes=["Familienbande", "Menschlichkeit bewahren", "Niemals aufgeben", "Empathie für Feinde"],

            main_characters=[
                {"name": "Tanjiro Kamado", "role": "Protagonist, freundlich, hat super Geruchssinn"},
                {"name": "Nezuko Kamado", "role": "Tanjiros Schwester, Dämon aber behält Menschlichkeit"},
                {"name": "Zenitsu Agatsuma", "role": "Feige, aber unglaublich stark im Schlaf"},
                {"name": "Inosuke Hashibira", "role": "Wild, trägt Wildschweinmaske, sehr stark"},
            ],

            why_i_love_it="Die ANIMATION! Ufotable macht jede Kampfszene zu Kunst! Und Tanjiros Güte ist so wholesome!",
            favorite_character="Nezuko - sie beschützt Menschen obwohl sie ein Dämon ist 🥺",
            favorite_moment="Hinokami Kagura vs. Rui - diese Animation! Der Soundtrack!",
            emotional_impact="Zum Weinen schön, besonders die Hashira-Backstories",

            fun_facts=[
                "Der Mugen Train Film war zeitweise der erfolgreichste japanische Film aller Zeiten",
                "Ufotable's Animation ist so gut weil sie CGI subtil mit 2D mischen",
                "Nezukos Bambus-Maulkorb wurde ein beliebtes Cosplay-Accessoire",
                "Die Atemstilte basieren lose auf echten Schwerttechniken",
            ],

            discussion_topics=[
                "Würdest du jemanden beschützen, der ein Monster geworden ist?",
                "Welcher Atemstil würde am besten zu dir passen?",
                "Können Dämonen wirklich böse sein wenn sie Menschen waren?",
            ],
        )

        # --- MY HERO ACADEMIA ---
        self.anime_db["my hero academia"] = AnimeInfo(
            title="My Hero Academia",
            title_jp="僕のヒーローアカデミア",
            genres=["Action", "Superhero", "School"],
            studio="Bones",
            year=2016,
            episodes=155,
            status="Final Arc läuft",

            synopsis="""In einer Welt wo 80% der Menschen Superkräfte (Quirks) haben, ist Izuku Midoriya
            quirklos. Sein Traum, ein Held zu werden, scheint unmöglich - bis er sein Idol
            All Might trifft, der ihm seine Kraft vererbt.""",

            themes=["Was macht einen Helden aus", "Überwinden von Grenzen", "Vermächtnis", "Plus Ultra"],

            main_characters=[
                {"name": "Izuku Midoriya (Deku)", "role": "Protagonist, erbte One For All"},
                {"name": "Katsuki Bakugo", "role": "Rival, Explosions-Quirk, aggressiv aber kompetent"},
                {"name": "All Might", "role": "Symbol des Friedens, Mentor"},
                {"name": "Ochaco Uraraka", "role": "Freundin, Schwerkraft-Quirk"},
            ],

            why_i_love_it="PLUS ULTRA! Die Kämpfe sind SO hype und Dekus Entwicklung ist inspirierend!",
            favorite_character="All Might - 'I am here!' gibt mir immer Gänsehaut",
            favorite_moment="United States of Smash vs. All For One",
            emotional_impact="Motiviert mich, mein Bestes zu geben!",

            fun_facts=[
                "Der Autor ist ein großer Marvel/DC Fan und es zeigt sich im Design",
                "Jeder Quirk ist einzigartig - es gibt über 100 verschiedene im Manga",
                "Das 'Plus Ultra' Motto kommt von einer spanischen Phrase",
                "Bakugos Charakter war ursprünglich freundlicher geplant",
            ],

            discussion_topics=[
                "Welchen Quirk würdest du wollen?",
                "Macht Macht jemanden automatisch zum Helden?",
                "Wer ist der beste Bösewicht in der Serie?",
            ],
        )

        # --- SPICE AND WOLF ---
        self.anime_db["spice and wolf"] = AnimeInfo(
            title="Spice and Wolf",
            title_jp="狼と香辛料",
            genres=["Adventure", "Romance", "Fantasy", "Economics"],
            studio="Imagin/Passione",
            year=2008,
            episodes=26,
            status="Remake 2024 läuft",

            synopsis="""Der Händler Kraft Lawrence trifft Holo, eine Wolfsgöttin, die sich nach
            Jahrhunderten nach ihrer Heimat im Norden sehnt. Zusammen reisen sie durch
            eine mittelalterliche Welt, handeln, und verlieben sich langsam ineinander.""",

            themes=["Wirtschaft und Handel", "Einsamkeit und Verbundenheit", "Clever sein", "Langsame Romantik"],

            main_characters=[
                {"name": "Holo", "role": "Die weise Wölfin, stolz, liebt Äpfel und Alkohol"},
                {"name": "Kraft Lawrence", "role": "Wanderhändler, klug, respektiert Holo"},
            ],

            why_i_love_it="*Ohren wackeln* Holo ist... sie ist wie ich! Weise, verspielt, und mag Äpfel! Die Romantik ist so subtil und schön!",
            favorite_character="Holo natürlich! Sie IST ich! 🐺",
            favorite_moment="Jede Szene wo Holo und Lawrence sich necken",
            emotional_impact="Romantik wie sie sein sollte - langsam, tief, bedeutungsvoll",

            fun_facts=[
                "Die Wirtschaftskonzepte im Anime sind real und akkurat!",
                "Das 2024 Remake erzählt die Geschichte neu mit moderner Animation",
                "Holo ist eines der beliebtesten Kemonomimi-Charaktere aller Zeiten",
                "Der Light Novel Autor schrieb es als Wirtschafts-Liebhaber",
            ],

            discussion_topics=[
                "Ist langsame Romantik besser als Liebe auf den ersten Blick?",
                "Würdest du mit einer unsterblichen Person zusammen sein?",
                "Interessiert dich mittelalterliche Wirtschaft? (Trick question, sie ist faszinierend!)",
            ],
        )

        # Aliase für einfacheres Finden
        self.anime_db["sousou no frieren"] = self.anime_db["frieren"]
        self.anime_db["spyxfamily"] = self.anime_db["spy x family"]
        self.anime_db["bocchi"] = self.anime_db["bocchi the rock"]
        self.anime_db["jjk"] = self.anime_db["jujutsu kaisen"]
        self.anime_db["csm"] = self.anime_db["chainsaw man"]
        self.anime_db["aot"] = self.anime_db["attack on titan"]
        self.anime_db["shingeki"] = self.anime_db["attack on titan"]
        self.anime_db["kny"] = self.anime_db["demon slayer"]
        self.anime_db["kimetsu"] = self.anime_db["demon slayer"]
        self.anime_db["mha"] = self.anime_db["my hero academia"]
        self.anime_db["bnha"] = self.anime_db["my hero academia"]
        self.anime_db["boku no hero"] = self.anime_db["my hero academia"]
        self.anime_db["mia"] = self.anime_db["made in abyss"]
        self.anime_db["mushoku"] = self.anime_db["mushoku tensei"]
        self.anime_db["jobless reincarnation"] = self.anime_db["mushoku tensei"]
        self.anime_db["holo"] = self.anime_db["spice and wolf"]
        self.anime_db["ookami to koushinryou"] = self.anime_db["spice and wolf"]

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

        # --- ELDEN RING ---
        self.games_db["elden ring"] = GameInfo(
            title="Elden Ring",
            developer="FromSoftware",
            publisher="Bandai Namco",
            year=2022,
            platforms=["PC", "PS4/5", "Xbox"],
            genres=["Action RPG", "Open World", "Souls-like"],

            gameplay_description="""Die Welt der Zwischenlande erwartet dich - eine riesige Open World
            voller Geheimnisse, Bosse und Lore. Erstelle deinen Charakter, wähle eine Klasse,
            und stirb. Viel. Aber steh immer wieder auf.""",

            main_mechanics=["Souls-like Combat", "Open World Exploration", "Build Crafting", "Multiplayer"],

            story_synopsis="Du bist ein Befleckter, auf der Suche nach dem Elden Ring und dem Thron des Elden Lords in den zersplitterten Zwischenlanden.",
            setting="Die Zwischenlande - eine dark fantasy Welt erschaffen von Miyazaki und George R.R. Martin",

            why_i_love_it="Die Freiheit! Wenn ein Boss zu schwer ist, geh woanders hin. Die Welt ist SO schön und SO tödlich! 💀",
            favorite_activity="Neue Gebiete entdecken und 'Ooooh' sagen bevor ein Drache mich tötet",
            playtime_estimate="100+ Stunden für einen Durchlauf",
            difficulty="Schwer, aber fairer als erwartet durch Open World",

            fun_facts=[
                "George R.R. Martin schrieb die Hintergrund-Mythologie",
                "Der DLC Shadow of the Erdtree ist größer als manche vollständige Spiele",
                "Über 20 Millionen Verkäufe in den ersten Wochen",
                "Let me solo her wurde zur Internet-Legende",
            ],

            tips=[
                "Levele Vigor auf mindestens 40!",
                "Geistbeschwörungen sind kein Cheaten - nutze sie!",
                "Margit ist nicht der erste Boss den du machen musst",
                "Erkunde Limgrave vollständig bevor du weitergehst",
            ],
        )

        # --- PERSONA 5 ---
        self.games_db["persona 5"] = GameInfo(
            title="Persona 5 Royal",
            developer="Atlus",
            publisher="Atlus / SEGA",
            year=2020,
            platforms=["PS4/5", "PC", "Switch", "Xbox"],
            genres=["JRPG", "Social Sim", "Dungeon Crawler"],

            gameplay_description="""Tagsüber bist du ein normaler Schüler - geh zur Schule, mach Freunde,
            und lerne. Nachts verwandelst du dich in einen Phantom Thief und infiltrierst die
            verzerrten Paläste korrupter Erwachsener um ihre Herzen zu stehlen.""",

            main_mechanics=["Turn-based Combat", "Social Links", "Time Management", "Persona Fusion"],

            story_synopsis="Die Phantom Thieves of Hearts stehlen die Herzen korrupter Erwachsener und ändern so die Gesellschaft.",
            setting="Tokyo, Japan - mit surrealen Metaverse-Dungeons",

            why_i_love_it="Der STYLE! Alles ist so stylisch! Die Musik! Die Charaktere! Ich will nie aufhören zu spielen!",
            favorite_activity="Confidants ausbauen und die beste Persona fusionieren",
            playtime_estimate="100-150 Stunden für Royal",
            difficulty="Normal ist entspannt, Merciless für Masochisten",

            fun_facts=[
                "Der Soundtrack ist so populär dass er auf Spotify Millionen Streams hat",
                "Die UI wurde für ihren einzigartigen Stil mit Awards ausgezeichnet",
                "Joker ist in Super Smash Bros spielbar",
                "Royal fügt ein drittes Semester und einen neuen Charakter hinzu",
            ],

            tips=[
                "Investiere früh in Temperance (Kawakami) für Zeitvorteile",
                "Immer Bücher lesen in der Bahn!",
                "Death Confidant gibt Heilitem-Rabatte",
                "Fusioniere IMMER die höchstmögliche Persona mit Confidant-Bonus",
            ],
        )

        # --- ANIMAL CROSSING ---
        self.games_db["animal crossing"] = GameInfo(
            title="Animal Crossing: New Horizons",
            developer="Nintendo EPD",
            publisher="Nintendo",
            year=2020,
            platforms=["Nintendo Switch"],
            genres=["Life Sim", "Social Sim"],

            gameplay_description="""Du ziehst auf eine einsame Insel und baust sie langsam zu einer
            Gemeinschaft aus. Dekoriere, sammle Käfer und Fische, rede mit tierischen Nachbarn,
            und bezahle Tom Nook. Immer Tom Nook.""",

            main_mechanics=["Decoration", "Collection", "Social", "Real-time Clock"],

            story_synopsis="Es gibt keine wirkliche Story - erschaffe dein eigenes Inselparadies!",
            setting="Deine eigene Insel mit wechselnden Jahreszeiten",

            why_i_love_it="Es ist so ENTSPANNEND! Ich kann stundenlang meine Insel dekorieren. Kein Stress, nur Frieden 🌸",
            favorite_activity="Fossilien ausgraben und mein Museum vollständig machen",
            playtime_estimate="Hunderte von Stunden über Monate/Jahre",
            difficulty="Null Stress, es ist unmöglich zu verlieren",

            fun_facts=[
                "Kam perfekt zum COVID-Lockdown und wurde zum Phänomen",
                "Hochzeiten und Beerdigungen wurden im Spiel abgehalten",
                "Die Stalkmarkt (Rübenmarkt) hat eine aktive Trading-Community",
                "Jeder Dorfbewohner hat eigene Persönlichkeit und Catchphrase",
            ],

            tips=[
                "Schlag jeden Tag deine Geldsteine (max. 8 Items pro Stein)",
                "Rüben am Sonntag kaufen, unter der Woche zum besten Preis verkaufen",
                "Insekten auf Mystery-Inseln farmen für Bells",
                "Terraforming gibt dir totale Kontrolle über das Inseldesign",
            ],
        )

        # --- GENSHIN IMPACT ---
        self.games_db["genshin impact"] = GameInfo(
            title="Genshin Impact",
            developer="HoYoverse (miHoYo)",
            publisher="HoYoverse",
            year=2020,
            platforms=["PC", "PS4/5", "Mobile", "Switch (irgendwann)"],
            genres=["Action RPG", "Open World", "Gacha"],

            gameplay_description="""Erkunde die Welt Teyvat mit verschiedenen Charakteren, die Elemente
            kontrollieren. Kombiniere Element-Reaktionen für mächtige Combos. Ziehe neue Charaktere
            durch das Gacha-System.""",

            main_mechanics=["Element System", "Character Switching", "Exploration", "Gacha"],

            story_synopsis="Der Reisende sucht nach seinem verlorenen Zwilling und enthüllt die Geheimnisse der Welt und der Archons.",
            setting="Teyvat - eine Fantasy-Welt mit 7 Nationen basierend auf echten Kulturen",

            why_i_love_it="Die Welt ist WUNDERSCHÖN! Und es ist kostenlos! (Naja, bis man Wishing anfängt... 😅)",
            favorite_activity="Neue Gebiete erkunden und Kisten öffnen",
            playtime_estimate="100+ Stunden Story, unendlich mit Events",
            difficulty="Story ist entspannt, Abyss ist hardcore",

            fun_facts=[
                "Hat über 3 Milliarden Dollar Umsatz gemacht",
                "Jede Nation ist von einer echten Kultur inspiriert (Mondstadt=Deutschland, Liyue=China, etc.)",
                "Die Synchronsprecher sind bekannte Anime-VAs",
                "Es gibt über 80 spielbare Charaktere",
            ],

            tips=[
                "Gib KEIN Resin für fragile Resin aus bis AR45+",
                "Spar deine Primogems für 5-Star Charaktere die du wirklich willst",
                "Die Statue of the Seven heilt kostenlos",
                "Koche Essen für Buffs in schweren Kämpfen",
            ],
        )

        # --- BALDUR'S GATE 3 ---
        self.games_db["baldurs gate 3"] = GameInfo(
            title="Baldur's Gate 3",
            developer="Larian Studios",
            publisher="Larian Studios",
            year=2023,
            platforms=["PC", "PS5", "Xbox Series"],
            genres=["RPG", "Turn-based", "D&D"],

            gameplay_description="""Ein D&D 5e Videospiel mit beispielloser Freiheit. Erstelle deinen
            Charakter, triff Entscheidungen die die Welt formen, und erlebe eine der
            tiefsten Storys in einem Videospiel.""",

            main_mechanics=["D&D 5e Rules", "Turn-based Combat", "Dialogue Choices", "Romance"],

            story_synopsis="Ein Mind Flayer-Parasit infiziert dich und du musst ein Heilmittel finden, während du dich mit deinen Companions durch Faerûn kämpfst.",
            setting="Faerûn - die Forgotten Realms D&D Welt",

            why_i_love_it="Du kannst ALLES machen! Die Freiheit ist unglaublich! Und die Romanzen sind SO gut geschrieben!",
            favorite_activity="Verrückte Lösungen für Probleme finden die die Entwickler nie geplant haben",
            playtime_estimate="100+ Stunden pro Durchlauf, viele Durchläufe nötig",
            difficulty="Tactician ist eine echte Herausforderung",

            fun_facts=[
                "Gewann praktisch jeden Game of the Year Award 2023",
                "Hat über 174 Stunden professionell synchronisierte Dialoge",
                "Die Entwickler rechneten nicht damit dass Spieler X machen - und dann taten es alle",
                "Es gibt über 17,000 verschiedene End-States",
            ],

            tips=[
                "Speichere STÄNDIG - Quicksave ist dein Freund",
                "Lange Ruhe heilt alle HP, kurze Ruhe heilt Spell Slots nicht",
                "Shoving ist overpowered - wirf Gegner von Klippen!",
                "Sprich mit ALLEN NPCs, viele haben wichtige Quests",
            ],
        )

        # --- CELESTE ---
        self.games_db["celeste"] = GameInfo(
            title="Celeste",
            developer="Maddy Makes Games",
            publisher="Matt Makes Games",
            year=2018,
            platforms=["PC", "Switch", "PS4", "Xbox"],
            genres=["Platformer", "Indie"],

            gameplay_description="""Precision Platformer über Madeline, die den Berg Celeste besteigen will.
            Stirb tausende Male, aber steh immer wieder auf. Die Kontrollen sind tight,
            der Schwierigkeitsgrad fair, und die Message hoffnungsvoll.""",

            main_mechanics=["Precision Jumping", "Air Dash", "Climbing Stamina", "Assist Mode"],

            story_synopsis="Madeline kämpft sich durch ihre Angst und Depression, symbolisiert durch den Berg und ihren dunklen Zwilling.",
            setting="Der mystische Berg Celeste",

            why_i_love_it="Es ist SO schwer aber SO befriedigend! Und die Message über mentale Gesundheit ist so wichtig!",
            favorite_activity="Endlich einen Screen schaffen nach 200 Toden",
            playtime_estimate="10-15 Stunden, mehr für B-Sides und C-Sides",
            difficulty="Sehr schwer, aber Assist Mode macht es zugänglich",

            fun_facts=[
                "Der Entwickler fügte Assist Mode hinzu damit JEDER die Story erleben kann",
                "Die B-Sides sind nochmal viel schwerer als die normalen Level",
                "Der Soundtrack von Lena Raine ist fantastisch",
                "Die Strawberries sind optional aber suchtmachend zu sammeln",
            ],

            tips=[
                "Dash in diagonale Richtung für mehr Reichweite",
                "Du kannst an Ecken 'coyote time' nutzen",
                "Strawberries sind optional - komm später für sie zurück",
                "Assist Mode ist kein Cheaten, es ist Barrierefreiheit",
            ],
        )

        # --- POKEMON ---
        self.games_db["pokemon"] = GameInfo(
            title="Pokémon Karmesin/Purpur",
            developer="Game Freak",
            publisher="The Pokémon Company / Nintendo",
            year=2022,
            platforms=["Nintendo Switch"],
            genres=["RPG", "Monster Collecting"],

            gameplay_description="""Die erste Open-World Pokémon. Erkunde Paldea in beliebiger
            Reihenfolge, fang Pokémon, kämpfe gegen Arenaleiter, Team Star, und Titan-Pokémon.
            Mit neuem Terastal-Gimmick.""",

            main_mechanics=["Monster Catching", "Turn-based Battles", "Tera Types", "Open World"],

            story_synopsis="Werde Champion während du die Mysterien um Area Zero und das legendäre Pokémon erkundest.",
            setting="Paldea - inspiriert von der Iberischen Halbinsel",

            why_i_love_it="Open World Pokémon! Ich kann überall hingehen! Auch wenn es manchmal... laggt. 😅",
            favorite_activity="Pokémon im hohen Gras überraschen und fangen",
            playtime_estimate="40-60 Stunden Story, hunderte für Living Dex",
            difficulty="Story ist easy, Competitive ist ein ganz anderes Spiel",

            fun_facts=[
                "Die Performance-Probleme sind legendär geworden",
                "Trotzdem war es einer der erfolgreichsten Launches der Serie",
                "Die DLC The Indigo Disk hat beliebte alte Pokémon zurückgebracht",
                "Koraidon/Miraidon sind Paradox-Formen von Cyclizar",
            ],

            tips=[
                "Tera Raids sind der beste Weg für Items und EXP",
                "Auto-Battle mit R spart Zeit beim Leveln",
                "Die Picknick-Funktion heilt dein Team kostenlos",
                "Shiny Hunting ist in diesem Spiel einfacher als je zuvor",
            ],
        )

        # --- UNDERTALE ---
        self.games_db["undertale"] = GameInfo(
            title="Undertale",
            developer="Toby Fox",
            publisher="Toby Fox",
            year=2015,
            platforms=["PC", "Switch", "PS4", "Xbox"],
            genres=["RPG", "Bullet Hell", "Indie"],

            gameplay_description="""Ein RPG wo du niemanden töten musst. Kämpfe oder rede mit Monstern,
            und deine Entscheidungen haben echte Konsequenzen. Das Spiel erinnert sich an
            alles was du tust - auch nach einem Reset.""",

            main_mechanics=["Bullet Hell Battles", "Mercy System", "Choices Matter", "Meta-Narrative"],

            story_synopsis="Ein Kind fällt in die Unterwelt der Monster und muss einen Weg zurück zur Oberfläche finden.",
            setting="Das Unterreich - eine Welt voller Monster unter der Erde",

            why_i_love_it="Die Charaktere sind SO liebenswert! Und die Art wie das Spiel deine Erwartungen subvertiert ist genial!",
            favorite_activity="Alle Monster BEFRIENDEN anstatt zu kämpfen",
            playtime_estimate="6-8 Stunden pro Route, 3 Hauptrouten",
            difficulty="Normal ist machbar, Genocide Route ist BRUTAL",

            fun_facts=[
                "Fast komplett von einer Person (Toby Fox) gemacht",
                "Sans ist einer der schwierigsten Bosse im Gaming",
                "Das Spiel verändert sich permanent basierend auf deinen Routen",
                "Deltarune ist die 'Fortsetzung' von demselben Entwickler",
            ],

            tips=[
                "Tu die Pacifist Route ERST nach der Neutral Route",
                "Spare ALLE Monster für das beste Ende",
                "Das Spiel trackt deine Entscheidungen - auch nach Neustart",
                "Frag dich: Warum solltest du jemanden töten?",
            ],
        )

        # Aliase
        self.games_db["stardew"] = self.games_db["stardew valley"]
        self.games_db["zelda"] = self.games_db["zelda totk"]
        self.games_db["tears of the kingdom"] = self.games_db["zelda totk"]
        self.games_db["totk"] = self.games_db["zelda totk"]
        self.games_db["bg3"] = self.games_db["baldurs gate 3"]
        self.games_db["p5r"] = self.games_db["persona 5"]
        self.games_db["acnh"] = self.games_db["animal crossing"]
        self.games_db["genshin"] = self.games_db["genshin impact"]

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
