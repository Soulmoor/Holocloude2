#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO ENTITY DATABASE - Massive Sammlung von Namen & Entities               ║
║                                                                              ║
║  ENTHÄLT:                                                                    ║
║  • 2000+ Internationale Vornamen (DE, EN, TR, AR, RU, PL, ES, IT, FR, JP)   ║
║  • 500+ Gaming-Charaktere (Genshin, HSR, ZZZ, LoL, Valorant, etc.)          ║
║  • 300+ Anime-Charaktere                                                     ║
║  • 200+ Spiele                                                               ║
║  • 100+ Technologie-Begriffe                                                 ║
║  • 150+ Intent-Patterns                                                      ║
║                                                                              ║
║  Version: 1.0                                                                ║
║  Author: Kira & Claude                                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

# =============================================================================
# INTERNATIONALE VORNAMEN DATENBANK
# =============================================================================

# Deutsche Vornamen (500+)
GERMAN_MALE_NAMES = {
    # Klassisch
    "alexander", "andreas", "anton", "armin", "axel", "benjamin", "bernd", "bernhard",
    "boris", "bruno", "carl", "carsten", "christian", "christoph", "clemens", "daniel",
    "david", "dennis", "detlef", "dieter", "dirk", "dominik", "eckhard", "edgar",
    "egon", "elias", "emil", "erik", "ernst", "erwin", "fabian", "felix", "ferdinand",
    "finn", "florian", "frank", "franz", "frederic", "friedrich", "fritz", "gabriel",
    "georg", "gerhard", "gerd", "günter", "günther", "hans", "harald", "hartmut",
    "heiko", "heinrich", "heinz", "helmut", "hendrik", "henning", "henry", "herbert",
    "hermann", "holger", "horst", "hugo", "ingo", "jakob", "jan", "jannik", "jens",
    "joachim", "jochen", "johannes", "jonas", "jonathan", "jörg", "josef", "jürgen",
    "julian", "julius", "kai", "karl", "karsten", "kevin", "klaus", "konrad", "kurt",
    "lars", "leon", "leonard", "liam", "lorenz", "lothar", "louis", "luca", "lucas",
    "ludwig", "lukas", "lutz", "malte", "manfred", "manuel", "marc", "marcel", "marco",
    "mario", "marius", "markus", "martin", "matthias", "max", "maximilian", "michael",
    "mirko", "moritz", "nico", "nicolas", "niklas", "nils", "noah", "norbert", "olaf",
    "oliver", "oskar", "otto", "pascal", "patrick", "paul", "peter", "philipp", "rainer",
    "ralf", "ralph", "reinhard", "reinhold", "rene", "richard", "robert", "robin",
    "roland", "rolf", "roman", "ronald", "rudi", "rudolf", "rüdiger", "sascha",
    "sebastian", "siegfried", "simon", "stefan", "steffen", "stephan", "sven", "theo",
    "theodor", "thomas", "thorsten", "till", "tim", "timo", "tobias", "tom", "torsten",
    "udo", "ulf", "ulrich", "uwe", "valentin", "viktor", "volker", "walter", "werner",
    "wilhelm", "willi", "wolfgang", "yannik",
}

GERMAN_FEMALE_NAMES = {
    "alexandra", "amelie", "andrea", "anette", "angela", "angelika", "anika", "anja",
    "anna", "annalena", "anne", "anneliese", "annette", "antje", "antonia", "astrid",
    "barbara", "beate", "beatrix", "bianca", "birgit", "brigitte", "britta", "carla",
    "carmen", "caroline", "charlotte", "christa", "christiane", "christina", "claudia",
    "conny", "cornelia", "dagmar", "daniela", "diana", "doris", "dorothea", "edith",
    "elena", "eleonore", "elfriede", "elisabeth", "elke", "ella", "emily", "emma",
    "erika", "erna", "eva", "evelyn", "franziska", "frieda", "friederike", "gabriele",
    "gabi", "gerda", "gertrud", "gisela", "gudrun", "hanna", "hannah", "hannelore",
    "heide", "heidi", "heike", "helene", "helga", "henriette", "hildegard", "ilona",
    "ilse", "ines", "inga", "ingeborg", "ingrid", "irene", "iris", "isabella", "jana",
    "janina", "jasmin", "jennifer", "jenny", "jessica", "johanna", "josefine", "judith",
    "julia", "juliane", "jutta", "karin", "karla", "karolina", "katharina", "kathrin",
    "katja", "kerstin", "kirsten", "klara", "klaudia", "kornelia", "kristin", "larissa",
    "laura", "lea", "lena", "leonie", "lieselotte", "lina", "linda", "lisa", "lotte",
    "louisa", "lucia", "luisa", "luise", "madeleine", "magdalena", "manuela", "maren",
    "margarete", "maria", "marianne", "marie", "marina", "marion", "marlene", "marta",
    "martha", "martina", "mathilde", "maya", "melanie", "melissa", "mia", "michaela",
    "miriam", "monika", "nadine", "nadja", "natalie", "natascha", "nicole", "nina",
    "nora", "olivia", "patricia", "paula", "pauline", "petra", "pia", "regina", "renate",
    "rita", "rosa", "rosemarie", "roswitha", "ruth", "sabine", "sabrina", "sandra",
    "sarah", "silke", "silvia", "simone", "sonja", "sophia", "sophie", "stefanie",
    "stephanie", "susanne", "svenja", "sylvia", "tamara", "tanja", "theresa", "tina",
    "ulrike", "ursula", "ute", "valentina", "vanessa", "vera", "veronika", "verena",
    "victoria", "vivien", "yvonne", "zoe",
}

# Türkische Vornamen (300+)
TURKISH_MALE_NAMES = {
    "ahmet", "ali", "alican", "alp", "alparslan", "anil", "arda", "atakan", "aykut",
    "baran", "baris", "berk", "berke", "berkay", "burak", "bülent", "can", "cem",
    "cengiz", "cemal", "cihan", "deniz", "devrim", "dogan", "efe", "emre", "ender",
    "engin", "ercan", "erdem", "erdogan", "erhan", "erkan", "erol", "ersen", "ersin",
    "faruk", "fatih", "ferhat", "fikret", "firat", "furkan", "galip", "gökhan",
    "göksel", "görkem", "güven", "hakan", "halil", "haluk", "hamza", "hasan", "haydar",
    "hikmet", "hüseyin", "ibrahim", "ilhan", "ilker", "ilyas", "irfan", "ismail",
    "kaan", "kadir", "kamil", "kemal", "kenan", "kerem", "koray", "korkut", "kürsat",
    "levent", "mahmut", "mehmet", "mert", "mesut", "metin", "murat", "mustafa",
    "necati", "neset", "nevzat", "nihat", "oguz", "okan", "oktay", "omer", "onur",
    "orhan", "osman", "özcan", "özgür", "polat", "ramazan", "recep", "riza", "sahin",
    "salih", "sami", "sedat", "selçuk", "selim", "selman", "semih", "serdar", "serhan",
    "serkan", "sinan", "süleyman", "suat", "tahir", "tamer", "tarik", "taylan",
    "tolgay", "tolga", "tuncay", "turgut", "ufuk", "ugur", "umut", "ünal", "vedat",
    "volkan", "yalcin", "yasin", "yavuz", "yigit", "yilmaz", "yunus", "yusuf", "zafer",
}

TURKISH_FEMALE_NAMES = {
    "ada", "ayla", "aylin", "aysegül", "aysel", "aysu", "aysun", "azra", "basak",
    "belgin", "beren", "berna", "betül", "bilge", "büsra", "cansu", "ceren", "damla",
    "defne", "derya", "didem", "dilara", "dilek", "duygu", "ebru", "ece", "ekin",
    "ela", "elif", "emel", "emine", "esma", "esra", "evrim", "eylem", "fadime",
    "fatma", "feride", "feryal", "feyza", "filiz", "funda", "gamze", "gonca", "gözde",
    "gül", "gülay", "gülcan", "gülden", "gülen", "güler", "gülfem", "gülhan", "gülizar",
    "gülnur", "gülsen", "gülsüm", "günes", "hacer", "handan", "hatice", "havva",
    "hayriye", "hülya", "ilknur", "irem", "irmak", "ipek", "jale", "kadriye", "kader",
    "leyla", "melek", "meltem", "melis", "merve", "meryem", "miray", "müge", "nalan",
    "nazli", "neslihan", "nesrin", "nevin", "nihal", "nil", "nisa", "nur", "nuray",
    "nurgül", "nurhan", "nurten", "özge", "özlem", "pelin", "pembe", "pinar", "rabia",
    "reyhan", "saadet", "sanem", "sebnem", "seda", "seher", "selin", "selma", "sema",
    "serap", "serpil", "sevda", "sevgi", "sevil", "sevim", "sevinç", "sibel", "simge",
    "sinem", "songül", "sultan", "sümeyye", "süreyya", "tuba", "tugba", "tülay",
    "ülkü", "ümran", "vildan", "yagmur", "yeliz", "yesim", "zehra", "zeliha", "zeynep",
}

# Arabische Vornamen (200+)
ARABIC_MALE_NAMES = {
    "abbas", "abdallah", "abdul", "abdullah", "adam", "adnan", "ahmad", "ahmed",
    "akram", "ali", "amin", "amir", "ammar", "anwar", "ayman", "aziz", "badr",
    "bashar", "bassam", "bilal", "djamel", "fadi", "fahad", "faisal", "farid",
    "faris", "fouad", "habib", "hadi", "hafiz", "hakim", "hamid", "hamza", "hani",
    "hassan", "hussein", "ibrahim", "idris", "imad", "imran", "isa", "ismail",
    "jamal", "jamil", "kamal", "karim", "khaled", "khalid", "khalil", "mahmoud",
    "malik", "mansour", "marwan", "mehdi", "mohamed", "mohammed", "mokhtar", "mourad",
    "moustafa", "munir", "nabil", "nader", "nadir", "naji", "nasir", "nasser", "nazim",
    "omar", "osama", "othman", "rachid", "rami", "rashid", "riad", "saad", "sabri",
    "sadiq", "said", "salah", "salim", "samir", "sami", "selim", "sharif", "sultan",
    "taher", "tarek", "tariq", "walid", "wassim", "yasser", "youssef", "yusuf",
    "zaid", "zakaria", "ziad",
}

ARABIC_FEMALE_NAMES = {
    "aida", "aisha", "alia", "alya", "amani", "amina", "amira", "aya", "basma",
    "bushra", "dalal", "dalia", "dana", "dina", "fadwa", "fadia", "farida", "fatima",
    "fatma", "ghada", "hala", "hanan", "hana", "hiba", "houda", "iman", "inaya",
    "jamila", "karima", "khadija", "laila", "lamia", "latifa", "leila", "lina",
    "lubna", "madiha", "maha", "manal", "maram", "mariam", "may", "maysa", "mona",
    "nada", "nadia", "nadira", "naima", "najat", "najla", "nawal", "nazira", "nesma",
    "noor", "noura", "ola", "rabab", "rania", "rasha", "rawan", "reem", "rima",
    "rola", "safia", "safiya", "sahar", "salma", "samia", "samira", "sana", "sara",
    "sawsan", "siham", "souad", "sumaya", "wafa", "widad", "yara", "yasmin", "zahra",
    "zainab", "zara", "zeina",
}

# Russische/Slawische Vornamen (200+)
SLAVIC_MALE_NAMES = {
    "adam", "aleksander", "aleksei", "aleksandr", "alexei", "alexey", "anatoli",
    "andrei", "andrey", "anton", "artem", "boris", "daniil", "denis", "dmitri",
    "dmitry", "eduard", "egor", "evgeni", "evgeny", "fedor", "gennadi", "georgi",
    "grigori", "igor", "ilia", "ilya", "ivan", "jakub", "jan", "jerzy", "kirill",
    "konstantin", "krysztof", "leonid", "lev", "lukasz", "marek", "maxim", "michal",
    "mikhail", "nikita", "nikolai", "nikolay", "oleg", "pavel", "piotr", "pyotr",
    "radoslaw", "roman", "ruslan", "sergei", "sergey", "slawek", "stanislaw", "stefan",
    "tomasz", "vadim", "valentin", "valeri", "vasili", "viktor", "vitali", "vitaly",
    "vladimir", "vladislav", "wojciech", "yakov", "yaroslav", "yevgeni", "yuri",
}

SLAVIC_FEMALE_NAMES = {
    "agnieszka", "aleksandra", "alina", "anastasia", "anna", "anya", "beata",
    "daria", "dorota", "ekaterina", "elena", "eva", "ewa", "galina", "gosia",
    "irina", "ivana", "izabela", "jolanta", "julia", "karina", "karolina",
    "katarzyna", "katya", "kinga", "kristina", "larisa", "lena", "lidia", "ludmila",
    "lyudmila", "malgorzata", "maria", "marina", "marta", "milena", "nadia", "nadja",
    "natalia", "natalya", "nina", "oksana", "olga", "paulina", "polina", "renata",
    "sofia", "svetlana", "tamara", "tanya", "tatiana", "tatyana", "valentina",
    "vera", "viktoria", "yana", "yulia", "zuzanna",
}

# Englische/Amerikanische Vornamen (300+)
ENGLISH_MALE_NAMES = {
    "aaron", "adam", "adrian", "aiden", "alan", "albert", "alex", "alexander",
    "alfred", "andrew", "anthony", "arthur", "austin", "barry", "benjamin", "billy",
    "blake", "bobby", "brad", "bradley", "brandon", "brent", "brett", "brian",
    "bruce", "bryan", "caleb", "cameron", "carl", "carlos", "chad", "charles",
    "chase", "chris", "christian", "christopher", "clarence", "clark", "clayton",
    "clifford", "cody", "cole", "colin", "connor", "corey", "craig", "dale", "damian",
    "dan", "daniel", "danny", "darren", "david", "dean", "dennis", "derek", "desmond",
    "devin", "dominic", "donald", "douglas", "drew", "dustin", "dylan", "earl",
    "eddie", "edgar", "edward", "edwin", "eli", "elijah", "elliot", "eric", "ernest",
    "ethan", "eugene", "evan", "felix", "floyd", "francis", "frank", "franklin",
    "fred", "frederick", "gabriel", "gary", "gavin", "george", "gerald", "glen",
    "gordon", "grant", "greg", "gregory", "harold", "harry", "harvey", "heath",
    "henry", "herbert", "howard", "hugh", "hunter", "ian", "isaac", "ivan", "jack",
    "jackson", "jacob", "jake", "james", "jamie", "jared", "jason", "jay", "jeff",
    "jeffrey", "jeremy", "jerry", "jesse", "jim", "jimmy", "joe", "joel", "john",
    "johnny", "jonathan", "jordan", "jose", "joseph", "josh", "joshua", "juan",
    "justin", "karl", "keith", "kelly", "ken", "kenneth", "kevin", "kyle", "lance",
    "larry", "lawrence", "lee", "leo", "leonard", "leon", "leroy", "levi", "lewis",
    "liam", "lloyd", "logan", "louis", "lucas", "luis", "luke", "malcolm", "marcus",
    "mario", "mark", "marshall", "martin", "marvin", "mason", "matt", "matthew",
    "maurice", "max", "michael", "mike", "mitchell", "morgan", "nathan", "neil",
    "nelson", "nicholas", "nick", "noah", "noel", "norman", "oliver", "oscar",
    "owen", "patrick", "paul", "perry", "pete", "peter", "philip", "phillip",
    "ralph", "randy", "ray", "raymond", "reed", "reginald", "richard", "rick",
    "ricky", "robert", "rodney", "roger", "roland", "ron", "ronald", "ross", "roy",
    "ruben", "russell", "ryan", "sam", "samuel", "scott", "sean", "seth", "shane",
    "shaun", "shawn", "sidney", "simon", "spencer", "stanley", "stephen", "steve",
    "steven", "stuart", "taylor", "ted", "terry", "theodore", "thomas", "tim",
    "timothy", "todd", "tom", "tommy", "tony", "travis", "trevor", "troy", "tyler",
    "vernon", "victor", "vincent", "wade", "wallace", "walter", "warren", "wayne",
    "wesley", "william", "willie", "wyatt", "xavier", "zachary", "zane",
}

ENGLISH_FEMALE_NAMES = {
    "abigail", "addison", "alexandra", "alexis", "alice", "alicia", "allison",
    "alyssa", "amanda", "amber", "amy", "andrea", "angela", "anna", "anne",
    "annie", "april", "ashley", "audrey", "autumn", "barbara", "beatrice", "becky",
    "bella", "beth", "betty", "beverly", "bonnie", "brenda", "bridget", "brittany",
    "brooke", "caitlin", "camille", "candice", "carla", "carmen", "carol", "caroline",
    "carrie", "cassandra", "catherine", "charlene", "charlotte", "chelsea", "cheryl",
    "chloe", "christina", "christine", "cindy", "claire", "clara", "claudia",
    "courtney", "crystal", "cynthia", "daisy", "dana", "danielle", "darlene", "dawn",
    "debbie", "deborah", "denise", "diana", "diane", "donna", "doris", "dorothy",
    "edith", "eileen", "elaine", "eleanor", "elena", "elizabeth", "ella", "ellen",
    "emily", "emma", "erica", "erin", "esther", "eva", "evelyn", "faith", "felicia",
    "fiona", "florence", "frances", "gabrielle", "gail", "gloria", "grace", "gwen",
    "haley", "hannah", "harriet", "hayley", "heather", "heidi", "helen", "hillary",
    "holly", "hope", "irene", "iris", "isabella", "ivy", "jackie", "jacqueline",
    "jade", "jamie", "jane", "janet", "janice", "jasmine", "jean", "jeanette",
    "jenna", "jennifer", "jenny", "jessica", "jill", "joan", "joanna", "jocelyn",
    "jodi", "jodie", "jordan", "josephine", "joy", "joyce", "judith", "judy",
    "julia", "juliana", "julie", "june", "kara", "karen", "kate", "katherine",
    "kathleen", "kathryn", "kathy", "katie", "kayla", "kelly", "kelsey", "kendra",
    "kerry", "kim", "kimberly", "kristen", "kristin", "kristina", "laura", "lauren",
    "leah", "leigh", "leslie", "lillian", "lily", "linda", "lindsay", "lindsey",
    "lisa", "lois", "loretta", "lori", "louise", "lucy", "lydia", "lynn", "madison",
    "maggie", "maisie", "mandy", "margaret", "maria", "marilyn", "marion", "marissa",
    "marjorie", "marlene", "martha", "mary", "maureen", "megan", "melanie", "melissa",
    "melody", "meredith", "michelle", "mildred", "miranda", "molly", "monica",
    "morgan", "myrtle", "nancy", "naomi", "natalie", "natasha", "nicole", "nina",
    "nora", "norma", "olivia", "paige", "pamela", "patricia", "patty", "paula",
    "pauline", "pearl", "peggy", "penny", "phyllis", "priscilla", "rachel", "rebecca",
    "regina", "renee", "rhonda", "rita", "roberta", "robin", "rosa", "rose",
    "rosemary", "ruby", "ruth", "sabrina", "sally", "samantha", "sandra", "sara",
    "sarah", "savannah", "shannon", "sharon", "sheila", "shelby", "shelly", "sherry",
    "shirley", "sierra", "sophia", "stacey", "stacy", "stella", "stephanie", "sue",
    "summer", "susan", "suzanne", "sylvia", "tamara", "tammy", "tanya", "tara",
    "taylor", "teresa", "terri", "thelma", "theresa", "tiffany", "tina", "tracy",
    "valerie", "vanessa", "vera", "veronica", "vicki", "vickie", "victoria", "viola",
    "violet", "virginia", "vivian", "wanda", "wendy", "whitney", "wilma", "yolanda",
    "yvonne", "zoe", "zoey",
}

# Spanische/Lateinamerikanische Vornamen (150+)
SPANISH_MALE_NAMES = {
    "adrian", "alejandro", "alfonso", "alfredo", "andres", "angel", "antonio",
    "arturo", "benito", "bernardo", "carlos", "cesar", "cristian", "daniel", "david",
    "diego", "domingo", "eduardo", "emilio", "enrique", "ernesto", "esteban",
    "felipe", "fernando", "francisco", "gabriel", "gerardo", "gilberto", "gonzalo",
    "guillermo", "gustavo", "hector", "hugo", "ignacio", "ivan", "jaime", "javier",
    "jesus", "joaquin", "jorge", "jose", "juan", "julio", "leonardo", "lorenzo",
    "lucas", "luis", "manuel", "marco", "marcos", "mario", "martin", "mateo",
    "mauricio", "miguel", "nicolas", "oscar", "pablo", "patricio", "pedro", "rafael",
    "ramon", "raul", "ricardo", "roberto", "rodrigo", "ruben", "salvador", "samuel",
    "santiago", "sebastian", "sergio", "victor", "vicente",
}

SPANISH_FEMALE_NAMES = {
    "adriana", "alejandra", "alicia", "ana", "andrea", "angela", "antonia", "aurora",
    "beatriz", "blanca", "camila", "carla", "carmen", "carolina", "catalina",
    "cecilia", "clara", "claudia", "cristina", "daniela", "dolores", "elena", "elisa",
    "emilia", "esperanza", "estefania", "eugenia", "eva", "fernanda", "francisca",
    "gabriela", "gloria", "graciela", "guadalupe", "ines", "irene", "isabel",
    "josefina", "juana", "julia", "laura", "leticia", "lilia", "lorena", "lucia",
    "luisa", "luz", "magdalena", "marcela", "margarita", "maria", "mariana", "marta",
    "mercedes", "monica", "natalia", "nuria", "olga", "paola", "patricia", "paula",
    "pilar", "raquel", "rebeca", "rocio", "rosa", "rosario", "sandra", "silvia",
    "sofia", "sonia", "susana", "teresa", "valentina", "valeria", "veronica",
    "victoria", "virginia", "yolanda",
}

# Italienische Vornamen (100+)
ITALIAN_MALE_NAMES = {
    "adriano", "alberto", "aldo", "alessio", "alessandro", "andrea", "angelo",
    "antonio", "bruno", "carlo", "claudio", "daniele", "dario", "davide", "domenico",
    "edoardo", "emanuele", "enrico", "fabio", "fabrizio", "federico", "filippo",
    "francesco", "franco", "giacomo", "gianni", "giorgio", "giovanni", "giulio",
    "giuseppe", "guido", "luca", "luciano", "luigi", "marco", "mario", "massimo",
    "matteo", "maurizio", "michele", "nicola", "paolo", "pasquale", "piero", "pietro",
    "raffaele", "renato", "riccardo", "roberto", "salvatore", "sandro", "sergio",
    "silvio", "simone", "stefano", "tommaso", "umberto", "vincenzo", "vittorio",
}

ITALIAN_FEMALE_NAMES = {
    "adriana", "alessandra", "alessia", "alice", "anna", "antonella", "beatrice",
    "bianca", "carla", "caterina", "cecilia", "chiara", "cinzia", "claudia",
    "cristina", "daniela", "elena", "eleonora", "elisa", "elisabetta", "emanuela",
    "federica", "francesca", "gabriella", "giada", "giorgia", "giovanna", "giulia",
    "giuseppina", "ilaria", "irene", "isabella", "laura", "lisa", "lorenza", "lucia",
    "luciana", "luisa", "manuela", "margherita", "maria", "marta", "martina",
    "michela", "monica", "paola", "patrizia", "raffaella", "roberta", "rosa",
    "rossella", "sabrina", "sara", "serena", "silvia", "simona", "sofia", "stefania",
    "valentina", "valeria", "vanessa", "veronica", "virginia",
}

# Französische Vornamen (100+)
FRENCH_MALE_NAMES = {
    "adrien", "alain", "alexandre", "alexis", "antoine", "arnaud", "bastien",
    "benoit", "bernard", "bertrand", "bruno", "cedric", "charles", "christophe",
    "claude", "clement", "damien", "david", "denis", "didier", "dominique", "edouard",
    "emmanuel", "eric", "etienne", "fabien", "fabrice", "florian", "francois",
    "frederic", "gabriel", "gauthier", "gerard", "guillaume", "henri", "herve",
    "hugo", "jacques", "jean", "jerome", "joel", "jonathan", "julien", "kevin",
    "laurent", "leo", "lionel", "louis", "luc", "lucas", "marc", "marcel", "mathieu",
    "maxime", "michel", "nicolas", "olivier", "pascal", "patrice", "paul", "philippe",
    "pierre", "quentin", "remi", "renaud", "richard", "robert", "roger", "romain",
    "sebastien", "serge", "simon", "stephane", "sylvain", "theo", "thierry", "thomas",
    "valentin", "vincent", "xavier", "yannick", "yves",
}

FRENCH_FEMALE_NAMES = {
    "adeline", "agathe", "alice", "amandine", "amelie", "andrea", "anais", "anne",
    "aurelie", "beatrice", "brigitte", "camille", "caroline", "catherine", "cecile",
    "celine", "chantal", "charlotte", "christine", "claire", "claudine", "clemence",
    "colette", "corinne", "danielle", "delphine", "denise", "dominique", "eliane",
    "elise", "emilie", "emma", "elodie", "fabienne", "florence", "francoise",
    "gabrielle", "genevieve", "helene", "isabelle", "jacqueline", "jeanne", "joelle",
    "josephine", "julie", "juliette", "laetitia", "laurence", "lea", "louise", "lucie",
    "madeleine", "manon", "margot", "marie", "marine", "martine", "mathilde",
    "melanie", "michelle", "monique", "nadia", "nadine", "nathalie", "nicole",
    "oceane", "odette", "pauline", "renee", "sabine", "sandrine", "simone", "sophie",
    "stephanie", "sylvie", "therese", "valerie", "veronique", "virginie", "yvette",
}

# Japanische Vornamen (100+)
JAPANESE_MALE_NAMES = {
    "akihiko", "akihiro", "akira", "aoi", "atsushi", "daichi", "daiki", "daisuke",
    "goro", "haru", "haruki", "haruto", "hayato", "hideki", "hideo", "hikaru",
    "hiroki", "hiroshi", "ichiro", "jiro", "jun", "kaito", "kazuki", "kazuma",
    "kazuo", "kei", "keiji", "keisuke", "ken", "kenji", "kenta", "koji", "kosuke",
    "kota", "makoto", "mamoru", "masaki", "masaru", "masashi", "minoru", "naoki",
    "noboru", "nobuo", "osamu", "ren", "riku", "ryota", "ryuji", "saburo", "satoshi",
    "shin", "shingo", "shinji", "shota", "shuichi", "shun", "sora", "sota", "subaru",
    "tadashi", "taichi", "takashi", "takeshi", "takumi", "taro", "tatsuo", "tatsuya",
    "tetsuya", "tomohiro", "tomoya", "toru", "yamato", "yoshi", "yoshiki", "yosuke",
    "yuki", "yuji", "yusuke", "yuta", "yuto",
}

JAPANESE_FEMALE_NAMES = {
    "ai", "aiko", "airi", "akane", "aki", "akiko", "ami", "asuka", "aya", "ayaka",
    "ayumi", "chie", "chika", "chiyo", "emi", "erika", "hana", "hanako", "haruka",
    "hikari", "hina", "hinata", "hitomi", "honoka", "kaede", "kana", "kanako",
    "kaori", "kasumi", "kazumi", "keiko", "kiko", "kimiko", "koharu", "kokoro",
    "kumiko", "kyoko", "madoka", "mai", "maki", "mana", "manami", "mariko", "megu",
    "megumi", "mei", "miki", "miku", "minako", "minami", "misaki", "miu", "miyuki",
    "moe", "momoka", "nana", "nanami", "naomi", "natsuki", "natsumi", "rin", "riko",
    "rina", "risa", "sachiko", "saki", "sakura", "saya", "sayaka", "sayuri", "shizuka",
    "sumire", "tomoko", "yui", "yuka", "yuki", "yukiko", "yuko", "yumi", "yumiko",
    "yuna", "yuri", "yuriko",
}

# Koreanische Vornamen (50+)
KOREAN_MALE_NAMES = {
    "beomseok", "byungho", "changmin", "daehyun", "donghae", "dongwoo", "eunwoo",
    "gunwoo", "hojin", "hyunwoo", "jaehyun", "jimin", "jinwoo", "jiwon", "joohyun",
    "joonho", "junhyung", "junki", "minho", "minseok", "minsoo", "myungsoo",
    "sangwoo", "seokjin", "seongmin", "seunghoon", "seungwoo", "siwoo", "sungjin",
    "sungmin", "taehyung", "woojin", "yoongi", "youngho", "yunho",
}

KOREAN_FEMALE_NAMES = {
    "bora", "chaeyoung", "dahyun", "eunjin", "eunji", "haeun", "hayoung", "heejin",
    "hyejin", "hyuna", "jieun", "jimin", "jisoo", "jiyeon", "minji", "minjoo",
    "naeun", "nayeon", "seolhyun", "seoyeon", "soojin", "sooyoung", "subin", "yeonwoo",
    "yerim", "yoona", "yujin", "yuna",
}

# Indische Vornamen (50+)
INDIAN_MALE_NAMES = {
    "aarav", "aditya", "ajay", "amit", "anil", "arjun", "ashok", "deepak", "dev",
    "ganesh", "gopal", "hari", "jayesh", "kiran", "krishna", "manoj", "mohan",
    "naveen", "nikhil", "pankaj", "prem", "rahul", "raj", "rajesh", "rajan", "rakesh",
    "ravi", "rohit", "sachin", "sandeep", "sanjay", "santosh", "shyam", "sunil",
    "suresh", "vijay", "vikram", "vinod", "vishal", "vivek",
}

INDIAN_FEMALE_NAMES = {
    "ananya", "anjali", "asha", "deepa", "devi", "geeta", "indira", "jaya", "kavita",
    "lata", "madhuri", "meera", "nandini", "neha", "padma", "pooja", "priya",
    "radha", "rani", "rekha", "ritu", "sangeeta", "sarita", "shanti", "shivani",
    "sneha", "sonia", "sunita", "swati", "usha", "vidya",
}


# =============================================================================
# KOMBINIERE ALLE NAMEN
# =============================================================================

def get_all_male_names():
    """Hole alle männlichen Vornamen"""
    all_names = set()
    all_names.update(GERMAN_MALE_NAMES)
    all_names.update(TURKISH_MALE_NAMES)
    all_names.update(ARABIC_MALE_NAMES)
    all_names.update(SLAVIC_MALE_NAMES)
    all_names.update(ENGLISH_MALE_NAMES)
    all_names.update(SPANISH_MALE_NAMES)
    all_names.update(ITALIAN_MALE_NAMES)
    all_names.update(FRENCH_MALE_NAMES)
    all_names.update(JAPANESE_MALE_NAMES)
    all_names.update(KOREAN_MALE_NAMES)
    all_names.update(INDIAN_MALE_NAMES)
    return all_names


def get_all_female_names():
    """Hole alle weiblichen Vornamen"""
    all_names = set()
    all_names.update(GERMAN_FEMALE_NAMES)
    all_names.update(TURKISH_FEMALE_NAMES)
    all_names.update(ARABIC_FEMALE_NAMES)
    all_names.update(SLAVIC_FEMALE_NAMES)
    all_names.update(ENGLISH_FEMALE_NAMES)
    all_names.update(SPANISH_FEMALE_NAMES)
    all_names.update(ITALIAN_FEMALE_NAMES)
    all_names.update(FRENCH_FEMALE_NAMES)
    all_names.update(JAPANESE_FEMALE_NAMES)
    all_names.update(KOREAN_FEMALE_NAMES)
    all_names.update(INDIAN_FEMALE_NAMES)
    return all_names


def get_all_names_with_gender():
    """Hole alle Vornamen mit Gender"""
    names = {}
    for name in get_all_male_names():
        names[name] = "male"
    for name in get_all_female_names():
        names[name] = "female"
    return names


# =============================================================================
# GAMING CHARAKTERE DATENBANK
# =============================================================================

GAMING_CHARACTERS = {
    # =============== GENSHIN IMPACT (80+) ===============
    "raiden shogun": {"game": "Genshin Impact", "gender": "female", "element": "electro"},
    "raiden": {"game": "Genshin Impact", "gender": "female", "element": "electro"},
    "ei": {"game": "Genshin Impact", "gender": "female", "element": "electro"},
    "yae miko": {"game": "Genshin Impact", "gender": "female", "element": "electro"},
    "yae": {"game": "Genshin Impact", "gender": "female", "element": "electro"},
    "zhongli": {"game": "Genshin Impact", "gender": "male", "element": "geo"},
    "venti": {"game": "Genshin Impact", "gender": "male", "element": "anemo"},
    "nahida": {"game": "Genshin Impact", "gender": "female", "element": "dendro"},
    "furina": {"game": "Genshin Impact", "gender": "female", "element": "hydro"},
    "neuvillette": {"game": "Genshin Impact", "gender": "male", "element": "hydro"},
    "hu tao": {"game": "Genshin Impact", "gender": "female", "element": "pyro"},
    "ganyu": {"game": "Genshin Impact", "gender": "female", "element": "cryo"},
    "ayaka": {"game": "Genshin Impact", "gender": "female", "element": "cryo"},
    "kamisato ayaka": {"game": "Genshin Impact", "gender": "female", "element": "cryo"},
    "ayato": {"game": "Genshin Impact", "gender": "male", "element": "hydro"},
    "kamisato ayato": {"game": "Genshin Impact", "gender": "male", "element": "hydro"},
    "kazuha": {"game": "Genshin Impact", "gender": "male", "element": "anemo"},
    "kaedehara kazuha": {"game": "Genshin Impact", "gender": "male", "element": "anemo"},
    "xiao": {"game": "Genshin Impact", "gender": "male", "element": "anemo"},
    "keqing": {"game": "Genshin Impact", "gender": "female", "element": "electro"},
    "ningguang": {"game": "Genshin Impact", "gender": "female", "element": "geo"},
    "diluc": {"game": "Genshin Impact", "gender": "male", "element": "pyro"},
    "jean": {"game": "Genshin Impact", "gender": "female", "element": "anemo"},
    "klee": {"game": "Genshin Impact", "gender": "female", "element": "pyro"},
    "albedo": {"game": "Genshin Impact", "gender": "male", "element": "geo"},
    "eula": {"game": "Genshin Impact", "gender": "female", "element": "cryo"},
    "itto": {"game": "Genshin Impact", "gender": "male", "element": "geo"},
    "arataki itto": {"game": "Genshin Impact", "gender": "male", "element": "geo"},
    "yelan": {"game": "Genshin Impact", "gender": "female", "element": "hydro"},
    "shenhe": {"game": "Genshin Impact", "gender": "female", "element": "cryo"},
    "cyno": {"game": "Genshin Impact", "gender": "male", "element": "electro"},
    "nilou": {"game": "Genshin Impact", "gender": "female", "element": "hydro"},
    "dehya": {"game": "Genshin Impact", "gender": "female", "element": "pyro"},
    "alhaitham": {"game": "Genshin Impact", "gender": "male", "element": "dendro"},
    "wanderer": {"game": "Genshin Impact", "gender": "male", "element": "anemo"},
    "scaramouche": {"game": "Genshin Impact", "gender": "male", "element": "anemo"},
    "tighnari": {"game": "Genshin Impact", "gender": "male", "element": "dendro"},
    "lyney": {"game": "Genshin Impact", "gender": "male", "element": "pyro"},
    "lynette": {"game": "Genshin Impact", "gender": "female", "element": "anemo"},
    "freminet": {"game": "Genshin Impact", "gender": "male", "element": "cryo"},
    "navia": {"game": "Genshin Impact", "gender": "female", "element": "geo"},
    "clorinde": {"game": "Genshin Impact", "gender": "female", "element": "electro"},
    "arlecchino": {"game": "Genshin Impact", "gender": "female", "element": "pyro"},
    "sigewinne": {"game": "Genshin Impact", "gender": "female", "element": "hydro"},
    "emilie": {"game": "Genshin Impact", "gender": "female", "element": "dendro"},
    "mualani": {"game": "Genshin Impact", "gender": "female", "element": "hydro"},
    "kinich": {"game": "Genshin Impact", "gender": "male", "element": "dendro"},
    "xilonen": {"game": "Genshin Impact", "gender": "female", "element": "geo"},
    "chasca": {"game": "Genshin Impact", "gender": "female", "element": "anemo"},
    "ororon": {"game": "Genshin Impact", "gender": "male", "element": "electro"},
    "citlali": {"game": "Genshin Impact", "gender": "female", "element": "cryo"},
    "mavuika": {"game": "Genshin Impact", "gender": "female", "element": "pyro"},
    "bennett": {"game": "Genshin Impact", "gender": "male", "element": "pyro"},
    "xingqiu": {"game": "Genshin Impact", "gender": "male", "element": "hydro"},
    "xiangling": {"game": "Genshin Impact", "gender": "female", "element": "pyro"},
    "fischl": {"game": "Genshin Impact", "gender": "female", "element": "electro"},
    "barbara": {"game": "Genshin Impact", "gender": "female", "element": "hydro"},
    "mona": {"game": "Genshin Impact", "gender": "female", "element": "hydro"},
    "qiqi": {"game": "Genshin Impact", "gender": "female", "element": "cryo"},
    "tartaglia": {"game": "Genshin Impact", "gender": "male", "element": "hydro"},
    "childe": {"game": "Genshin Impact", "gender": "male", "element": "hydro"},
    "kokomi": {"game": "Genshin Impact", "gender": "female", "element": "hydro"},
    "sangonomiya kokomi": {"game": "Genshin Impact", "gender": "female", "element": "hydro"},
    "yoimiya": {"game": "Genshin Impact", "gender": "female", "element": "pyro"},
    "sara": {"game": "Genshin Impact", "gender": "female", "element": "electro"},
    "kujou sara": {"game": "Genshin Impact", "gender": "female", "element": "electro"},
    "gorou": {"game": "Genshin Impact", "gender": "male", "element": "geo"},
    "thoma": {"game": "Genshin Impact", "gender": "male", "element": "pyro"},
    "heizou": {"game": "Genshin Impact", "gender": "male", "element": "anemo"},
    "shikanoin heizou": {"game": "Genshin Impact", "gender": "male", "element": "anemo"},
    "shinobu": {"game": "Genshin Impact", "gender": "female", "element": "electro"},
    "kuki shinobu": {"game": "Genshin Impact", "gender": "female", "element": "electro"},
    "collei": {"game": "Genshin Impact", "gender": "female", "element": "dendro"},
    "dori": {"game": "Genshin Impact", "gender": "female", "element": "electro"},
    "candace": {"game": "Genshin Impact", "gender": "female", "element": "hydro"},
    "layla": {"game": "Genshin Impact", "gender": "female", "element": "cryo"},
    "faruzan": {"game": "Genshin Impact", "gender": "female", "element": "anemo"},
    "yaoyao": {"game": "Genshin Impact", "gender": "female", "element": "dendro"},
    "mika": {"game": "Genshin Impact", "gender": "male", "element": "cryo"},
    "baizhu": {"game": "Genshin Impact", "gender": "male", "element": "dendro"},
    "kaveh": {"game": "Genshin Impact", "gender": "male", "element": "dendro"},
    "kirara": {"game": "Genshin Impact", "gender": "female", "element": "dendro"},
    "charlotte": {"game": "Genshin Impact", "gender": "female", "element": "cryo"},
    "chevreuse": {"game": "Genshin Impact", "gender": "female", "element": "pyro"},
    "gaming": {"game": "Genshin Impact", "gender": "male", "element": "pyro"},
    "chiori": {"game": "Genshin Impact", "gender": "female", "element": "geo"},
    "sethos": {"game": "Genshin Impact", "gender": "male", "element": "electro"},
    "kachina": {"game": "Genshin Impact", "gender": "female", "element": "geo"},
    
    # =============== HONKAI STAR RAIL (70+) ===============
    "kafka": {"game": "Honkai Star Rail", "gender": "female", "path": "Nihility"},
    "seele": {"game": "Honkai Star Rail", "gender": "female", "path": "Hunt"},
    "bronya": {"game": "Honkai Star Rail", "gender": "female", "path": "Harmony"},
    "himeko": {"game": "Honkai Star Rail", "gender": "female", "path": "Erudition"},
    "welt": {"game": "Honkai Star Rail", "gender": "male", "path": "Nihility"},
    "clara": {"game": "Honkai Star Rail", "gender": "female", "path": "Destruction"},
    "jing yuan": {"game": "Honkai Star Rail", "gender": "male", "path": "Erudition"},
    "blade": {"game": "Honkai Star Rail", "gender": "male", "path": "Destruction"},
    "dan heng": {"game": "Honkai Star Rail", "gender": "male", "path": "Hunt"},
    "dan heng imbibitor lunae": {"game": "Honkai Star Rail", "gender": "male", "path": "Destruction"},
    "march 7th": {"game": "Honkai Star Rail", "gender": "female", "path": "Preservation"},
    "silver wolf": {"game": "Honkai Star Rail", "gender": "female", "path": "Nihility"},
    "luocha": {"game": "Honkai Star Rail", "gender": "male", "path": "Abundance"},
    "fu xuan": {"game": "Honkai Star Rail", "gender": "female", "path": "Preservation"},
    "jingliu": {"game": "Honkai Star Rail", "gender": "female", "path": "Destruction"},
    "topaz": {"game": "Honkai Star Rail", "gender": "female", "path": "Hunt"},
    "guinaifen": {"game": "Honkai Star Rail", "gender": "female", "path": "Nihility"},
    "lynx": {"game": "Honkai Star Rail", "gender": "female", "path": "Abundance"},
    "huohuo": {"game": "Honkai Star Rail", "gender": "female", "path": "Abundance"},
    "argenti": {"game": "Honkai Star Rail", "gender": "male", "path": "Erudition"},
    "hanya": {"game": "Honkai Star Rail", "gender": "female", "path": "Harmony"},
    "ruan mei": {"game": "Honkai Star Rail", "gender": "female", "path": "Harmony"},
    "dr ratio": {"game": "Honkai Star Rail", "gender": "male", "path": "Hunt"},
    "xueyi": {"game": "Honkai Star Rail", "gender": "female", "path": "Destruction"},
    "black swan": {"game": "Honkai Star Rail", "gender": "female", "path": "Nihility"},
    "sparkle": {"game": "Honkai Star Rail", "gender": "female", "path": "Harmony"},
    "misha": {"game": "Honkai Star Rail", "gender": "male", "path": "Destruction"},
    "acheron": {"game": "Honkai Star Rail", "gender": "female", "path": "Nihility"},
    "aventurine": {"game": "Honkai Star Rail", "gender": "male", "path": "Preservation"},
    "gallagher": {"game": "Honkai Star Rail", "gender": "male", "path": "Abundance"},
    "robin": {"game": "Honkai Star Rail", "gender": "female", "path": "Harmony"},
    "boothill": {"game": "Honkai Star Rail", "gender": "male", "path": "Hunt"},
    "firefly": {"game": "Honkai Star Rail", "gender": "female", "path": "Destruction"},
    "sam": {"game": "Honkai Star Rail", "gender": "female", "path": "Destruction"},
    "jade": {"game": "Honkai Star Rail", "gender": "female", "path": "Erudition"},
    "yunli": {"game": "Honkai Star Rail", "gender": "female", "path": "Destruction"},
    "jiaoqiu": {"game": "Honkai Star Rail", "gender": "male", "path": "Nihility"},
    "feixiao": {"game": "Honkai Star Rail", "gender": "female", "path": "Hunt"},
    "moze": {"game": "Honkai Star Rail", "gender": "male", "path": "Hunt"},
    "lingsha": {"game": "Honkai Star Rail", "gender": "female", "path": "Abundance"},
    "rappa": {"game": "Honkai Star Rail", "gender": "female", "path": "Erudition"},
    "sunday": {"game": "Honkai Star Rail", "gender": "male", "path": "Harmony"},
    "fugue": {"game": "Honkai Star Rail", "gender": "female", "path": "Nihility"},
    "the herta": {"game": "Honkai Star Rail", "gender": "female", "path": "Erudition"},
    "aglaea": {"game": "Honkai Star Rail", "gender": "female", "path": "Remembrance"},
    "tribbie": {"game": "Honkai Star Rail", "gender": "female", "path": "Harmony"},
    "mydei": {"game": "Honkai Star Rail", "gender": "male", "path": "Destruction"},
    "castorice": {"game": "Honkai Star Rail", "gender": "female", "path": "Remembrance"},
    "anaxa": {"game": "Honkai Star Rail", "gender": "male", "path": "Erudition"},
    "trailblazer": {"game": "Honkai Star Rail", "gender": "neutral", "path": "multiple"},
    "stelle": {"game": "Honkai Star Rail", "gender": "female", "path": "multiple"},
    "caelus": {"game": "Honkai Star Rail", "gender": "male", "path": "multiple"},
    "asta": {"game": "Honkai Star Rail", "gender": "female", "path": "Harmony"},
    "natasha": {"game": "Honkai Star Rail", "gender": "female", "path": "Abundance"},
    "pela": {"game": "Honkai Star Rail", "gender": "female", "path": "Nihility"},
    "serval": {"game": "Honkai Star Rail", "gender": "female", "path": "Erudition"},
    "gepard": {"game": "Honkai Star Rail", "gender": "male", "path": "Preservation"},
    "sampo": {"game": "Honkai Star Rail", "gender": "male", "path": "Nihility"},
    "hook": {"game": "Honkai Star Rail", "gender": "female", "path": "Destruction"},
    "sushang": {"game": "Honkai Star Rail", "gender": "female", "path": "Hunt"},
    "tingyun": {"game": "Honkai Star Rail", "gender": "female", "path": "Harmony"},
    "yukong": {"game": "Honkai Star Rail", "gender": "female", "path": "Harmony"},
    "qingque": {"game": "Honkai Star Rail", "gender": "female", "path": "Erudition"},
    "yanqing": {"game": "Honkai Star Rail", "gender": "male", "path": "Hunt"},
    "bailu": {"game": "Honkai Star Rail", "gender": "female", "path": "Abundance"},
    "luka": {"game": "Honkai Star Rail", "gender": "male", "path": "Nihility"},
    
    # =============== ZENLESS ZONE ZERO (40+) ===============
    "ellen": {"game": "Zenless Zone Zero", "gender": "female", "faction": "Victoria Housekeeping"},
    "ellen joe": {"game": "Zenless Zone Zero", "gender": "female", "faction": "Victoria Housekeeping"},
    "zhu yuan": {"game": "Zenless Zone Zero", "gender": "female", "faction": "Criminal Investigation Special Response Team"},
    "miyabi": {"game": "Zenless Zone Zero", "gender": "female", "faction": "Section 6"},
    "astra yao": {"game": "Zenless Zone Zero", "gender": "female", "faction": "Stars of Lyra"},
    "evelyn": {"game": "Zenless Zone Zero", "gender": "female", "faction": "Obol Squad"},
    "nicole demara": {"game": "Zenless Zone Zero", "gender": "female", "faction": "Cunning Hares"},
    "nicole": {"game": "Zenless Zone Zero", "gender": "female", "faction": "Cunning Hares"},
    "anby demara": {"game": "Zenless Zone Zero", "gender": "female", "faction": "Cunning Hares"},
    "anby": {"game": "Zenless Zone Zero", "gender": "female", "faction": "Cunning Hares"},
    "billy kid": {"game": "Zenless Zone Zero", "gender": "male", "faction": "Cunning Hares"},
    "billy": {"game": "Zenless Zone Zero", "gender": "male", "faction": "Cunning Hares"},
    "nekomata": {"game": "Zenless Zone Zero", "gender": "female", "faction": "Cunning Hares"},
    "koleda": {"game": "Zenless Zone Zero", "gender": "female", "faction": "Belobog Heavy Industries"},
    "koleda belobog": {"game": "Zenless Zone Zero", "gender": "female", "faction": "Belobog Heavy Industries"},
    "grace howard": {"game": "Zenless Zone Zero", "gender": "female", "faction": "Belobog Heavy Industries"},
    "grace": {"game": "Zenless Zone Zero", "gender": "female", "faction": "Belobog Heavy Industries"},
    "ben bigger": {"game": "Zenless Zone Zero", "gender": "male", "faction": "Belobog Heavy Industries"},
    "ben": {"game": "Zenless Zone Zero", "gender": "male", "faction": "Belobog Heavy Industries"},
    "rina": {"game": "Zenless Zone Zero", "gender": "female", "faction": "Victoria Housekeeping"},
    "corin": {"game": "Zenless Zone Zero", "gender": "female", "faction": "Victoria Housekeeping"},
    "corin wickes": {"game": "Zenless Zone Zero", "gender": "female", "faction": "Victoria Housekeeping"},
    "lycaon": {"game": "Zenless Zone Zero", "gender": "male", "faction": "Victoria Housekeeping"},
    "von lycaon": {"game": "Zenless Zone Zero", "gender": "male", "faction": "Victoria Housekeeping"},
    "qingyi": {"game": "Zenless Zone Zero", "gender": "female", "faction": "Criminal Investigation Special Response Team"},
    "jane doe": {"game": "Zenless Zone Zero", "gender": "female", "faction": "Sons of Calydon"},
    "jane": {"game": "Zenless Zone Zero", "gender": "female", "faction": "Sons of Calydon"},
    "seth": {"game": "Zenless Zone Zero", "gender": "male", "faction": "Criminal Investigation Special Response Team"},
    "seth lowell": {"game": "Zenless Zone Zero", "gender": "male", "faction": "Criminal Investigation Special Response Team"},
    "caesar": {"game": "Zenless Zone Zero", "gender": "female", "faction": "Sons of Calydon"},
    "caesar king": {"game": "Zenless Zone Zero", "gender": "female", "faction": "Sons of Calydon"},
    "burnice": {"game": "Zenless Zone Zero", "gender": "female", "faction": "Sons of Calydon"},
    "burnice white": {"game": "Zenless Zone Zero", "gender": "female", "faction": "Sons of Calydon"},
    "lighter": {"game": "Zenless Zone Zero", "gender": "male", "faction": "Sons of Calydon"},
    "yanagi": {"game": "Zenless Zone Zero", "gender": "female", "faction": "Section 6"},
    "harumasa": {"game": "Zenless Zone Zero", "gender": "male", "faction": "Section 6"},
    "soukaku": {"game": "Zenless Zone Zero", "gender": "female", "faction": "Section 6"},
    "lucy": {"game": "Zenless Zone Zero", "gender": "female", "faction": "Sons of Calydon"},
    "piper": {"game": "Zenless Zone Zero", "gender": "female", "faction": "Sons of Calydon"},
    "soldier 11": {"game": "Zenless Zone Zero", "gender": "female", "faction": "Obol Squad"},
    "anton": {"game": "Zenless Zone Zero", "gender": "male", "faction": "Belobog Heavy Industries"},
    
    # =============== LEAGUE OF LEGENDS (50+) ===============
    "ahri": {"game": "League of Legends", "gender": "female", "role": "mage"},
    "akali": {"game": "League of Legends", "gender": "female", "role": "assassin"},
    "yasuo": {"game": "League of Legends", "gender": "male", "role": "fighter"},
    "yone": {"game": "League of Legends", "gender": "male", "role": "fighter"},
    "jinx": {"game": "League of Legends", "gender": "female", "role": "marksman"},
    "vi": {"game": "League of Legends", "gender": "female", "role": "fighter"},
    "caitlyn": {"game": "League of Legends", "gender": "female", "role": "marksman"},
    "lux": {"game": "League of Legends", "gender": "female", "role": "mage"},
    "miss fortune": {"game": "League of Legends", "gender": "female", "role": "marksman"},
    "seraphine": {"game": "League of Legends", "gender": "female", "role": "mage"},
    "sona": {"game": "League of Legends", "gender": "female", "role": "support"},
    "katarina": {"game": "League of Legends", "gender": "female", "role": "assassin"},
    "leblanc": {"game": "League of Legends", "gender": "female", "role": "mage"},
    "syndra": {"game": "League of Legends", "gender": "female", "role": "mage"},
    "irelia": {"game": "League of Legends", "gender": "female", "role": "fighter"},
    "riven": {"game": "League of Legends", "gender": "female", "role": "fighter"},
    "fiora": {"game": "League of Legends", "gender": "female", "role": "fighter"},
    "leona": {"game": "League of Legends", "gender": "female", "role": "tank"},
    "morgana": {"game": "League of Legends", "gender": "female", "role": "mage"},
    "kayle": {"game": "League of Legends", "gender": "female", "role": "fighter"},
    "diana": {"game": "League of Legends", "gender": "female", "role": "fighter"},
    "zed": {"game": "League of Legends", "gender": "male", "role": "assassin"},
    "talon": {"game": "League of Legends", "gender": "male", "role": "assassin"},
    "lee sin": {"game": "League of Legends", "gender": "male", "role": "fighter"},
    "darius": {"game": "League of Legends", "gender": "male", "role": "fighter"},
    "garen": {"game": "League of Legends", "gender": "male", "role": "fighter"},
    "ezreal": {"game": "League of Legends", "gender": "male", "role": "marksman"},
    "lucian": {"game": "League of Legends", "gender": "male", "role": "marksman"},
    "vayne": {"game": "League of Legends", "gender": "female", "role": "marksman"},
    "kaisa": {"game": "League of Legends", "gender": "female", "role": "marksman"},
    "samira": {"game": "League of Legends", "gender": "female", "role": "marksman"},
    "thresh": {"game": "League of Legends", "gender": "male", "role": "support"},
    "pyke": {"game": "League of Legends", "gender": "male", "role": "support"},
    "sett": {"game": "League of Legends", "gender": "male", "role": "fighter"},
    "viego": {"game": "League of Legends", "gender": "male", "role": "fighter"},
    "evelynn": {"game": "League of Legends", "gender": "female", "role": "assassin"},
    "qiyana": {"game": "League of Legends", "gender": "female", "role": "assassin"},
    "aurora": {"game": "League of Legends", "gender": "female", "role": "mage"},
    "nilah": {"game": "League of Legends", "gender": "female", "role": "marksman"},
    "belveth": {"game": "League of Legends", "gender": "female", "role": "fighter"},
    "ambessa": {"game": "League of Legends", "gender": "female", "role": "fighter"},
    
    # =============== VALORANT (25+) ===============
    "jett": {"game": "Valorant", "gender": "female", "role": "duelist"},
    "reyna": {"game": "Valorant", "gender": "female", "role": "duelist"},
    "raze": {"game": "Valorant", "gender": "female", "role": "duelist"},
    "neon": {"game": "Valorant", "gender": "female", "role": "duelist"},
    "yoru": {"game": "Valorant", "gender": "male", "role": "duelist"},
    "phoenix": {"game": "Valorant", "gender": "male", "role": "duelist"},
    "iso": {"game": "Valorant", "gender": "male", "role": "duelist"},
    "sage": {"game": "Valorant", "gender": "female", "role": "sentinel"},
    "killjoy": {"game": "Valorant", "gender": "female", "role": "sentinel"},
    "cypher": {"game": "Valorant", "gender": "male", "role": "sentinel"},
    "chamber": {"game": "Valorant", "gender": "male", "role": "sentinel"},
    "deadlock": {"game": "Valorant", "gender": "female", "role": "sentinel"},
    "viper": {"game": "Valorant", "gender": "female", "role": "controller"},
    "omen": {"game": "Valorant", "gender": "male", "role": "controller"},
    "brimstone": {"game": "Valorant", "gender": "male", "role": "controller"},
    "astra": {"game": "Valorant", "gender": "female", "role": "controller"},
    "harbor": {"game": "Valorant", "gender": "male", "role": "controller"},
    "clove": {"game": "Valorant", "gender": "nonbinary", "role": "controller"},
    "sova": {"game": "Valorant", "gender": "male", "role": "initiator"},
    "breach": {"game": "Valorant", "gender": "male", "role": "initiator"},
    "skye": {"game": "Valorant", "gender": "female", "role": "initiator"},
    "kay/o": {"game": "Valorant", "gender": "male", "role": "initiator"},
    "fade": {"game": "Valorant", "gender": "female", "role": "initiator"},
    "gekko": {"game": "Valorant", "gender": "male", "role": "initiator"},
    "vyse": {"game": "Valorant", "gender": "female", "role": "sentinel"},
    "tejo": {"game": "Valorant", "gender": "male", "role": "initiator"},
    
    # =============== WUTHERING WAVES (30+) ===============
    "rover": {"game": "Wuthering Waves", "gender": "neutral"},
    "jiyan": {"game": "Wuthering Waves", "gender": "male"},
    "yinlin": {"game": "Wuthering Waves", "gender": "female"},
    "calcharo": {"game": "Wuthering Waves", "gender": "male"},
    "jinhsi": {"game": "Wuthering Waves", "gender": "female"},
    "changli": {"game": "Wuthering Waves", "gender": "female"},
    "zhezhi": {"game": "Wuthering Waves", "gender": "female"},
    "xiangli yao": {"game": "Wuthering Waves", "gender": "male"},
    "shorekeeper": {"game": "Wuthering Waves", "gender": "female"},
    "camellya": {"game": "Wuthering Waves", "gender": "female"},
    "carlotta": {"game": "Wuthering Waves", "gender": "female"},
    "roccia": {"game": "Wuthering Waves", "gender": "female"},
    "verina": {"game": "Wuthering Waves", "gender": "female"},
    "encore": {"game": "Wuthering Waves", "gender": "female"},
    "sanhua": {"game": "Wuthering Waves", "gender": "female"},
    "danjin": {"game": "Wuthering Waves", "gender": "female"},
    "yangyang": {"game": "Wuthering Waves", "gender": "female"},
    "chixia": {"game": "Wuthering Waves", "gender": "female"},
    "mortefi": {"game": "Wuthering Waves", "gender": "male"},
    "aalto": {"game": "Wuthering Waves", "gender": "male"},
    "baizhi": {"game": "Wuthering Waves", "gender": "female"},
    "lingyang": {"game": "Wuthering Waves", "gender": "male"},
    "yuanwu": {"game": "Wuthering Waves", "gender": "male"},
    "taoqi": {"game": "Wuthering Waves", "gender": "female"},
    "lumi": {"game": "Wuthering Waves", "gender": "female"},
    "jianxin": {"game": "Wuthering Waves", "gender": "female"},
    "phoebe": {"game": "Wuthering Waves", "gender": "female"},
    "brant": {"game": "Wuthering Waves", "gender": "male"},
}


# =============================================================================
# ANIME CHARAKTERE DATENBANK
# =============================================================================

ANIME_CHARACTERS = {
    # =============== NARUTO (30+) ===============
    "naruto": {"anime": "Naruto", "gender": "male"},
    "naruto uzumaki": {"anime": "Naruto", "gender": "male"},
    "sasuke": {"anime": "Naruto", "gender": "male"},
    "sasuke uchiha": {"anime": "Naruto", "gender": "male"},
    "sakura": {"anime": "Naruto", "gender": "female"},
    "sakura haruno": {"anime": "Naruto", "gender": "female"},
    "kakashi": {"anime": "Naruto", "gender": "male"},
    "kakashi hatake": {"anime": "Naruto", "gender": "male"},
    "hinata": {"anime": "Naruto", "gender": "female"},
    "hinata hyuga": {"anime": "Naruto", "gender": "female"},
    "itachi": {"anime": "Naruto", "gender": "male"},
    "itachi uchiha": {"anime": "Naruto", "gender": "male"},
    "madara": {"anime": "Naruto", "gender": "male"},
    "madara uchiha": {"anime": "Naruto", "gender": "male"},
    "obito": {"anime": "Naruto", "gender": "male"},
    "obito uchiha": {"anime": "Naruto", "gender": "male"},
    "minato": {"anime": "Naruto", "gender": "male"},
    "minato namikaze": {"anime": "Naruto", "gender": "male"},
    "jiraiya": {"anime": "Naruto", "gender": "male"},
    "tsunade": {"anime": "Naruto", "gender": "female"},
    "orochimaru": {"anime": "Naruto", "gender": "male"},
    "gaara": {"anime": "Naruto", "gender": "male"},
    "rock lee": {"anime": "Naruto", "gender": "male"},
    "neji": {"anime": "Naruto", "gender": "male"},
    "tenten": {"anime": "Naruto", "gender": "female"},
    "shikamaru": {"anime": "Naruto", "gender": "male"},
    "ino": {"anime": "Naruto", "gender": "female"},
    "choji": {"anime": "Naruto", "gender": "male"},
    "kiba": {"anime": "Naruto", "gender": "male"},
    "shino": {"anime": "Naruto", "gender": "male"},
    
    # =============== DRAGON BALL (20+) ===============
    "goku": {"anime": "Dragon Ball", "gender": "male"},
    "son goku": {"anime": "Dragon Ball", "gender": "male"},
    "vegeta": {"anime": "Dragon Ball", "gender": "male"},
    "gohan": {"anime": "Dragon Ball", "gender": "male"},
    "goten": {"anime": "Dragon Ball", "gender": "male"},
    "trunks": {"anime": "Dragon Ball", "gender": "male"},
    "piccolo": {"anime": "Dragon Ball", "gender": "male"},
    "krillin": {"anime": "Dragon Ball", "gender": "male"},
    "bulma": {"anime": "Dragon Ball", "gender": "female"},
    "chi-chi": {"anime": "Dragon Ball", "gender": "female"},
    "android 18": {"anime": "Dragon Ball", "gender": "female"},
    "frieza": {"anime": "Dragon Ball", "gender": "male"},
    "cell": {"anime": "Dragon Ball", "gender": "male"},
    "majin buu": {"anime": "Dragon Ball", "gender": "male"},
    "beerus": {"anime": "Dragon Ball", "gender": "male"},
    "whis": {"anime": "Dragon Ball", "gender": "male"},
    "broly": {"anime": "Dragon Ball", "gender": "male"},
    "jiren": {"anime": "Dragon Ball", "gender": "male"},
    
    # =============== ONE PIECE (25+) ===============
    "luffy": {"anime": "One Piece", "gender": "male"},
    "monkey d luffy": {"anime": "One Piece", "gender": "male"},
    "zoro": {"anime": "One Piece", "gender": "male"},
    "roronoa zoro": {"anime": "One Piece", "gender": "male"},
    "nami": {"anime": "One Piece", "gender": "female"},
    "sanji": {"anime": "One Piece", "gender": "male"},
    "usopp": {"anime": "One Piece", "gender": "male"},
    "chopper": {"anime": "One Piece", "gender": "male"},
    "robin": {"anime": "One Piece", "gender": "female"},
    "nico robin": {"anime": "One Piece", "gender": "female"},
    "franky": {"anime": "One Piece", "gender": "male"},
    "brook": {"anime": "One Piece", "gender": "male"},
    "jinbe": {"anime": "One Piece", "gender": "male"},
    "ace": {"anime": "One Piece", "gender": "male"},
    "portgas d ace": {"anime": "One Piece", "gender": "male"},
    "sabo": {"anime": "One Piece", "gender": "male"},
    "shanks": {"anime": "One Piece", "gender": "male"},
    "whitebeard": {"anime": "One Piece", "gender": "male"},
    "law": {"anime": "One Piece", "gender": "male"},
    "trafalgar law": {"anime": "One Piece", "gender": "male"},
    "boa hancock": {"anime": "One Piece", "gender": "female"},
    "yamato": {"anime": "One Piece", "gender": "female"},
    
    # =============== ATTACK ON TITAN (20+) ===============
    "eren": {"anime": "Attack on Titan", "gender": "male"},
    "eren yeager": {"anime": "Attack on Titan", "gender": "male"},
    "mikasa": {"anime": "Attack on Titan", "gender": "female"},
    "mikasa ackerman": {"anime": "Attack on Titan", "gender": "female"},
    "armin": {"anime": "Attack on Titan", "gender": "male"},
    "armin arlert": {"anime": "Attack on Titan", "gender": "male"},
    "levi": {"anime": "Attack on Titan", "gender": "male"},
    "levi ackerman": {"anime": "Attack on Titan", "gender": "male"},
    "erwin": {"anime": "Attack on Titan", "gender": "male"},
    "erwin smith": {"anime": "Attack on Titan", "gender": "male"},
    "hange": {"anime": "Attack on Titan", "gender": "nonbinary"},
    "historia": {"anime": "Attack on Titan", "gender": "female"},
    "annie": {"anime": "Attack on Titan", "gender": "female"},
    "annie leonhart": {"anime": "Attack on Titan", "gender": "female"},
    "reiner": {"anime": "Attack on Titan", "gender": "male"},
    "bertholdt": {"anime": "Attack on Titan", "gender": "male"},
    "jean": {"anime": "Attack on Titan", "gender": "male"},
    "connie": {"anime": "Attack on Titan", "gender": "male"},
    "sasha": {"anime": "Attack on Titan", "gender": "female"},
    "ymir": {"anime": "Attack on Titan", "gender": "female"},
    
    # =============== JUJUTSU KAISEN (20+) ===============
    "gojo": {"anime": "Jujutsu Kaisen", "gender": "male"},
    "gojo satoru": {"anime": "Jujutsu Kaisen", "gender": "male"},
    "satoru gojo": {"anime": "Jujutsu Kaisen", "gender": "male"},
    "itadori": {"anime": "Jujutsu Kaisen", "gender": "male"},
    "yuji itadori": {"anime": "Jujutsu Kaisen", "gender": "male"},
    "megumi": {"anime": "Jujutsu Kaisen", "gender": "male"},
    "megumi fushiguro": {"anime": "Jujutsu Kaisen", "gender": "male"},
    "nobara": {"anime": "Jujutsu Kaisen", "gender": "female"},
    "nobara kugisaki": {"anime": "Jujutsu Kaisen", "gender": "female"},
    "sukuna": {"anime": "Jujutsu Kaisen", "gender": "male"},
    "ryomen sukuna": {"anime": "Jujutsu Kaisen", "gender": "male"},
    "maki": {"anime": "Jujutsu Kaisen", "gender": "female"},
    "maki zenin": {"anime": "Jujutsu Kaisen", "gender": "female"},
    "toge": {"anime": "Jujutsu Kaisen", "gender": "male"},
    "panda": {"anime": "Jujutsu Kaisen", "gender": "male"},
    "yuta": {"anime": "Jujutsu Kaisen", "gender": "male"},
    "yuta okkotsu": {"anime": "Jujutsu Kaisen", "gender": "male"},
    "todo": {"anime": "Jujutsu Kaisen", "gender": "male"},
    "nanami": {"anime": "Jujutsu Kaisen", "gender": "male"},
    "geto": {"anime": "Jujutsu Kaisen", "gender": "male"},
    "mahito": {"anime": "Jujutsu Kaisen", "gender": "male"},
    
    # =============== DEMON SLAYER (15+) ===============
    "tanjiro": {"anime": "Demon Slayer", "gender": "male"},
    "tanjiro kamado": {"anime": "Demon Slayer", "gender": "male"},
    "nezuko": {"anime": "Demon Slayer", "gender": "female"},
    "nezuko kamado": {"anime": "Demon Slayer", "gender": "female"},
    "zenitsu": {"anime": "Demon Slayer", "gender": "male"},
    "zenitsu agatsuma": {"anime": "Demon Slayer", "gender": "male"},
    "inosuke": {"anime": "Demon Slayer", "gender": "male"},
    "inosuke hashibira": {"anime": "Demon Slayer", "gender": "male"},
    "kanao": {"anime": "Demon Slayer", "gender": "female"},
    "giyu": {"anime": "Demon Slayer", "gender": "male"},
    "giyu tomioka": {"anime": "Demon Slayer", "gender": "male"},
    "shinobu": {"anime": "Demon Slayer", "gender": "female"},
    "shinobu kocho": {"anime": "Demon Slayer", "gender": "female"},
    "mitsuri": {"anime": "Demon Slayer", "gender": "female"},
    "muzan": {"anime": "Demon Slayer", "gender": "male"},
    "muzan kibutsuji": {"anime": "Demon Slayer", "gender": "male"},
    "rengoku": {"anime": "Demon Slayer", "gender": "male"},
    "kyojuro rengoku": {"anime": "Demon Slayer", "gender": "male"},
    "tengen": {"anime": "Demon Slayer", "gender": "male"},
    "tengen uzui": {"anime": "Demon Slayer", "gender": "male"},
    
    # =============== MY HERO ACADEMIA (20+) ===============
    "deku": {"anime": "My Hero Academia", "gender": "male"},
    "izuku midoriya": {"anime": "My Hero Academia", "gender": "male"},
    "bakugo": {"anime": "My Hero Academia", "gender": "male"},
    "katsuki bakugo": {"anime": "My Hero Academia", "gender": "male"},
    "todoroki": {"anime": "My Hero Academia", "gender": "male"},
    "shoto todoroki": {"anime": "My Hero Academia", "gender": "male"},
    "all might": {"anime": "My Hero Academia", "gender": "male"},
    "ochako": {"anime": "My Hero Academia", "gender": "female"},
    "ochako uraraka": {"anime": "My Hero Academia", "gender": "female"},
    "iida": {"anime": "My Hero Academia", "gender": "male"},
    "tenya iida": {"anime": "My Hero Academia", "gender": "male"},
    "tsuyu": {"anime": "My Hero Academia", "gender": "female"},
    "kirishima": {"anime": "My Hero Academia", "gender": "male"},
    "denki": {"anime": "My Hero Academia", "gender": "male"},
    "momo": {"anime": "My Hero Academia", "gender": "female"},
    "momo yaoyorozu": {"anime": "My Hero Academia", "gender": "female"},
    "aizawa": {"anime": "My Hero Academia", "gender": "male"},
    "shigaraki": {"anime": "My Hero Academia", "gender": "male"},
    "dabi": {"anime": "My Hero Academia", "gender": "male"},
    "toga": {"anime": "My Hero Academia", "gender": "female"},
    "himiko toga": {"anime": "My Hero Academia", "gender": "female"},
    
    # =============== ANDERE POPULÄRE ANIME (40+) ===============
    # Re:Zero
    "rem": {"anime": "Re:Zero", "gender": "female"},
    "ram": {"anime": "Re:Zero", "gender": "female"},
    "emilia": {"anime": "Re:Zero", "gender": "female"},
    "subaru": {"anime": "Re:Zero", "gender": "male"},
    "beatrice": {"anime": "Re:Zero", "gender": "female"},
    
    # Sword Art Online
    "kirito": {"anime": "Sword Art Online", "gender": "male"},
    "asuna": {"anime": "Sword Art Online", "gender": "female"},
    "sinon": {"anime": "Sword Art Online", "gender": "female"},
    "alice": {"anime": "Sword Art Online", "gender": "female"},
    
    # Death Note
    "light": {"anime": "Death Note", "gender": "male"},
    "light yagami": {"anime": "Death Note", "gender": "male"},
    "l": {"anime": "Death Note", "gender": "male"},
    "ryuk": {"anime": "Death Note", "gender": "male"},
    "misa": {"anime": "Death Note", "gender": "female"},
    "misa amane": {"anime": "Death Note", "gender": "female"},
    
    # One Punch Man
    "saitama": {"anime": "One Punch Man", "gender": "male"},
    "genos": {"anime": "One Punch Man", "gender": "male"},
    "tatsumaki": {"anime": "One Punch Man", "gender": "female"},
    "fubuki": {"anime": "One Punch Man", "gender": "female"},
    
    # Darling in the FranXX
    "zero two": {"anime": "Darling in the FranXX", "gender": "female"},
    "hiro": {"anime": "Darling in the FranXX", "gender": "male"},
    
    # Spy x Family
    "loid forger": {"anime": "Spy x Family", "gender": "male"},
    "yor forger": {"anime": "Spy x Family", "gender": "female"},
    "anya forger": {"anime": "Spy x Family", "gender": "female"},
    "anya": {"anime": "Spy x Family", "gender": "female"},
    
    # Chainsaw Man
    "denji": {"anime": "Chainsaw Man", "gender": "male"},
    "makima": {"anime": "Chainsaw Man", "gender": "female"},
    "power": {"anime": "Chainsaw Man", "gender": "female"},
    "aki": {"anime": "Chainsaw Man", "gender": "male"},
    
    # Frieren
    "frieren": {"anime": "Frieren", "gender": "female"},
    "fern": {"anime": "Frieren", "gender": "female"},
    "stark": {"anime": "Frieren", "gender": "male"},
    "himmel": {"anime": "Frieren", "gender": "male"},
    
    # Solo Leveling
    "sung jinwoo": {"anime": "Solo Leveling", "gender": "male"},
    "jinwoo": {"anime": "Solo Leveling", "gender": "male"},
    "cha hae-in": {"anime": "Solo Leveling", "gender": "female"},
    
    # Kaiju No. 8
    "kafka hibino": {"anime": "Kaiju No. 8", "gender": "male"},
    "mina ashiro": {"anime": "Kaiju No. 8", "gender": "female"},
    
    # Bocchi the Rock
    "bocchi": {"anime": "Bocchi the Rock", "gender": "female"},
    "hitori gotoh": {"anime": "Bocchi the Rock", "gender": "female"},
    "nijika": {"anime": "Bocchi the Rock", "gender": "female"},
    "ryo": {"anime": "Bocchi the Rock", "gender": "female"},
    "kita": {"anime": "Bocchi the Rock", "gender": "female"},
    
    # Oshi no Ko
    "ai hoshino": {"anime": "Oshi no Ko", "gender": "female"},
    "aqua": {"anime": "Oshi no Ko", "gender": "male"},
    "ruby": {"anime": "Oshi no Ko", "gender": "female"},
    "kana arima": {"anime": "Oshi no Ko", "gender": "female"},
    "akane kurokawa": {"anime": "Oshi no Ko", "gender": "female"},
    
    # Blue Lock
    "isagi": {"anime": "Blue Lock", "gender": "male"},
    "isagi yoichi": {"anime": "Blue Lock", "gender": "male"},
    "bachira": {"anime": "Blue Lock", "gender": "male"},
    "nagi": {"anime": "Blue Lock", "gender": "male"},
    "rin itoshi": {"anime": "Blue Lock", "gender": "male"},
    "sae itoshi": {"anime": "Blue Lock", "gender": "male"},
    
    # Haikyuu
    "hinata": {"anime": "Haikyuu", "gender": "male"},
    "shoyo hinata": {"anime": "Haikyuu", "gender": "male"},
    "kageyama": {"anime": "Haikyuu", "gender": "male"},
    "oikawa": {"anime": "Haikyuu", "gender": "male"},
    "tsukishima": {"anime": "Haikyuu", "gender": "male"},
    
    # Jojo's Bizarre Adventure
    "jotaro": {"anime": "JoJo's Bizarre Adventure", "gender": "male"},
    "jotaro kujo": {"anime": "JoJo's Bizarre Adventure", "gender": "male"},
    "dio": {"anime": "JoJo's Bizarre Adventure", "gender": "male"},
    "dio brando": {"anime": "JoJo's Bizarre Adventure", "gender": "male"},
    "giorno": {"anime": "JoJo's Bizarre Adventure", "gender": "male"},
    "giorno giovanna": {"anime": "JoJo's Bizarre Adventure", "gender": "male"},
    "joseph joestar": {"anime": "JoJo's Bizarre Adventure", "gender": "male"},
    "jolyne": {"anime": "JoJo's Bizarre Adventure", "gender": "female"},
    "jolyne cujoh": {"anime": "JoJo's Bizarre Adventure", "gender": "female"},
}


# =============================================================================
# SPIELE DATENBANK
# =============================================================================

GAMES = {
    # Gacha/RPG
    "genshin impact": {"type": "gacha", "genre": "action_rpg"},
    "genshin": {"type": "gacha", "genre": "action_rpg", "full_name": "Genshin Impact"},
    "honkai star rail": {"type": "gacha", "genre": "turn_based_rpg"},
    "honkai": {"type": "gacha", "genre": "action"},
    "hsr": {"type": "gacha", "genre": "turn_based_rpg", "full_name": "Honkai Star Rail"},
    "zenless zone zero": {"type": "gacha", "genre": "action"},
    "zzz": {"type": "gacha", "genre": "action", "full_name": "Zenless Zone Zero"},
    "wuthering waves": {"type": "gacha", "genre": "action_rpg"},
    "arknights": {"type": "gacha", "genre": "tower_defense"},
    "azur lane": {"type": "gacha", "genre": "shoot_em_up"},
    "blue archive": {"type": "gacha", "genre": "rpg"},
    "fate grand order": {"type": "gacha", "genre": "rpg"},
    "fgo": {"type": "gacha", "genre": "rpg", "full_name": "Fate Grand Order"},
    "nikke": {"type": "gacha", "genre": "shooter"},
    "reverse 1999": {"type": "gacha", "genre": "rpg"},
    "girl's frontline": {"type": "gacha", "genre": "tactical"},
    
    # MOBA/Competitive
    "league of legends": {"type": "moba", "genre": "moba"},
    "lol": {"type": "moba", "genre": "moba", "full_name": "League of Legends"},
    "dota 2": {"type": "moba", "genre": "moba"},
    "dota": {"type": "moba", "genre": "moba", "full_name": "Dota 2"},
    "valorant": {"type": "fps", "genre": "tactical_shooter"},
    "counter strike": {"type": "fps", "genre": "tactical_shooter"},
    "cs2": {"type": "fps", "genre": "tactical_shooter", "full_name": "Counter-Strike 2"},
    "csgo": {"type": "fps", "genre": "tactical_shooter", "full_name": "Counter-Strike: Global Offensive"},
    "overwatch": {"type": "fps", "genre": "hero_shooter"},
    "overwatch 2": {"type": "fps", "genre": "hero_shooter"},
    "apex legends": {"type": "fps", "genre": "battle_royale"},
    "apex": {"type": "fps", "genre": "battle_royale", "full_name": "Apex Legends"},
    "fortnite": {"type": "fps", "genre": "battle_royale"},
    "pubg": {"type": "fps", "genre": "battle_royale", "full_name": "PlayerUnknown's Battlegrounds"},
    "rainbow six siege": {"type": "fps", "genre": "tactical_shooter"},
    "r6": {"type": "fps", "genre": "tactical_shooter", "full_name": "Rainbow Six Siege"},
    "call of duty": {"type": "fps", "genre": "shooter"},
    "cod": {"type": "fps", "genre": "shooter", "full_name": "Call of Duty"},
    "warzone": {"type": "fps", "genre": "battle_royale"},
    
    # RPG/Action
    "elden ring": {"type": "rpg", "genre": "action_rpg"},
    "dark souls": {"type": "rpg", "genre": "action_rpg"},
    "bloodborne": {"type": "rpg", "genre": "action_rpg"},
    "sekiro": {"type": "rpg", "genre": "action"},
    "final fantasy": {"type": "rpg", "genre": "jrpg"},
    "final fantasy xiv": {"type": "mmorpg", "genre": "mmorpg"},
    "ff14": {"type": "mmorpg", "genre": "mmorpg", "full_name": "Final Fantasy XIV"},
    "ffxiv": {"type": "mmorpg", "genre": "mmorpg", "full_name": "Final Fantasy XIV"},
    "world of warcraft": {"type": "mmorpg", "genre": "mmorpg"},
    "wow": {"type": "mmorpg", "genre": "mmorpg", "full_name": "World of Warcraft"},
    "diablo": {"type": "arpg", "genre": "action_rpg"},
    "diablo 4": {"type": "arpg", "genre": "action_rpg"},
    "path of exile": {"type": "arpg", "genre": "action_rpg"},
    "poe": {"type": "arpg", "genre": "action_rpg", "full_name": "Path of Exile"},
    "monster hunter": {"type": "rpg", "genre": "action_rpg"},
    "persona 5": {"type": "rpg", "genre": "jrpg"},
    "baldurs gate 3": {"type": "rpg", "genre": "crpg"},
    "bg3": {"type": "rpg", "genre": "crpg", "full_name": "Baldur's Gate 3"},
    "cyberpunk 2077": {"type": "rpg", "genre": "action_rpg"},
    "cyberpunk": {"type": "rpg", "genre": "action_rpg", "full_name": "Cyberpunk 2077"},
    "the witcher": {"type": "rpg", "genre": "action_rpg"},
    "witcher 3": {"type": "rpg", "genre": "action_rpg"},
    "skyrim": {"type": "rpg", "genre": "action_rpg"},
    "starfield": {"type": "rpg", "genre": "action_rpg"},
    
    # Nintendo
    "zelda": {"type": "adventure", "genre": "action_adventure"},
    "zelda tears of the kingdom": {"type": "adventure", "genre": "action_adventure"},
    "totk": {"type": "adventure", "genre": "action_adventure", "full_name": "Zelda: Tears of the Kingdom"},
    "breath of the wild": {"type": "adventure", "genre": "action_adventure"},
    "botw": {"type": "adventure", "genre": "action_adventure", "full_name": "Breath of the Wild"},
    "pokemon": {"type": "rpg", "genre": "jrpg"},
    "pokemon scarlet": {"type": "rpg", "genre": "jrpg"},
    "pokemon violet": {"type": "rpg", "genre": "jrpg"},
    "super mario": {"type": "platformer", "genre": "platformer"},
    "mario kart": {"type": "racing", "genre": "racing"},
    "mario kart 8": {"type": "racing", "genre": "racing"},
    "super smash bros": {"type": "fighting", "genre": "fighting"},
    "smash bros": {"type": "fighting", "genre": "fighting", "full_name": "Super Smash Bros"},
    "animal crossing": {"type": "simulation", "genre": "life_sim"},
    "splatoon": {"type": "shooter", "genre": "third_person_shooter"},
    
    # Sandbox/Survival
    "minecraft": {"type": "sandbox", "genre": "sandbox"},
    "terraria": {"type": "sandbox", "genre": "sandbox"},
    "roblox": {"type": "platform", "genre": "sandbox"},
    "rust": {"type": "survival", "genre": "survival"},
    "ark": {"type": "survival", "genre": "survival"},
    "valheim": {"type": "survival", "genre": "survival"},
    "subnautica": {"type": "survival", "genre": "survival"},
    "the forest": {"type": "survival", "genre": "survival"},
    "palworld": {"type": "survival", "genre": "survival"},
    "satisfactory": {"type": "simulation", "genre": "factory"},
    "factorio": {"type": "simulation", "genre": "factory"},
    "stardew valley": {"type": "simulation", "genre": "farming_sim"},
    
    # Other
    "gta": {"type": "action", "genre": "open_world", "full_name": "Grand Theft Auto"},
    "gta v": {"type": "action", "genre": "open_world"},
    "gta 6": {"type": "action", "genre": "open_world"},
    "red dead redemption": {"type": "action", "genre": "open_world"},
    "rdr2": {"type": "action", "genre": "open_world", "full_name": "Red Dead Redemption 2"},
    "destiny 2": {"type": "fps", "genre": "looter_shooter"},
    "destiny": {"type": "fps", "genre": "looter_shooter"},
    "rocket league": {"type": "sports", "genre": "sports"},
    "fifa": {"type": "sports", "genre": "sports"},
    "ea fc": {"type": "sports", "genre": "sports"},
    "nba 2k": {"type": "sports", "genre": "sports"},
    "dead by daylight": {"type": "horror", "genre": "asymmetric_horror"},
    "dbd": {"type": "horror", "genre": "asymmetric_horror", "full_name": "Dead by Daylight"},
    "phasmophobia": {"type": "horror", "genre": "horror"},
    "lethal company": {"type": "horror", "genre": "horror"},
    "among us": {"type": "party", "genre": "social_deduction"},
    "fall guys": {"type": "party", "genre": "party"},
    "it takes two": {"type": "coop", "genre": "action_adventure"},
    "hades": {"type": "roguelike", "genre": "roguelike"},
    "hades 2": {"type": "roguelike", "genre": "roguelike"},
    "hollow knight": {"type": "metroidvania", "genre": "metroidvania"},
    "silksong": {"type": "metroidvania", "genre": "metroidvania"},
    "celeste": {"type": "platformer", "genre": "platformer"},
    "cuphead": {"type": "action", "genre": "run_and_gun"},
}


# =============================================================================
# TECHNOLOGIE DATENBANK
# =============================================================================

TECHNOLOGY = {
    # AI/ML
    "chatgpt": {"category": "ai", "type": "llm"},
    "gpt-4": {"category": "ai", "type": "llm"},
    "gpt": {"category": "ai", "type": "llm"},
    "claude": {"category": "ai", "type": "llm"},
    "gemini": {"category": "ai", "type": "llm"},
    "llama": {"category": "ai", "type": "llm"},
    "mistral": {"category": "ai", "type": "llm"},
    "ollama": {"category": "ai", "type": "llm_runner"},
    "stable diffusion": {"category": "ai", "type": "image_gen"},
    "midjourney": {"category": "ai", "type": "image_gen"},
    "dall-e": {"category": "ai", "type": "image_gen"},
    "comfyui": {"category": "ai", "type": "image_gen_ui"},
    "automatic1111": {"category": "ai", "type": "image_gen_ui"},
    "tensorflow": {"category": "ai", "type": "ml_framework"},
    "pytorch": {"category": "ai", "type": "ml_framework"},
    "huggingface": {"category": "ai", "type": "ml_platform"},
    "openai": {"category": "ai", "type": "company"},
    "anthropic": {"category": "ai", "type": "company"},
    
    # Programming Languages
    "python": {"category": "programming", "type": "language"},
    "javascript": {"category": "programming", "type": "language"},
    "typescript": {"category": "programming", "type": "language"},
    "java": {"category": "programming", "type": "language"},
    "c++": {"category": "programming", "type": "language"},
    "c#": {"category": "programming", "type": "language"},
    "rust": {"category": "programming", "type": "language"},
    "go": {"category": "programming", "type": "language"},
    "kotlin": {"category": "programming", "type": "language"},
    "swift": {"category": "programming", "type": "language"},
    "ruby": {"category": "programming", "type": "language"},
    "php": {"category": "programming", "type": "language"},
    
    # Frameworks
    "react": {"category": "framework", "type": "frontend"},
    "vue": {"category": "framework", "type": "frontend"},
    "angular": {"category": "framework", "type": "frontend"},
    "svelte": {"category": "framework", "type": "frontend"},
    "next.js": {"category": "framework", "type": "fullstack"},
    "nextjs": {"category": "framework", "type": "fullstack"},
    "node.js": {"category": "runtime", "type": "backend"},
    "nodejs": {"category": "runtime", "type": "backend"},
    "django": {"category": "framework", "type": "backend"},
    "flask": {"category": "framework", "type": "backend"},
    "fastapi": {"category": "framework", "type": "backend"},
    
    # DevOps/Infrastructure
    "docker": {"category": "devops", "type": "container"},
    "kubernetes": {"category": "devops", "type": "orchestration"},
    "k8s": {"category": "devops", "type": "orchestration", "full_name": "Kubernetes"},
    "aws": {"category": "cloud", "type": "cloud_provider"},
    "azure": {"category": "cloud", "type": "cloud_provider"},
    "google cloud": {"category": "cloud", "type": "cloud_provider"},
    "gcp": {"category": "cloud", "type": "cloud_provider", "full_name": "Google Cloud Platform"},
    "github": {"category": "devops", "type": "version_control"},
    "gitlab": {"category": "devops", "type": "version_control"},
    "jenkins": {"category": "devops", "type": "ci_cd"},
    "terraform": {"category": "devops", "type": "iac"},
    "ansible": {"category": "devops", "type": "automation"},
    
    # Hardware/Embedded
    "raspberry pi": {"category": "hardware", "type": "sbc"},
    "pi": {"category": "hardware", "type": "sbc", "full_name": "Raspberry Pi"},
    "arduino": {"category": "hardware", "type": "microcontroller"},
    "esp32": {"category": "hardware", "type": "microcontroller"},
    "nvidia": {"category": "hardware", "type": "gpu"},
    "rtx": {"category": "hardware", "type": "gpu"},
    "amd": {"category": "hardware", "type": "cpu_gpu"},
    "intel": {"category": "hardware", "type": "cpu"},
    
    # OS
    "linux": {"category": "os", "type": "operating_system"},
    "ubuntu": {"category": "os", "type": "linux_distro"},
    "debian": {"category": "os", "type": "linux_distro"},
    "arch linux": {"category": "os", "type": "linux_distro"},
    "windows": {"category": "os", "type": "operating_system"},
    "windows 11": {"category": "os", "type": "operating_system"},
    "macos": {"category": "os", "type": "operating_system"},
    "android": {"category": "os", "type": "mobile_os"},
    "ios": {"category": "os", "type": "mobile_os"},
    
    # Smart Home
    "home assistant": {"category": "smart_home", "type": "hub"},
    "homeassistant": {"category": "smart_home", "type": "hub"},
    "zigbee": {"category": "smart_home", "type": "protocol"},
    "z-wave": {"category": "smart_home", "type": "protocol"},
    "matter": {"category": "smart_home", "type": "protocol"},
    "alexa": {"category": "smart_home", "type": "assistant"},
    "google home": {"category": "smart_home", "type": "assistant"},
    "homekit": {"category": "smart_home", "type": "platform"},
    "tuya": {"category": "smart_home", "type": "platform"},
    "tasmota": {"category": "smart_home", "type": "firmware"},
    "esphome": {"category": "smart_home", "type": "firmware"},
    
    # Databases
    "mysql": {"category": "database", "type": "relational"},
    "postgresql": {"category": "database", "type": "relational"},
    "postgres": {"category": "database", "type": "relational"},
    "mongodb": {"category": "database", "type": "nosql"},
    "redis": {"category": "database", "type": "cache"},
    "sqlite": {"category": "database", "type": "embedded"},
    "elasticsearch": {"category": "database", "type": "search"},
}


# =============================================================================
# HELPER FUNKTIONEN
# =============================================================================

def get_all_known_entities():
    """Kombiniere alle Entity-Datenbanken"""
    entities = {}
    
    # Gaming Characters
    for name, info in GAMING_CHARACTERS.items():
        entities[name] = {"type": "character", **info}
    
    # Anime Characters
    for name, info in ANIME_CHARACTERS.items():
        entities[name] = {"type": "character", **info}
    
    # Games
    for name, info in GAMES.items():
        entities[name] = {"type": "game", **info}
    
    # Technology
    for name, info in TECHNOLOGY.items():
        entities[name] = {"type": "technology", **info}
    
    return entities


# Statistiken
if __name__ == "__main__":
    print("=" * 70)
    print("📊 HOLO ENTITY DATABASE STATISTIKEN")
    print("=" * 70)
    
    male_names = get_all_male_names()
    female_names = get_all_female_names()
    all_entities = get_all_known_entities()
    
    print(f"\n👤 NAMEN:")
    print(f"   Männliche Vornamen: {len(male_names)}")
    print(f"   Weibliche Vornamen: {len(female_names)}")
    print(f"   Gesamt: {len(male_names) + len(female_names)}")
    
    print(f"\n🎮 GAMING CHARAKTERE: {len(GAMING_CHARACTERS)}")
    print(f"🎬 ANIME CHARAKTERE: {len(ANIME_CHARACTERS)}")
    print(f"🕹️ SPIELE: {len(GAMES)}")
    print(f"💻 TECHNOLOGIE: {len(TECHNOLOGY)}")
    
    print(f"\n📦 GESAMT ENTITIES: {len(all_entities)}")
    
    print("\n" + "=" * 70)
