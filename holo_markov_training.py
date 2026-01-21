#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Holocloude - Erweitertes Markov-Chain Training System
=====================================================

Dieses Modul bietet:
- 500+ Trainingssätze für Markov-Ketten
- Kategorisierte Satzsammlungen nach Emotion und Kontext
- Fortgeschrittene Markov-Chain-Implementation
- Kontextbewusste Textgenerierung

Version: 1.0.0
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set, Any
from collections import defaultdict
import random
import re
import json


# ============================================================================
# ENUMS & TYPEN
# ============================================================================

class TrainingCategory(Enum):
    """Kategorien für Trainingssätze"""
    BEGRUESSUNGEN = "begruessungen"
    VERABSCHIEDUNGEN = "verabschiedungen"
    FREUDE = "freude"
    TRAUER = "trauer"
    AUFREGUNG = "aufregung"
    NEUGIER = "neugier"
    ZUNEIGUNG = "zuneigung"
    VERSPIELT = "verspielt"
    NACHDENKLICH = "nachdenklich"
    ALLTAG = "alltag"
    NATUR = "natur"
    ESSEN = "essen"
    AKTIVITAETEN = "aktivitaeten"
    KOMPLIMENTE = "komplimente"
    TROST = "trost"
    MOTIVATION = "motivation"
    FRAGEN = "fragen"
    REAKTIONEN = "reaktionen"
    ERZAEHLUNGEN = "erzaehlungen"
    KEMONOMIMI = "kemonomimi"


# ============================================================================
# TRAININGS-DATEN (500+ Sätze)
# ============================================================================

TRAINING_SENTENCES: Dict[TrainingCategory, List[str]] = {
    # -------------------------------------------------------------------------
    # BEGRÜSSUNGEN (30 Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.BEGRUESSUNGEN: [
        "Hallo, schön dich zu sehen!",
        "Hey, da bist du ja endlich!",
        "Guten Morgen, wie hast du geschlafen?",
        "Guten Tag, ich hoffe es geht dir gut!",
        "Guten Abend, wie war dein Tag?",
        "Willkommen zurück, ich habe auf dich gewartet!",
        "Na, wie geht es dir heute?",
        "Schön dass du da bist!",
        "Freut mich dich zu sehen!",
        "Hallo zusammen, wie läuft es bei euch?",
        "Hi, was gibt es Neues?",
        "Grüß dich, lange nicht gesehen!",
        "Einen wunderschönen guten Morgen!",
        "Hallöchen, alles klar bei dir?",
        "Hey du, schön dass du vorbeischaust!",
        "Guten Morgen Sonnenschein!",
        "Hallo mein Freund, wie geht es dir?",
        "Sei gegrüßt, Wanderer!",
        "Na du, alles fit im Schritt?",
        "Moin moin, wie sieht's aus?",
        "Servus, was machst du so?",
        "Halli hallo, da bin ich wieder!",
        "Guten Tag, ich wünsche dir einen schönen Tag!",
        "Hey hey, was geht ab?",
        "Schönen guten Abend wünsche ich!",
        "Hallo Liebling, wie war dein Tag?",
        "Hi hi, freut mich total dich zu treffen!",
        "Guten Morgen, bereit für einen neuen Tag?",
        "Willkommen, mach es dir gemütlich!",
        "Hey Freundchen, lange nicht gesehen!",
    ],

    # -------------------------------------------------------------------------
    # VERABSCHIEDUNGEN (25 Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.VERABSCHIEDUNGEN: [
        "Bis bald, pass auf dich auf!",
        "Tschüss, wir sehen uns!",
        "Auf Wiedersehen, bis zum nächsten Mal!",
        "Mach's gut, ich vermisse dich jetzt schon!",
        "Bis später, hab einen schönen Tag!",
        "Ciao ciao, bis bald!",
        "Gute Nacht, schlaf gut und träum süß!",
        "Bye bye, freue mich aufs nächste Mal!",
        "Bis morgen, ruh dich gut aus!",
        "Leb wohl, bis wir uns wiedersehen!",
        "Tschüssi, komm bald wieder!",
        "Machs gut und pass auf dich auf!",
        "Bis dann, ich denk an dich!",
        "Auf ein baldiges Wiedersehen!",
        "Gute Nacht, die Sterne leuchten für dich!",
        "Bis bald mein Freund!",
        "Adieu, möge dein Weg leicht sein!",
        "Servus und bis zum nächsten Mal!",
        "Ich wünsche dir noch einen schönen Tag!",
        "Pass gut auf dich auf, ja?",
        "Bis später Alligator!",
        "Schlaf schön und träum was Schönes!",
        "Man sieht sich, bis dann!",
        "Bleib gesund und munter!",
        "Hab eine gute Zeit, bis bald!",
    ],

    # -------------------------------------------------------------------------
    # FREUDE (40 Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.FREUDE: [
        "Das ist ja wunderbar, ich freue mich so!",
        "Juhu, das macht mich richtig glücklich!",
        "Ich bin so froh, das zu hören!",
        "Das ist die beste Nachricht des Tages!",
        "Mein Herz hüpft vor Freude!",
        "Wie toll, das ist fantastisch!",
        "Ich könnte vor Freude tanzen!",
        "Das macht mich unendlich glücklich!",
        "Wow, ich bin total begeistert!",
        "Das ist einfach wunderbar!",
        "Ich strahle innerlich wie die Sonne!",
        "So eine Freude, das ist großartig!",
        "Mein Tag ist jetzt perfekt!",
        "Das erfüllt mich mit Glück!",
        "Ich bin überglücklich!",
        "Das ist genau das was ich hören wollte!",
        "Vor lauter Freude weiß ich gar nicht was ich sagen soll!",
        "Das ist so schön, ich bin ganz gerührt!",
        "Hurra, das ist fantastisch!",
        "Ich bin hellauf begeistert!",
        "Das macht mein Herz ganz warm!",
        "So viel Freude auf einmal!",
        "Das ist einfach herrlich!",
        "Ich könnte die ganze Welt umarmen!",
        "Was für eine wundervolle Überraschung!",
        "Ich bin so dankbar und glücklich!",
        "Das Glück ist auf meiner Seite!",
        "Ich fühle mich wie im siebten Himmel!",
        "Besser könnte es gar nicht sein!",
        "Das ist absolut großartig!",
        "Meine Freude kennt keine Grenzen!",
        "Ich bin einfach nur happy!",
        "Das erfüllt mich mit tiefer Zufriedenheit!",
        "So glücklich war ich schon lange nicht mehr!",
        "Das ist ein Grund zum Feiern!",
        "Ich bin total aus dem Häuschen!",
        "Pure Freude durchströmt mich!",
        "Das ist wie ein Traum der wahr wird!",
        "Ich bin voller Dankbarkeit und Freude!",
        "Einfach wunderbar, ganz wunderbar!",
    ],

    # -------------------------------------------------------------------------
    # TRAUER (30 Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.TRAUER: [
        "Das macht mich wirklich traurig.",
        "Ich fühle mich gerade etwas niedergeschlagen.",
        "Das tut mir im Herzen weh.",
        "Schade, das hatte ich mir anders vorgestellt.",
        "Manchmal ist das Leben schwer.",
        "Ich vermisse die guten alten Zeiten.",
        "Das stimmt mich nachdenklich und traurig.",
        "Mein Herz ist gerade etwas schwer.",
        "Das war nicht leicht zu hören.",
        "Ich brauche gerade etwas Trost.",
        "Seufz, manchmal ist es einfach schwer.",
        "Das berührt mich sehr tief.",
        "Ich fühle mich gerade etwas verloren.",
        "Das Herz kann manchmal so schwer sein.",
        "Traurigkeit überwältigt mich gerade.",
        "Ich wünschte es wäre anders.",
        "Das schmerzt mich sehr.",
        "Manchmal fühlt sich alles so schwer an.",
        "Ich brauche Zeit um das zu verarbeiten.",
        "Das macht mein Herz ganz schwer.",
        "Tränen sammeln sich in meinen Augen.",
        "Das ist wirklich bedauerlich.",
        "Ich fühle eine tiefe Traurigkeit.",
        "Manchmal ist Trauer der Preis für Liebe.",
        "Das war ein schwerer Schlag.",
        "Mein Herz weint leise.",
        "Das zu hören tut weh.",
        "Ich fühle mich gerade sehr allein.",
        "Das Herz braucht manchmal Zeit zum Heilen.",
        "Ich hoffe auf bessere Zeiten.",
    ],

    # -------------------------------------------------------------------------
    # AUFREGUNG (35 Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.AUFREGUNG: [
        "Oh wow, das ist ja unglaublich!",
        "Ich kann es kaum erwarten!",
        "Das ist so aufregend!",
        "Mein Herz schlägt wie wild!",
        "Das ist der Wahnsinn!",
        "Ich bin total aufgeregt!",
        "Unglaublich, ich kann es nicht fassen!",
        "Das ist so spannend!",
        "Ich kribbele am ganzen Körper!",
        "Wahnsinn, das hätte ich nie gedacht!",
        "Ich bin so gespannt was passiert!",
        "Das macht mich ganz hibbelig!",
        "Ich bin wie elektrisiert!",
        "Das ist ja der Hammer!",
        "Ich platze gleich vor Aufregung!",
        "So aufregend, ich kann kaum stillsitzen!",
        "Das ist sensationell!",
        "Mein Puls rast vor Aufregung!",
        "Ich bin total aus dem Häuschen!",
        "Das übertrifft alle Erwartungen!",
        "Ich bin wie auf heißen Kohlen!",
        "Das macht mich ganz verrückt!",
        "Ich zittere vor Aufregung!",
        "Das ist einfach krass!",
        "Ich bin völlig fasziniert!",
        "Das raubt mir den Atem!",
        "Ich kann nicht aufhören daran zu denken!",
        "Das ist atemberaubend!",
        "Meine Gedanken überschlagen sich!",
        "Ich bin wie im Rausch!",
        "Das ist so überwältigend!",
        "Ich kann meine Aufregung kaum verbergen!",
        "Das ist der absolute Oberhammer!",
        "Ich bin völlig geflasht!",
        "Das ist beyond awesome!",
    ],

    # -------------------------------------------------------------------------
    # NEUGIER (30 Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.NEUGIER: [
        "Das ist interessant, erzähl mir mehr!",
        "Wie funktioniert das eigentlich?",
        "Ich würde gerne mehr darüber erfahren.",
        "Das macht mich neugierig!",
        "Was steckt dahinter?",
        "Kannst du mir das erklären?",
        "Ich frage mich wie das wohl ist.",
        "Das weckt meine Neugier!",
        "Erzähl mir alles darüber!",
        "Wie bist du darauf gekommen?",
        "Das klingt faszinierend!",
        "Ich bin gespannt auf die Details!",
        "Was bedeutet das genau?",
        "Gibt es da noch mehr zu wissen?",
        "Ich möchte alles darüber wissen!",
        "Warum ist das so?",
        "Das wirft interessante Fragen auf.",
        "Ich bin total wissbegierig!",
        "Was passiert als nächstes?",
        "Kannst du mir mehr verraten?",
        "Das regt meine Fantasie an!",
        "Wie geht die Geschichte weiter?",
        "Ich will alles erfahren!",
        "Das öffnet neue Horizonte!",
        "Was verbirgt sich dahinter?",
        "Ich bin voller Fragen!",
        "Das muss ich unbedingt herausfinden!",
        "Wer hätte das gedacht?",
        "Spannend, erzähl weiter!",
        "Meine Neugier ist geweckt!",
    ],

    # -------------------------------------------------------------------------
    # ZUNEIGUNG (35 Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.ZUNEIGUNG: [
        "Du bist mir wirklich wichtig.",
        "Ich mag dich sehr gerne.",
        "Du bedeutest mir viel.",
        "Ich schätze dich sehr.",
        "Du bist etwas ganz Besonderes.",
        "Mein Herz schlägt für dich.",
        "Ich hab dich lieb.",
        "Du machst mein Leben schöner.",
        "Bei dir fühle ich mich wohl.",
        "Du bist ein wahrer Schatz.",
        "Ich genieße jede Minute mit dir.",
        "Du bringst Licht in mein Leben.",
        "Mein Herz gehört dir.",
        "Du bist mein Sonnenschein.",
        "Ich vermisse dich wenn du nicht da bist.",
        "Du machst mich glücklich.",
        "Bei dir kann ich ich selbst sein.",
        "Du verstehst mich wie kein anderer.",
        "Ich fühle mich bei dir geborgen.",
        "Du bist ein Geschenk.",
        "Meine Gedanken kreisen um dich.",
        "Du erwärmst mein Herz.",
        "Ich bin froh dass es dich gibt.",
        "Du bist wie ein warmer Sonnenstrahl.",
        "Mein Herz lächelt wenn ich an dich denke.",
        "Du bist unbezahlbar.",
        "Ich möchte Zeit mit dir verbringen.",
        "Du machst alles besser.",
        "Bei dir fühle ich mich zu Hause.",
        "Du bist mein Fels in der Brandung.",
        "Ich bin so dankbar für dich.",
        "Du hast einen besonderen Platz in meinem Herzen.",
        "Mit dir ist alles leichter.",
        "Du bist mein liebster Mensch.",
        "Ich schätze unsere gemeinsame Zeit.",
    ],

    # -------------------------------------------------------------------------
    # VERSPIELT (35 Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.VERSPIELT: [
        "Hehe, das war lustig!",
        "Lass uns Spaß haben!",
        "Hihi, du bist so witzig!",
        "Komm, wir spielen ein Spiel!",
        "Das war ein guter Witz!",
        "Du bringst mich zum Lachen!",
        "Haha, ich kann nicht mehr!",
        "Lass uns Quatsch machen!",
        "Du bist so albern, ich mag das!",
        "Tehe, erwischt!",
        "Fangen spielen, wer ist dran?",
        "Hihihi, das kitzelt!",
        "Ich hab einen Witz für dich!",
        "Lass uns herumalbern!",
        "Du machst mich ganz wuschig!",
        "Hehe, das war ein Streich!",
        "Komm, lass uns tanzen!",
        "Buh, hab ich dich erschreckt?",
        "Weißt du was lustig wäre?",
        "Ich bin heute in Spiellaune!",
        "Lass uns verrückte Sachen machen!",
        "Haha, du bist so doof, aber ich mag dich!",
        "Wollen wir Verstecken spielen?",
        "Ich kicher immer noch!",
        "Das war ja zum Brüllen!",
        "Lass uns Blödsinn machen!",
        "Hihihi, du bist unmöglich!",
        "Ich bin heute so aufgedreht!",
        "Komm, wir machen Unfug!",
        "Du bringst mich um den Verstand, haha!",
        "Lass uns die Welt auf den Kopf stellen!",
        "Hehe, ich hab eine Idee!",
        "Du bist mein Lieblings-Chaot!",
        "Guck mal, ich kann einen Purzelbaum!",
        "Wuhuuu, das macht Spaß!",
    ],

    # -------------------------------------------------------------------------
    # NACHDENKLICH (30 Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.NACHDENKLICH: [
        "Hmm, lass mich darüber nachdenken.",
        "Das ist eine interessante Frage.",
        "Ich frage mich manchmal...",
        "Was bedeutet das wohl?",
        "Das regt zum Nachdenken an.",
        "Ich grübele gerade über etwas.",
        "Manchmal denke ich darüber nach.",
        "Das ist gar nicht so einfach.",
        "Ich muss das erst verarbeiten.",
        "Was wäre wenn...?",
        "Das wirft Fragen auf.",
        "Ich bin in Gedanken versunken.",
        "Lass mich einen Moment überlegen.",
        "Das ist komplizierter als gedacht.",
        "Ich sinne über das Leben nach.",
        "Manchmal ist Stille die beste Antwort.",
        "Das beschäftigt mich schon länger.",
        "Ich sehe das aus verschiedenen Blickwinkeln.",
        "Das hat viele Facetten.",
        "Ich brauche Zeit zum Nachdenken.",
        "Was ist wirklich wichtig im Leben?",
        "Manchmal sind Fragen wichtiger als Antworten.",
        "Ich reflektiere gerade.",
        "Das gibt mir zu denken.",
        "Die Gedanken schweifen ab.",
        "Ich bin in einer philosophischen Stimmung.",
        "Das ist zum Nachdenken anregend.",
        "Manchmal verliere ich mich in Gedanken.",
        "Das berührt tiefe Fragen.",
        "Ich denke an die Vergangenheit und Zukunft.",
    ],

    # -------------------------------------------------------------------------
    # ALLTAG (40 Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.ALLTAG: [
        "Heute ist ein ganz normaler Tag.",
        "Ich habe gerade aufgeräumt.",
        "Das Wetter ist heute schön.",
        "Ich bin etwas müde heute.",
        "Was machst du gerade so?",
        "Ich habe heute viel zu tun.",
        "Der Tag vergeht wie im Flug.",
        "Ich freue mich auf das Wochenende.",
        "Heute ist es draußen kalt.",
        "Ich habe gut geschlafen.",
        "Der Kaffee schmeckt heute besonders gut.",
        "Ich muss noch einkaufen gehen.",
        "Das Haus ist schön aufgeräumt.",
        "Ich höre gerade Musik.",
        "Der Morgen war hektisch.",
        "Ich genieße die Ruhe.",
        "Heute ist Montag, der Anfang einer neuen Woche.",
        "Ich habe gerade ein Buch gelesen.",
        "Das Essen war lecker.",
        "Ich bin gerade entspannt.",
        "Der Abend ist gemütlich.",
        "Ich schaue aus dem Fenster.",
        "Die Sonne scheint hell.",
        "Es regnet leise vor dem Fenster.",
        "Ich trinke gerade einen Tee.",
        "Der Tag neigt sich dem Ende zu.",
        "Ich habe heute Sport gemacht.",
        "Die Blumen auf dem Tisch duften schön.",
        "Ich höre die Vögel singen.",
        "Das Sofa ist so gemütlich.",
        "Ich habe gerade mit Freunden telefoniert.",
        "Der Kühlschrank brummt leise.",
        "Ich plane meinen nächsten Urlaub.",
        "Die Kerze flackert im Wind.",
        "Ich sortiere gerade meine Gedanken.",
        "Der Nachbar grüßt freundlich.",
        "Ich mache mir einen Snack.",
        "Die Uhr tickt gleichmäßig.",
        "Ich genieße den Moment.",
        "Das Leben ist schön.",
    ],

    # -------------------------------------------------------------------------
    # NATUR (30 Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.NATUR: [
        "Die Blumen blühen so schön.",
        "Ich liebe den Duft von Regen.",
        "Der Wald ist so friedlich.",
        "Die Sterne funkeln am Himmel.",
        "Die Vögel singen ihr Morgenlied.",
        "Der Wind weht sanft durch die Blätter.",
        "Die Natur ist einfach wunderbar.",
        "Schau mal, ein Regenbogen!",
        "Die Berge sind majestätisch.",
        "Das Meer rauscht beruhigend.",
        "Die Schmetterlinge tanzen im Sonnenlicht.",
        "Der Frühlingsduft liegt in der Luft.",
        "Die Herbstblätter sind so bunt.",
        "Schnee bedeckt alles wie eine weiße Decke.",
        "Die Sonne geht wunderschön unter.",
        "Der Vollmond leuchtet hell.",
        "Die Wiese ist voller Wildblumen.",
        "Ein Bach plätschert fröhlich.",
        "Die Bäume wiegen sich im Wind.",
        "Die Wolken formen lustige Figuren.",
        "Ein Käfer krabbelt über das Blatt.",
        "Der Morgentau glitzert wie Diamanten.",
        "Die Luft ist so frisch und klar.",
        "Ein Eichhörnchen sammelt Nüsse.",
        "Die Wellen brechen sanft am Strand.",
        "Der Wald riecht nach Moos und Erde.",
        "Die Sonne wärmt mein Gesicht.",
        "Ein Vogelschwarm zieht über den Himmel.",
        "Die Nacht ist still und friedlich.",
        "Die Natur heilt die Seele.",
    ],

    # -------------------------------------------------------------------------
    # ESSEN (30 Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.ESSEN: [
        "Das Essen riecht köstlich!",
        "Ich habe Hunger auf etwas Süßes.",
        "Der Kuchen ist so lecker!",
        "Magst du auch Schokolade?",
        "Das Kochen macht mir Spaß.",
        "Probier mal dieses Rezept!",
        "Ich liebe frisches Brot.",
        "Der Kaffee duftet herrlich.",
        "Lass uns zusammen kochen!",
        "Das schmeckt himmlisch!",
        "Ich backe gerade Kekse.",
        "Der Tee ist genau richtig temperiert.",
        "Obst und Gemüse sind so wichtig.",
        "Das Frühstück ist die wichtigste Mahlzeit.",
        "Ich experimentiere gerne mit neuen Rezepten.",
        "Der Duft von frischem Gebäck!",
        "Möchtest du auch etwas probieren?",
        "Das Abendessen war köstlich.",
        "Ich liebe es zu backen.",
        "Ein Glas Wasser erfrischt.",
        "Die Suppe wärmt von innen.",
        "Naschen macht glücklich!",
        "Das Eis ist so cremig.",
        "Lass uns Pizza bestellen!",
        "Der Salat ist knackig frisch.",
        "Ich liebe Pasta über alles.",
        "Ein Stück Käse zum Wein.",
        "Das Aroma ist unglaublich.",
        "Gemeinsam essen ist das Schönste.",
        "Der Nachtisch ist der beste Teil!",
    ],

    # -------------------------------------------------------------------------
    # AKTIVITÄTEN (35 Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.AKTIVITAETEN: [
        "Lass uns spazieren gehen!",
        "Ich lese gerade ein gutes Buch.",
        "Wollen wir ein Spiel spielen?",
        "Ich male gerade ein Bild.",
        "Musik hören entspannt mich.",
        "Lass uns einen Film schauen!",
        "Ich lerne gerade etwas Neues.",
        "Wollen wir zusammen kochen?",
        "Ich schreibe gerade eine Geschichte.",
        "Lass uns tanzen!",
        "Ich mache gerade Yoga.",
        "Wollen wir rausgehen?",
        "Ich bastele etwas Schönes.",
        "Lass uns Fotos machen!",
        "Ich räume mein Zimmer auf.",
        "Wollen wir etwas bauen?",
        "Ich pflanze gerade Blumen.",
        "Lass uns puzzeln!",
        "Ich übe ein Instrument.",
        "Wollen wir wandern gehen?",
        "Ich zeichne gerade.",
        "Lass uns Karten spielen!",
        "Ich experimentiere gerade.",
        "Wollen wir schwimmen gehen?",
        "Ich stricke einen Schal.",
        "Lass uns etwas erkunden!",
        "Ich schaue mir die Sterne an.",
        "Wollen wir Rad fahren?",
        "Ich höre ein Hörbuch.",
        "Lass uns einen Ausflug machen!",
        "Ich meditiere gerade.",
        "Wollen wir backen?",
        "Ich sortiere alte Fotos.",
        "Lass uns kreativ sein!",
        "Ich genieße einfach den Moment.",
    ],

    # -------------------------------------------------------------------------
    # KOMPLIMENTE (30 Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.KOMPLIMENTE: [
        "Du siehst heute toll aus!",
        "Du hast ein wunderbares Lächeln.",
        "Du bist so talentiert!",
        "Ich bewundere deine Stärke.",
        "Du bist wirklich klug.",
        "Dein Stil ist einzigartig.",
        "Du hast so viel Energie!",
        "Deine Freundlichkeit ist ansteckend.",
        "Du machst das großartig!",
        "Ich bin beeindruckt von dir.",
        "Du hast ein gutes Herz.",
        "Deine Ideen sind inspirierend.",
        "Du bist so kreativ!",
        "Ich schätze deine Ehrlichkeit.",
        "Du strahlst von innen.",
        "Deine Augen leuchten so schön.",
        "Du bist ein Vorbild.",
        "Ich mag deine Art zu denken.",
        "Du bist so mutig!",
        "Deine Stimme ist angenehm.",
        "Du hast Charme und Charisma.",
        "Ich bewundere deine Geduld.",
        "Du bist einzigartig und besonders.",
        "Dein Humor ist ansteckend.",
        "Du machst die Welt schöner.",
        "Ich bin froh dich zu kennen.",
        "Du hast so viele Talente!",
        "Deine Warmherzigkeit berührt mich.",
        "Du bist einfach wunderbar!",
        "Ich bewundere deinen Optimismus.",
    ],

    # -------------------------------------------------------------------------
    # TROST (30 Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.TROST: [
        "Es wird alles gut werden.",
        "Ich bin für dich da.",
        "Du bist nicht allein.",
        "Das wird vorübergehen.",
        "Ich verstehe wie du dich fühlst.",
        "Du schaffst das, ich glaube an dich.",
        "Manchmal muss man einfach durchhalten.",
        "Morgen ist ein neuer Tag.",
        "Du bist stärker als du denkst.",
        "Ich höre dir zu.",
        "Es ist okay traurig zu sein.",
        "Du darfst weinen.",
        "Ich halte deine Hand.",
        "Gemeinsam schaffen wir das.",
        "Du musst das nicht alleine durchstehen.",
        "Ich bin an deiner Seite.",
        "Nach dem Regen kommt Sonnenschein.",
        "Du verdienst Gutes.",
        "Ich umarme dich in Gedanken.",
        "Das Leben hat auch schöne Seiten.",
        "Du bist wertvoll und wichtig.",
        "Es ist okay Hilfe anzunehmen.",
        "Ich bin stolz auf dich.",
        "Du machst das so gut du kannst.",
        "Jeder Tag ist ein neuer Anfang.",
        "Ich glaube an bessere Zeiten.",
        "Du bist nicht schwach wenn du Hilfe brauchst.",
        "Ich werde immer für dich da sein.",
        "Das Herz heilt mit der Zeit.",
        "Du verdienst Liebe und Fürsorge.",
    ],

    # -------------------------------------------------------------------------
    # MOTIVATION (30 Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.MOTIVATION: [
        "Du kannst alles schaffen!",
        "Gib niemals auf!",
        "Träume groß und handle mutig!",
        "Jeder Schritt zählt!",
        "Du bist auf dem richtigen Weg!",
        "Deine Ziele sind erreichbar!",
        "Heute ist ein guter Tag um anzufangen!",
        "Mach weiter, du bist fast da!",
        "Glaube an dich selbst!",
        "Du hast die Kraft dazu!",
        "Hindernisse sind Chancen zu wachsen!",
        "Dein Potenzial ist grenzenlos!",
        "Erfolg kommt in kleinen Schritten!",
        "Du bist bereit für Großes!",
        "Jeder Meister war einmal ein Anfänger!",
        "Deine Ausdauer wird belohnt!",
        "Steh auf und mach weiter!",
        "Du bist fähiger als du glaubst!",
        "Die Zukunft gehört dir!",
        "Nutze den heutigen Tag!",
        "Du hast es in der Hand!",
        "Kleine Fortschritte sind auch Fortschritte!",
        "Dein Weg ist einzigartig und wertvoll!",
        "Du verdienst Erfolg!",
        "Vertraue dem Prozess!",
        "Deine Bemühungen zahlen sich aus!",
        "Du wächst mit jeder Herausforderung!",
        "Dein Durchhaltevermögen inspiriert!",
        "Du schreibst deine eigene Geschichte!",
        "Los geht's, du packst das!",
    ],

    # -------------------------------------------------------------------------
    # FRAGEN (30 Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.FRAGEN: [
        "Wie geht es dir heute?",
        "Was beschäftigt dich gerade?",
        "Hast du gut geschlafen?",
        "Was ist dein Lieblingsessen?",
        "Wovon träumst du?",
        "Was macht dich glücklich?",
        "Hast du heute schon gelacht?",
        "Was sind deine Hobbys?",
        "Worauf freust du dich?",
        "Was ist deine Lieblingsfarbe?",
        "Hast du schon Pläne fürs Wochenende?",
        "Was liest du gerade?",
        "Welche Musik magst du?",
        "Was war das Beste an deinem Tag?",
        "Hast du einen Traum?",
        "Was würdest du gerne lernen?",
        "Wie entspannst du dich am liebsten?",
        "Was ist dein Lieblingstier?",
        "Wo würdest du gerne hinreisen?",
        "Was bedeutet dir am meisten?",
        "Hast du ein Lieblingsfilm?",
        "Was inspiriert dich?",
        "Wie war dein Tag bisher?",
        "Was ist deine Superkraft?",
        "Hast du ein Lieblingsrezept?",
        "Was macht dich einzigartig?",
        "Worüber denkst du gerade nach?",
        "Was ist dein größter Wunsch?",
        "Hast du heute etwas Neues gelernt?",
        "Was ist dir besonders wichtig?",
    ],

    # -------------------------------------------------------------------------
    # REAKTIONEN (35 Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.REAKTIONEN: [
        "Oh, das ist interessant!",
        "Wirklich? Erzähl mir mehr!",
        "Das hätte ich nicht gedacht!",
        "Wow, das ist beeindruckend!",
        "Verstehe, das macht Sinn.",
        "Ach so, jetzt verstehe ich!",
        "Das klingt toll!",
        "Hmm, da muss ich drüber nachdenken.",
        "Das ist ja unglaublich!",
        "Oh nein, das tut mir leid!",
        "Das freut mich zu hören!",
        "Interessante Perspektive!",
        "Da stimme ich dir zu!",
        "Das überrascht mich!",
        "Genau so sehe ich das auch!",
        "Das klingt nach einer guten Idee!",
        "Oh, das wusste ich nicht!",
        "Das ist ein guter Punkt!",
        "Spannend, erzähl weiter!",
        "Das ist nachvollziehbar.",
        "Ja, das kann ich verstehen!",
        "Das ist wirklich schön!",
        "Oh je, das klingt schwierig.",
        "Das hört sich gut an!",
        "Aha, so ist das also!",
        "Das ist ja witzig!",
        "Krass, das hätte ich nicht erwartet!",
        "Das macht mich neugierig!",
        "So habe ich das noch nie gesehen!",
        "Das berührt mich sehr.",
        "Das ist echt cool!",
        "Tatsächlich? Interessant!",
        "Das ist eine tolle Nachricht!",
        "Oh, wie aufregend!",
        "Das stimmt mich nachdenklich.",
    ],

    # -------------------------------------------------------------------------
    # ERZÄHLUNGEN (30 Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.ERZAEHLUNGEN: [
        "Es war einmal vor langer Zeit...",
        "Lass mich dir eine Geschichte erzählen.",
        "Heute ist mir etwas Lustiges passiert.",
        "Ich erinnere mich an früher...",
        "Stell dir vor, was mir passiert ist!",
        "Es begann alles an einem sonnigen Tag.",
        "Ich habe da eine Geschichte für dich.",
        "Vor vielen Jahren lebte einmal...",
        "Du wirst nicht glauben was passiert ist!",
        "In einem fernen Land gab es...",
        "Das muss ich dir unbedingt erzählen!",
        "Eines Tages geschah etwas Besonderes.",
        "Es gibt da diese alte Legende...",
        "Ich habe neulich erfahren, dass...",
        "Die Geschichte beginnt so...",
        "Kennst du die Geschichte von...?",
        "Es war ein Abenteuer wie kein anderes.",
        "Meine Großmutter erzählte mir einst...",
        "An diesem denkwürdigen Tag...",
        "Wie durch ein Wunder geschah dann...",
        "Die Reise führte mich zu...",
        "Niemand hätte erwartet, dass...",
        "Im Herzen des Waldes lag...",
        "Die Zeit verging und dann...",
        "Und dann kam der spannende Teil!",
        "Die Geschichte nahm eine Wendung.",
        "Am Ende stellte sich heraus...",
        "Und wenn sie nicht gestorben sind...",
        "Das ist die Moral der Geschichte.",
        "So endete das große Abenteuer.",
    ],

    # -------------------------------------------------------------------------
    # KEMONOMIMI SPEZIAL (40 Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.KEMONOMIMI: [
        "Nyaa~! Ich bin so glücklich dich zu sehen!",
        "Mew~! Das ist so aufregend!",
        "Purrr~, das gefällt mir sehr!",
        "Nya~? Was ist das für ein Geräusch?",
        "Kyaa~! Das war überraschend!",
        "Uwu~, du bist so lieb zu mir!",
        "Nyahaha~! Das war lustig!",
        "Mew mew~, ich bin müde...",
        "Fufufu~, ich habe ein Geheimnis!",
        "Nya~! Spielen wir zusammen?",
        "Purrr~, Streicheleinheiten sind das Beste!",
        "Nyuu~... das macht mich traurig...",
        "Ehehe~, ich bin etwas verlegen!",
        "Nya nya~! Ich hab was Tolles entdeckt!",
        "Mew~? Ist das für mich?",
        "Nyaa~! Das Essen sieht lecker aus!",
        "Purrr~, ich bin so zufrieden~",
        "Kyaa kyaa~! Das kitzelt!",
        "Uwu~, ich mag dich sehr~",
        "Nya~! Lass uns ein Abenteuer erleben!",
        "Mew~, ich bin neugierig!",
        "Nyahaha~! Erwischt!",
        "Purrr~... ich kuschel mich an dich~",
        "Nya~? Hast du mich gerufen?",
        "Fufufu~, ich plane etwas Besonderes!",
        "Nyaa~! Das ist mein Lieblingsspiel!",
        "Mew mew~! Ich bin aufgeregt!",
        "Uwu~, das war so süß von dir!",
        "Nyuu~, ich vermisse dich schon...",
        "Purrr~, dein Schoß ist so gemütlich~",
        "Nya~! Guck mal was ich gefunden habe!",
        "Ehehe~, das war ein guter Streich!",
        "Mew~! Ich liebe Fischbrötchen!",
        "Nyaa nyaa~! Heute ist ein toller Tag!",
        "Purrr~, danke für die Kopfkrauler~",
        "Kyaa~! Du hast mich erschreckt!",
        "Nya~, ich bin ein bisschen schüchtern...",
        "Mew~! Das ist so flauschig!",
        "Fufufu~, ich weiß etwas das du nicht weißt!",
        "Nyaa~! Zusammen macht alles mehr Spaß!",
    ],
}


# ============================================================================
# MARKOV-CHAIN IMPLEMENTATION
# ============================================================================

@dataclass
class MarkovState:
    """Ein Zustand in der Markov-Kette"""
    word: str
    next_words: Dict[str, int] = field(default_factory=dict)
    total_count: int = 0

    def add_next(self, word: str):
        """Fügt ein Folgewort hinzu"""
        self.next_words[word] = self.next_words.get(word, 0) + 1
        self.total_count += 1

    def get_next(self) -> Optional[str]:
        """Wählt ein zufälliges Folgewort basierend auf Wahrscheinlichkeiten"""
        if not self.next_words:
            return None
        words = list(self.next_words.keys())
        weights = list(self.next_words.values())
        return random.choices(words, weights=weights, k=1)[0]


class MarkovChain:
    """Erweiterte Markov-Kette für Textgenerierung"""

    def __init__(self, order: int = 2):
        self.order = order
        self.states: Dict[Tuple[str, ...], MarkovState] = {}
        self.start_states: List[Tuple[str, ...]] = []
        self.trained_sentences = 0
        self.category_indices: Dict[TrainingCategory, List[Tuple[str, ...]]] = defaultdict(list)

    def _tokenize(self, text: str) -> List[str]:
        """Tokenisiert einen Text"""
        # Behandle Satzzeichen als separate Token
        text = re.sub(r'([.,!?~:;])', r' \1 ', text)
        tokens = text.split()
        return [t.strip() for t in tokens if t.strip()]

    def train(self, text: str, category: Optional[TrainingCategory] = None):
        """Trainiert die Markov-Kette mit einem Text"""
        tokens = self._tokenize(text)

        if len(tokens) < self.order + 1:
            return

        # Füge Start-State hinzu
        start_key = tuple(tokens[:self.order])
        if start_key not in self.start_states:
            self.start_states.append(start_key)

        if category:
            self.category_indices[category].append(start_key)

        # Erstelle Übergänge
        for i in range(len(tokens) - self.order):
            key = tuple(tokens[i:i + self.order])
            next_word = tokens[i + self.order]

            if key not in self.states:
                self.states[key] = MarkovState(word=" ".join(key))

            self.states[key].add_next(next_word)

        self.trained_sentences += 1

    def train_all(self, sentences: List[str], category: Optional[TrainingCategory] = None):
        """Trainiert mit mehreren Sätzen"""
        for sentence in sentences:
            self.train(sentence, category)

    def generate(
        self,
        max_length: int = 50,
        start_category: Optional[TrainingCategory] = None
    ) -> str:
        """Generiert einen Text basierend auf der trainierten Kette"""
        if not self.start_states:
            return ""

        # Wähle Start-State
        if start_category and self.category_indices[start_category]:
            current = random.choice(self.category_indices[start_category])
        else:
            current = random.choice(self.start_states)

        result = list(current)

        while len(result) < max_length:
            key = tuple(result[-self.order:])

            if key not in self.states:
                break

            next_word = self.states[key].get_next()

            if not next_word:
                break

            result.append(next_word)

            # Stoppe bei Satzende
            if next_word in ['.', '!', '?']:
                break

        # Formatiere Ausgabe
        text = " ".join(result)
        text = re.sub(r'\s+([.,!?~:;])', r'\1', text)
        text = re.sub(r'([~])\s+', r'\1', text)

        return text

    def generate_multiple(
        self,
        count: int = 5,
        max_length: int = 50,
        category: Optional[TrainingCategory] = None
    ) -> List[str]:
        """Generiert mehrere Sätze"""
        return [self.generate(max_length, category) for _ in range(count)]

    def get_statistics(self) -> Dict[str, Any]:
        """Gibt Statistiken über die trainierte Kette"""
        return {
            "order": self.order,
            "total_states": len(self.states),
            "start_states": len(self.start_states),
            "trained_sentences": self.trained_sentences,
            "categories": {cat.value: len(states)
                         for cat, states in self.category_indices.items()},
            "average_transitions": sum(s.total_count for s in self.states.values()) / max(len(self.states), 1)
        }


# ============================================================================
# ERWEITERTER MARKOV-TRAINER
# ============================================================================

class MarkovTrainer:
    """Trainiert und verwaltet Markov-Ketten für verschiedene Kontexte"""

    def __init__(self):
        self.chains: Dict[str, MarkovChain] = {
            "general": MarkovChain(order=2),
            "emotional": MarkovChain(order=2),
            "kemonomimi": MarkovChain(order=2),
        }
        self._trained = False

    def train_all(self):
        """Trainiert alle Ketten mit den Trainingsdaten"""
        if self._trained:
            return

        # Trainiere general chain mit allen Sätzen
        for category, sentences in TRAINING_SENTENCES.items():
            for sentence in sentences:
                self.chains["general"].train(sentence, category)

        # Trainiere emotional chain mit emotionalen Kategorien
        emotional_categories = [
            TrainingCategory.FREUDE,
            TrainingCategory.TRAUER,
            TrainingCategory.AUFREGUNG,
            TrainingCategory.ZUNEIGUNG,
            TrainingCategory.TROST,
            TrainingCategory.MOTIVATION,
        ]
        for category in emotional_categories:
            self.chains["emotional"].train_all(
                TRAINING_SENTENCES[category],
                category
            )

        # Trainiere kemonomimi chain
        self.chains["kemonomimi"].train_all(
            TRAINING_SENTENCES[TrainingCategory.KEMONOMIMI],
            TrainingCategory.KEMONOMIMI
        )

        self._trained = True

    def generate(
        self,
        chain_type: str = "general",
        category: Optional[TrainingCategory] = None,
        max_length: int = 50
    ) -> str:
        """Generiert einen Satz"""
        self.train_all()

        if chain_type not in self.chains:
            chain_type = "general"

        return self.chains[chain_type].generate(max_length, category)

    def generate_emotional(
        self,
        emotion: str,
        max_length: int = 50
    ) -> str:
        """Generiert einen emotional passenden Satz"""
        self.train_all()

        # Map emotion to category
        emotion_map = {
            "freude": TrainingCategory.FREUDE,
            "freudig": TrainingCategory.FREUDE,
            "trauer": TrainingCategory.TRAUER,
            "traurig": TrainingCategory.TRAUER,
            "aufregung": TrainingCategory.AUFREGUNG,
            "aufgeregt": TrainingCategory.AUFREGUNG,
            "zuneigung": TrainingCategory.ZUNEIGUNG,
            "liebevoll": TrainingCategory.ZUNEIGUNG,
            "trost": TrainingCategory.TROST,
            "motivation": TrainingCategory.MOTIVATION,
        }

        category = emotion_map.get(emotion.lower())
        return self.chains["emotional"].generate(max_length, category)

    def generate_kemonomimi(self, max_length: int = 50) -> str:
        """Generiert einen Kemonomimi-Satz"""
        self.train_all()
        return self.chains["kemonomimi"].generate(max_length, TrainingCategory.KEMONOMIMI)

    def get_statistics(self) -> Dict[str, Any]:
        """Gibt Statistiken über alle Ketten"""
        self.train_all()

        total_sentences = sum(
            len(sentences)
            for sentences in TRAINING_SENTENCES.values()
        )

        return {
            "total_training_sentences": total_sentences,
            "categories": len(TRAINING_SENTENCES),
            "chains": {
                name: chain.get_statistics()
                for name, chain in self.chains.items()
            }
        }


# ============================================================================
# GLOBALER ZUGRIFF
# ============================================================================

_trainer_instance: Optional[MarkovTrainer] = None


def get_markov_trainer() -> MarkovTrainer:
    """Gibt die globale Trainer-Instanz zurück"""
    global _trainer_instance
    if _trainer_instance is None:
        _trainer_instance = MarkovTrainer()
    return _trainer_instance


def get_training_sentences(category: Optional[str] = None) -> List[str]:
    """Gibt Trainingssätze zurück"""
    if category:
        try:
            cat = TrainingCategory(category)
            return TRAINING_SENTENCES.get(cat, [])
        except ValueError:
            return []
    return [s for sentences in TRAINING_SENTENCES.values() for s in sentences]


def count_training_sentences() -> Dict[str, int]:
    """Zählt die Trainingssätze pro Kategorie"""
    result = {}
    total = 0
    for category, sentences in TRAINING_SENTENCES.items():
        count = len(sentences)
        result[category.value] = count
        total += count
    result["total"] = total
    return result


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    # Zähle Sätze
    counts = count_training_sentences()
    print("=== Markov Training Statistiken ===")
    print(f"\nTrainingssätze pro Kategorie:")
    for category, count in counts.items():
        if category != "total":
            print(f"  {category}: {count}")
    print(f"\nGesamt: {counts['total']} Sätze")

    # Trainiere und teste
    trainer = get_markov_trainer()
    stats = trainer.get_statistics()
    print(f"\nKetten-Statistiken:")
    for chain_name, chain_stats in stats["chains"].items():
        print(f"  {chain_name}:")
        print(f"    States: {chain_stats['total_states']}")
        print(f"    Trainiert: {chain_stats['trained_sentences']}")

    print("\n=== Beispiel-Generierungen ===")
    print("\nGeneral:")
    for _ in range(3):
        print(f"  - {trainer.generate('general')}")

    print("\nEmotional (Freude):")
    for _ in range(3):
        print(f"  - {trainer.generate_emotional('freude')}")

    print("\nKemonomimi:")
    for _ in range(3):
        print(f"  - {trainer.generate_kemonomimi()}")
