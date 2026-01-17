#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOLO WEB CURIOSITY & CRITICAL THINKING v1.0
============================================
Holos eigene Neugier + kritisches Denken beim Web-Surfen.

FEATURES:
1. 🔍 Eigene Web-Suche wenn Holo neugierig ist
2. 🛡️ Misstrauen gegenüber dem Internet (Fake-Erkennung)
3. ✅ Verifizierung auf vertrauenswürdigen Quellen
4. 💡 Interessen-Entdeckung (wenn 2 Themen zusammenpassen)
5. 📚 Eigene Wissensdatenbank mit Vertrauenslevel

PHILOSOPHIE:
"Ich bin neugierig, aber nicht naiv.
 Ich prüfe was ich finde, bevor ich es glaube."
"""

import json
import random
import hashlib
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

logger = logging.getLogger("HoloWebCuriosity")

# Safe access helpers für Strict Mode
try:
    from holo_error_tracker import safe_list_access, safe_split_access, report_error
except ImportError:
    def safe_list_access(lst, index, module, function, default=None, context=""):
        if not lst or len(lst) <= abs(index):
            return default
        return lst[index]
    def safe_split_access(text, sep, index, module, function, default="", context=""):
        parts = text.split(sep) if text else []
        if len(parts) <= abs(index):
            return default
        return parts[index]
    def report_error(e, module="", function="", context="", severity=None, fallback_value=None):
        return fallback_value


# =============================================================================
# CONFIGURATION
# =============================================================================

class WebCuriosityConfig:
    """Konfiguration für Web-Neugier"""

    # Vertrauenslevel
    MIN_TRUST_FOR_BELIEF = 0.6      # Ab diesem Trust-Level "glaubt" Holo etwas
    VERIFICATION_BOOST = 0.2         # Boost wenn verifiziert
    UNVERIFIED_PENALTY = -0.1        # Penalty wenn nicht verifizierbar

    # Suche
    MAX_SEARCH_RESULTS = 10
    SEARCH_COOLDOWN_SECONDS = 60     # Nicht zu oft suchen

    # Interessen-Entdeckung
    MIN_TOPIC_OVERLAP = 2            # Mindestens 2 gemeinsame Konzepte
    DISCOVERY_THRESHOLD = 0.6        # Ab wann wird neues Interesse erstellt

    # Fakten-Speicherung
    MAX_FACTS_PER_TOPIC = 100
    FACT_DECAY_DAYS = 90             # Nach 90 Tagen sinkt Vertrauen


# =============================================================================
# ENUMS
# =============================================================================

class TrustLevel(Enum):
    """Vertrauenslevel für Quellen"""
    OFFICIAL = 1.0          # Offizielle Quellen (Regierung, Universitäten)
    REPUTABLE = 0.85        # Seriöse Medien (etablierte Zeitungen)
    KNOWN = 0.7             # Bekannte Seiten
    NEUTRAL = 0.5           # Unbekannt, neutral
    SUSPICIOUS = 0.3        # Verdächtig
    UNTRUSTED = 0.1         # Nicht vertrauenswürdig
    FAKE = 0.0              # Bekannte Fake-Seite


class FactStatus(Enum):
    """Status eines Fakts"""
    VERIFIED = "verified"           # Auf mehreren Quellen bestätigt
    LIKELY_TRUE = "likely_true"     # Wahrscheinlich wahr
    UNVERIFIED = "unverified"       # Noch nicht geprüft
    DISPUTED = "disputed"           # Widersprüchliche Infos
    LIKELY_FALSE = "likely_false"   # Wahrscheinlich falsch
    DEBUNKED = "debunked"           # Als falsch entlarvt


class SearchIntent(Enum):
    """Warum sucht Holo?"""
    CURIOSITY = "curiosity"         # Reine Neugier
    VERIFICATION = "verification"   # Etwas überprüfen
    LEARNING = "learning"           # Etwas lernen
    USER_REQUEST = "user_request"   # User hat gefragt
    FOLLOW_UP = "follow_up"         # Weiterführende Frage


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class TrustedSource:
    """Eine vertrauenswürdige Quelle"""
    domain: str
    trust_level: TrustLevel
    category: str                   # "news", "academic", "government", "wiki"
    language: str = "de"
    notes: str = ""


@dataclass
class WebFact:
    """Ein Fakt den Holo im Web gefunden hat"""
    fact_id: str
    content: str                    # Der Fakt selbst
    topic: str                      # Hauptthema
    related_topics: List[str]       # Verwandte Themen

    # Quellen
    sources: List[str] = field(default_factory=list)  # URLs
    source_trust_scores: List[float] = field(default_factory=list)

    # Vertrauen
    trust_score: float = 0.5        # 0-1, wie sehr Holo das glaubt
    status: FactStatus = FactStatus.UNVERIFIED
    verification_attempts: int = 0

    # Meta
    discovered_at: str = ""
    last_verified: str = ""
    times_encountered: int = 1

    def calculate_trust(self) -> float:
        """Berechnet Vertrauensscore basierend auf Quellen"""
        if not self.source_trust_scores:
            return 0.3  # Unbekannte Quelle = niedriges Vertrauen

        # Gewichteter Durchschnitt + Bonus für mehrere Quellen
        avg_trust = sum(self.source_trust_scores) / len(self.source_trust_scores)
        multi_source_bonus = min(0.2, 0.05 * (len(self.sources) - 1))

        return min(1.0, avg_trust + multi_source_bonus)


@dataclass
class DiscoveredInterest:
    """Ein neu entdecktes Interesse durch Themen-Kombination"""
    interest_id: str
    name: str                       # z.B. "Quantenbiologie"
    parent_topics: List[str]        # z.B. ["quantenphysik", "biologie"]
    description: str                # Warum interessant

    # Entstehung
    discovered_at: str = ""
    trigger_fact: str = ""          # Welcher Fakt hat das ausgelöst

    # Entwicklung
    interest_level: float = 0.6     # Startet bei 60%
    facts_collected: int = 0
    exploration_count: int = 0

    def __post_init__(self):
        if not self.discovered_at:
            self.discovered_at = datetime.now().isoformat()


@dataclass
class SearchQuery:
    """Eine Suchanfrage von Holo"""
    query_id: str
    query: str
    intent: SearchIntent
    topics: List[str]

    # Ergebnisse
    results_count: int = 0
    facts_extracted: int = 0
    new_interests_discovered: int = 0

    # Meta
    timestamp: str = ""
    was_successful: bool = False


# =============================================================================
# TRUSTED SOURCES DATABASE
# =============================================================================

class TrustedSourcesDB:
    """
    Datenbank vertrauenswürdiger Quellen.

    Holo weiß welchen Seiten sie vertrauen kann!
    """

    # Vordefinierte vertrauenswürdige Quellen
    TRUSTED_SOURCES = {
        # === OFFIZIELLE QUELLEN (1.0) ===
        "bundesregierung.de": TrustedSource("bundesregierung.de", TrustLevel.OFFICIAL, "government"),
        "europa.eu": TrustedSource("europa.eu", TrustLevel.OFFICIAL, "government"),
        "who.int": TrustedSource("who.int", TrustLevel.OFFICIAL, "government"),
        "nasa.gov": TrustedSource("nasa.gov", TrustLevel.OFFICIAL, "government"),
        "esa.int": TrustedSource("esa.int", TrustLevel.OFFICIAL, "government"),
        "dlr.de": TrustedSource("dlr.de", TrustLevel.OFFICIAL, "government"),

        # === AKADEMISCH (0.9) ===
        "nature.com": TrustedSource("nature.com", TrustLevel.OFFICIAL, "academic"),
        "science.org": TrustedSource("science.org", TrustLevel.OFFICIAL, "academic"),
        "arxiv.org": TrustedSource("arxiv.org", TrustLevel.OFFICIAL, "academic"),
        "pubmed.ncbi.nlm.nih.gov": TrustedSource("pubmed.ncbi.nlm.nih.gov", TrustLevel.OFFICIAL, "academic"),
        "springer.com": TrustedSource("springer.com", TrustLevel.OFFICIAL, "academic"),

        # === SERIÖSE MEDIEN (0.85) ===
        "tagesschau.de": TrustedSource("tagesschau.de", TrustLevel.REPUTABLE, "news"),
        "zeit.de": TrustedSource("zeit.de", TrustLevel.REPUTABLE, "news"),
        "spiegel.de": TrustedSource("spiegel.de", TrustLevel.REPUTABLE, "news"),
        "sueddeutsche.de": TrustedSource("sueddeutsche.de", TrustLevel.REPUTABLE, "news"),
        "faz.net": TrustedSource("faz.net", TrustLevel.REPUTABLE, "news"),
        "heise.de": TrustedSource("heise.de", TrustLevel.REPUTABLE, "news", notes="Technik"),
        "golem.de": TrustedSource("golem.de", TrustLevel.REPUTABLE, "news", notes="Technik"),
        "reuters.com": TrustedSource("reuters.com", TrustLevel.REPUTABLE, "news"),
        "apnews.com": TrustedSource("apnews.com", TrustLevel.REPUTABLE, "news"),
        "bbc.com": TrustedSource("bbc.com", TrustLevel.REPUTABLE, "news", language="en"),
        "theguardian.com": TrustedSource("theguardian.com", TrustLevel.REPUTABLE, "news", language="en"),

        # === BEKANNTE SEITEN (0.7) ===
        "wikipedia.org": TrustedSource("wikipedia.org", TrustLevel.KNOWN, "wiki", notes="Gut für Überblick, aber prüfen"),
        "stackoverflow.com": TrustedSource("stackoverflow.com", TrustLevel.KNOWN, "tech"),
        "github.com": TrustedSource("github.com", TrustLevel.KNOWN, "tech"),
        "youtube.com": TrustedSource("youtube.com", TrustLevel.NEUTRAL, "video", notes="Sehr unterschiedliche Qualität"),

        # === VERDÄCHTIGE SEITEN (0.3) ===
        # Diese werden dynamisch hinzugefügt wenn Holo lernt
    }

    # Muster für verdächtige URLs
    SUSPICIOUS_PATTERNS = [
        r".*fake.*news.*",
        r".*conspiracy.*",
        r".*truth.*reveal.*",
        r".*secret.*exposed.*",
        r".*mainstream.*media.*lies.*",
        r".*they.*dont.*want.*you.*know.*",
    ]

    # Bekannte Fake-Domains (Beispiele)
    KNOWN_FAKE_DOMAINS = {
        # Hier könnten bekannte Fake-News Seiten stehen
        # Leer gelassen da sich das ändert
    }

    def __init__(self, custom_sources_path: Path = None):
        self.sources = dict(self.TRUSTED_SOURCES)
        self.custom_path = custom_sources_path
        self._load_custom()

    def _load_custom(self):
        """Lädt benutzerdefinierte Quellen"""
        if self.custom_path and self.custom_path.exists():
            try:
                data = json.loads(self.custom_path.read_text())
                for domain, info in data.items():
                    self.sources[domain] = TrustedSource(
                        domain=domain,
                        trust_level=TrustLevel(info.get("trust_level", 0.5)),
                        category=info.get("category", "unknown"),
                        notes=info.get("notes", "")
                    )
            except Exception as e:
                logger.warning(f"Could not load custom sources: {e}")

    def get_trust_score(self, url: str) -> Tuple[float, str]:
        """
        Gibt Trust-Score und Begründung für eine URL.

        Returns:
            (trust_score, reason)
        """
        # Domain extrahieren
        domain = self._extract_domain(url)

        # Bekannte Quelle?
        if domain in self.sources:
            source = self.sources[domain]
            return source.trust_level.value, f"Bekannte Quelle: {source.category}"

        # Bekannte Fake-Domain?
        if domain in self.KNOWN_FAKE_DOMAINS:
            return 0.0, "Bekannte Fake-News Seite"

        # Verdächtige Muster in URL?
        url_lower = url.lower()
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.match(pattern, url_lower):
                return 0.2, "Verdächtiges URL-Muster"

        # Unbekannt = neutral mit Vorsicht
        return 0.4, "Unbekannte Quelle - mit Vorsicht genießen"

    def _extract_domain(self, url: str) -> str:
        """Extrahiert Domain aus URL"""
        # Einfache Extraktion
        url = url.lower()
        url = url.replace("https://", "").replace("http://", "")
        url = url.replace("www.", "")
        domain = safe_split_access(url, "/", 0, "web_curiosity", "_extract_domain", default="unknown")
        return domain

    def is_verification_source(self, url: str) -> bool:
        """Ist diese URL gut zum Verifizieren?"""
        domain = self._extract_domain(url)
        if domain in self.sources:
            source = self.sources[domain]
            return source.trust_level.value >= 0.7
        return False

    def get_verification_sources(self, topic: str) -> List[str]:
        """Gibt gute Quellen zum Verifizieren eines Themas"""
        suggestions = []

        # Akademische Quellen für Wissenschaft
        if topic in ["wissenschaft", "forschung", "studie", "medizin"]:
            suggestions.extend([
                "https://scholar.google.com",
                "https://pubmed.ncbi.nlm.nih.gov",
                "https://www.nature.com"
            ])

        # News-Quellen für aktuelle Ereignisse
        if topic in ["politik", "welt", "wirtschaft", "news"]:
            suggestions.extend([
                "https://www.tagesschau.de",
                "https://www.reuters.com",
                "https://apnews.com"
            ])

        # Technik
        if topic in ["technik", "technologie", "software", "hardware"]:
            suggestions.extend([
                "https://www.heise.de",
                "https://www.golem.de"
            ])

        # Wikipedia als Überblick
        suggestions.append(f"https://de.wikipedia.org/wiki/{topic}")

        return suggestions[:5]


# =============================================================================
# FACT VERIFICATION ENGINE
# =============================================================================

class FactVerificationEngine:
    """
    Holos Fakten-Prüfungs-System.

    "Stimmt das wirklich? Lass mich nachschauen..."
    """

    # Skeptische Gedanken
    SKEPTICAL_THOUGHTS = [
        "Hmm, das klingt zu gut um wahr zu sein...",
        "Moment, das sollte ich lieber nochmal prüfen.",
        "Eine Quelle reicht mir nicht. Wo steht das noch?",
        "Das widerspricht dem was ich vorher gelesen habe...",
        "Klingt interessant, aber ist das auch belegt?",
        "Wer hat das geschrieben und warum?",
    ]

    # Verifikations-Ergebnisse
    VERIFICATION_RESPONSES = {
        FactStatus.VERIFIED: [
            "Ja, das stimmt! Mehrere seriöse Quellen bestätigen das.",
            "Das habe ich verifiziert - scheint korrekt zu sein.",
            "Stimmt! Ich habe das auf {sources} gefunden.",
        ],
        FactStatus.LIKELY_TRUE: [
            "Das scheint zu stimmen, aber ich bin nicht 100% sicher.",
            "Wahrscheinlich korrekt - eine seriöse Quelle sagt das.",
            "Sieht gut aus, aber mehr Quellen wären besser.",
        ],
        FactStatus.DISPUTED: [
            "Hmm, da gibt es unterschiedliche Meinungen...",
            "Das ist umstritten - manche Quellen sagen ja, andere nein.",
            "Schwierig zu sagen - die Experten sind sich nicht einig.",
        ],
        FactStatus.LIKELY_FALSE: [
            "Das stimmt wahrscheinlich nicht. Ich finde keine Bestätigung.",
            "Vorsicht! Das sieht nach Fehlinformation aus.",
            "Ich bin skeptisch - keine seriöse Quelle bestätigt das.",
        ],
        FactStatus.DEBUNKED: [
            "Das ist falsch! Das wurde bereits widerlegt.",
            "Nein, das stimmt nicht. {reason}",
            "Vorsicht, Fake! Hier ist warum: {reason}",
        ],
    }

    def __init__(self, trusted_sources: TrustedSourcesDB):
        self.trusted_sources = trusted_sources
        self.verification_cache: Dict[str, WebFact] = {}

    def should_verify(self, content: str, source_trust: float) -> Tuple[bool, str]:
        """
        Entscheidet ob etwas verifiziert werden sollte.

        Returns:
            (should_verify, reason)
        """
        # Niedrige Quelle = immer verifizieren
        if source_trust < 0.5:
            return True, "Quelle nicht sehr vertrauenswürdig"

        # Starke Behauptungen
        strong_claim_indicators = [
            "erstmals", "durchbruch", "revolution", "sensation",
            "alle", "niemand", "immer", "nie", "bewiesen",
            "geheim", "verschwiegen", "enthüllt"
        ]

        content_lower = content.lower()
        for indicator in strong_claim_indicators:
            if indicator in content_lower:
                return True, f"Starke Behauptung ('{indicator}')"

        # Kontroverse Themen
        controversial_topics = [
            "impfung", "klima", "politik", "verschwörung",
            "corona", "covid", "migration"
        ]

        for topic in controversial_topics:
            if topic in content_lower:
                return True, f"Kontroverses Thema ({topic})"

        # Hohe Quelle = nicht unbedingt verifizieren
        if source_trust >= 0.8:
            return False, "Vertrauenswürdige Quelle"

        # Default: Bei Unsicherheit lieber prüfen
        return random.random() > 0.5, "Stichprobe"

    def get_skeptical_thought(self) -> str:
        """Gibt einen skeptischen Gedanken zurück"""
        return random.choice(self.SKEPTICAL_THOUGHTS)

    def express_verification_result(self, fact: WebFact) -> str:
        """Drückt das Verifikationsergebnis natürlich aus"""
        templates = self.VERIFICATION_RESPONSES.get(fact.status, ["Ich bin mir unsicher."])
        response = random.choice(templates)

        # Platzhalter ersetzen
        if "{sources}" in response and fact.sources:
            sources_str = ", ".join(fact.sources[:2])
            response = response.replace("{sources}", sources_str)

        return response

    def calculate_fact_status(self, fact: WebFact) -> FactStatus:
        """Berechnet den Status eines Fakts basierend auf Quellen"""
        if not fact.sources:
            return FactStatus.UNVERIFIED

        trust = fact.calculate_trust()
        num_sources = len(fact.sources)

        # Mehrere vertrauenswürdige Quellen = verifiziert
        if trust >= 0.8 and num_sources >= 2:
            return FactStatus.VERIFIED

        # Eine gute Quelle = wahrscheinlich wahr
        if trust >= 0.7:
            return FactStatus.LIKELY_TRUE

        # Mittleres Vertrauen = ungeprüft
        if trust >= 0.4:
            return FactStatus.UNVERIFIED

        # Niedriges Vertrauen = verdächtig
        if trust >= 0.2:
            return FactStatus.LIKELY_FALSE

        # Sehr niedrig = wahrscheinlich falsch
        return FactStatus.DEBUNKED


# =============================================================================
# INTEREST DISCOVERY ENGINE
# =============================================================================

class InterestDiscoveryEngine:
    """
    Entdeckt neue Interessen wenn Themen sich überschneiden.

    "Oh, Quantenphysik und Biologie zusammen? Das ist ja Quantenbiologie!"
    """

    # Bekannte Überschneidungen die interessant sind
    KNOWN_INTERSECTIONS = {
        ("quantenphysik", "biologie"): "Quantenbiologie",
        ("quantenphysik", "computer"): "Quantencomputing",
        ("ki", "kunst"): "KI-generierte Kunst",
        ("ki", "musik"): "KI-Musik",
        ("biologie", "technologie"): "Biotechnologie",
        ("gehirn", "computer"): "Neuroinformatik",
        ("psychologie", "wirtschaft"): "Verhaltensökonomie",
        ("astronomie", "biologie"): "Astrobiologie",
        ("musik", "mathematik"): "Musiktheorie",
        ("sprache", "ki"): "Natural Language Processing",
        ("ethik", "ki"): "KI-Ethik",
        ("philosophie", "physik"): "Philosophie der Physik",
    }

    # Konzepte die Themen verbinden
    BRIDGE_CONCEPTS = {
        "evolution": ["biologie", "psychologie", "gesellschaft"],
        "information": ["physik", "biologie", "computer"],
        "komplexität": ["mathematik", "biologie", "gesellschaft"],
        "emergenz": ["physik", "biologie", "bewusstsein"],
        "netzwerk": ["computer", "biologie", "gesellschaft"],
    }

    def __init__(self, db_path: Path = None, db: 'HoloDatabaseManager' = None):
        self.db = db  # HoloDatabaseManager für zentrale Speicherung
        self.db_path = db_path or Path("data/discovered_interests.json")
        self.discovered: Dict[str, DiscoveredInterest] = {}
        self._load()

    def connect_database(self, db: 'HoloDatabaseManager'):
        """Verbindet mit HoloDatabaseManager für persistente Speicherung"""
        self.db = db
        self._load()

    def _load(self):
        """Lädt entdeckte Interessen aus HoloDatabaseManager"""
        try:
            if self.db:
                data = self.db.state.get_state('discovered_interests')
                if data:
                    for interest_id, info in data.items():
                        self.discovered[interest_id] = DiscoveredInterest(
                            interest_id=interest_id,
                            name=info["name"],
                            parent_topics=info["parent_topics"],
                            description=info.get("description", ""),
                            discovered_at=info.get("discovered_at", ""),
                            trigger_fact=info.get("trigger_fact", ""),
                            interest_level=info.get("interest_level", 0.6),
                            facts_collected=info.get("facts_collected", 0),
                            exploration_count=info.get("exploration_count", 0)
                        )
        except Exception as e:
            logger.warning(f"Could not load discovered interests: {e}")

    def _save(self):
        """Speichert entdeckte Interessen in HoloDatabaseManager"""
        if not self.db:
            return
        try:
            data = {
                iid: {
                    "name": i.name,
                    "parent_topics": i.parent_topics,
                    "description": i.description,
                    "discovered_at": i.discovered_at,
                    "trigger_fact": i.trigger_fact,
                    "interest_level": i.interest_level,
                    "facts_collected": i.facts_collected,
                    "exploration_count": i.exploration_count
                }
                for iid, i in self.discovered.items()
            }
            self.db.state.save_state('discovered_interests', data)
        except Exception as e:
            logger.error(f"Could not save discovered interests: {e}")

    def check_for_discovery(self, topics: List[str],
                            fact_content: str = "") -> Optional[DiscoveredInterest]:
        """
        Prüft ob eine Themen-Kombination ein neues Interesse ergibt.

        Returns:
            DiscoveredInterest wenn neu entdeckt, sonst None
        """
        if len(topics) < 2:
            return None

        # Prüfe bekannte Überschneidungen
        for i, topic1 in enumerate(topics):
            for topic2 in topics[i+1:]:
                # Beide Richtungen prüfen
                key1 = (topic1.lower(), topic2.lower())
                key2 = (topic2.lower(), topic1.lower())

                intersection_name = self.KNOWN_INTERSECTIONS.get(key1) or \
                                   self.KNOWN_INTERSECTIONS.get(key2)

                if intersection_name:
                    # Schon entdeckt?
                    interest_id = f"discovered_{topic1}_{topic2}"
                    if interest_id in self.discovered:
                        # Interesse verstärken
                        self.discovered[interest_id].interest_level = min(
                            1.0,
                            self.discovered[interest_id].interest_level + 0.05
                        )
                        self.discovered[interest_id].facts_collected += 1
                        self._save()
                        return None

                    # Neu entdecken!
                    new_interest = DiscoveredInterest(
                        interest_id=interest_id,
                        name=intersection_name,
                        parent_topics=[topic1, topic2],
                        description=f"Spannende Verbindung zwischen {topic1} und {topic2}!",
                        trigger_fact=fact_content[:200] if fact_content else "",
                        interest_level=0.7
                    )

                    self.discovered[interest_id] = new_interest
                    self._save()

                    logger.info(f"[DISCOVERY] Neues Interesse entdeckt: {intersection_name}")
                    return new_interest

        # Prüfe Bridge-Konzepte
        for bridge, connected_topics in self.BRIDGE_CONCEPTS.items():
            matching = [t for t in topics if t.lower() in connected_topics]
            if len(matching) >= 2:
                interest_id = f"bridge_{bridge}_{'_'.join(sorted(matching))}"
                if interest_id not in self.discovered:
                    new_interest = DiscoveredInterest(
                        interest_id=interest_id,
                        name=f"{bridge.title()} in {' & '.join(matching)}",
                        parent_topics=matching,
                        description=f"Das Konzept '{bridge}' verbindet diese Themen!",
                        trigger_fact=fact_content[:200] if fact_content else "",
                        interest_level=0.6
                    )

                    self.discovered[interest_id] = new_interest
                    self._save()
                    return new_interest

        return None

    def express_discovery(self, interest: DiscoveredInterest) -> str:
        """Drückt die Entdeckung natürlich aus"""
        expressions = [
            f"Oh! 💡 {interest.name}! Das ist ja spannend - {interest.parent_topics[0]} "
            f"und {interest.parent_topics[1]} hängen zusammen!",

            f"Moment... *schaut aufmerksam* {interest.name}? Das muss ich mir merken!",

            f"Interessant! Ich hab gerade was entdeckt: {interest.name}. "
            f"Die Verbindung zwischen {interest.parent_topics[0]} und {interest.parent_topics[1]} "
            f"fasziniert mich!",

            f"🌟 Neues Interesse: {interest.name}! Das will ich mehr erkunden.",
        ]

        return random.choice(expressions)

    def get_discovery_suggestions(self, current_topics: List[str]) -> List[str]:
        """Gibt Vorschläge was Holo als nächstes erkunden könnte"""
        suggestions = []

        for topic in current_topics:
            for (t1, t2), name in self.KNOWN_INTERSECTIONS.items():
                if topic.lower() == t1:
                    suggestions.append(f"Was wenn ich {topic} mit {t2} verbinde? → {name}")
                elif topic.lower() == t2:
                    suggestions.append(f"Was wenn ich {topic} mit {t1} verbinde? → {name}")

        return suggestions[:3]

    def get_all_discovered(self) -> List[DiscoveredInterest]:
        """Gibt alle entdeckten Interessen zurück"""
        return sorted(
            self.discovered.values(),
            key=lambda x: x.interest_level,
            reverse=True
        )


# =============================================================================
# WEB FACTS DATABASE
# =============================================================================

class WebFactsDB:
    """
    Holos eigene Wissensdatenbank mit Fakten aus dem Web.

    Jeder Fakt hat ein Vertrauenslevel!
    """

    def __init__(self, db_path: Path = None, db: 'HoloDatabaseManager' = None):
        self.db = db  # HoloDatabaseManager für zentrale Speicherung
        self.db_path = db_path or Path("data/holo_web_facts.json")
        self.facts: Dict[str, WebFact] = {}
        self.facts_by_topic: Dict[str, List[str]] = defaultdict(list)
        self._load()

    def connect_database(self, db: 'HoloDatabaseManager'):
        """Verbindet mit HoloDatabaseManager für persistente Speicherung"""
        self.db = db
        self._load()

    def _load(self):
        """Lädt Fakten aus HoloDatabaseManager"""
        try:
            if self.db:
                data = self.db.state.get_state('web_facts')
                if data:
                    for fact_id, info in data.get("facts", {}).items():
                        fact = WebFact(
                            fact_id=fact_id,
                            content=info["content"],
                            topic=info["topic"],
                            related_topics=info.get("related_topics", []),
                            sources=info.get("sources", []),
                            source_trust_scores=info.get("source_trust_scores", []),
                            trust_score=info.get("trust_score", 0.5),
                            status=FactStatus(info.get("status", "unverified")),
                            verification_attempts=info.get("verification_attempts", 0),
                            discovered_at=info.get("discovered_at", ""),
                            last_verified=info.get("last_verified", ""),
                            times_encountered=info.get("times_encountered", 1)
                        )
                        self.facts[fact_id] = fact
                        self.facts_by_topic[fact.topic].append(fact_id)
                    logger.info(f"[FACTS] Loaded {len(self.facts)} facts from DB")
        except Exception as e:
            logger.warning(f"Could not load facts: {e}")

    def _save(self):
        """Speichert Fakten in HoloDatabaseManager"""
        if not self.db:
            return
        try:
            data = {
                "facts": {
                    fid: {
                        "content": f.content,
                        "topic": f.topic,
                        "related_topics": f.related_topics,
                        "sources": f.sources,
                        "source_trust_scores": f.source_trust_scores,
                        "trust_score": f.trust_score,
                        "status": f.status.value,
                        "verification_attempts": f.verification_attempts,
                        "discovered_at": f.discovered_at,
                        "last_verified": f.last_verified,
                        "times_encountered": f.times_encountered
                    }
                    for fid, f in self.facts.items()
                },
                "last_updated": datetime.now().isoformat()
            }
            self.db.state.save_state('web_facts', data)
        except Exception as e:
            logger.error(f"Could not save facts: {e}")

    def add_fact(self, content: str, topic: str, source_url: str,
                 source_trust: float, related_topics: List[str] = None) -> WebFact:
        """Fügt einen neuen Fakt hinzu"""
        # ID aus Content-Hash
        fact_id = hashlib.md5(content.encode()).hexdigest()[:12]

        # Existiert schon?
        if fact_id in self.facts:
            existing = self.facts[fact_id]
            existing.times_encountered += 1
            if source_url not in existing.sources:
                existing.sources.append(source_url)
                existing.source_trust_scores.append(source_trust)
                existing.trust_score = existing.calculate_trust()
            self._save()
            return existing

        # Neu erstellen
        fact = WebFact(
            fact_id=fact_id,
            content=content,
            topic=topic,
            related_topics=related_topics or [],
            sources=[source_url],
            source_trust_scores=[source_trust],
            trust_score=source_trust,
            discovered_at=datetime.now().isoformat()
        )

        self.facts[fact_id] = fact
        self.facts_by_topic[topic].append(fact_id)

        # Limit pro Topic
        if len(self.facts_by_topic[topic]) > WebCuriosityConfig.MAX_FACTS_PER_TOPIC:
            # Älteste mit niedrigstem Trust entfernen
            oldest_id = self.facts_by_topic[topic][0]
            del self.facts[oldest_id]
            self.facts_by_topic[topic].pop(0)

        self._save()
        return fact

    def get_facts_by_topic(self, topic: str, min_trust: float = 0.0) -> List[WebFact]:
        """Holt Fakten zu einem Thema"""
        fact_ids = self.facts_by_topic.get(topic, [])
        facts = [self.facts[fid] for fid in fact_ids if fid in self.facts]

        if min_trust > 0:
            facts = [f for f in facts if f.trust_score >= min_trust]

        return sorted(facts, key=lambda x: x.trust_score, reverse=True)

    def get_verified_facts(self, topic: str = None) -> List[WebFact]:
        """Holt nur verifizierte Fakten"""
        if topic:
            facts = self.get_facts_by_topic(topic)
        else:
            facts = list(self.facts.values())

        return [f for f in facts if f.status == FactStatus.VERIFIED]

    def search_facts(self, query: str) -> List[WebFact]:
        """Durchsucht Fakten"""
        query_lower = query.lower()
        results = []

        for fact in self.facts.values():
            if query_lower in fact.content.lower():
                results.append(fact)
            elif any(query_lower in t.lower() for t in [fact.topic] + fact.related_topics):
                results.append(fact)

        return sorted(results, key=lambda x: x.trust_score, reverse=True)[:10]


# =============================================================================
# MAIN CLASS: HOLO WEB CURIOSITY
# =============================================================================

class HoloWebCuriosity:
    """
    Holos Web-Neugier-System.

    Kombiniert:
    - Kritisches Denken bei Web-Inhalten
    - Vertrauenswürdige Quellen
    - Fakten-Verifizierung
    - Interessen-Entdeckung
    - Eigene Wissensdatenbank
    
    Verbindungen zu anderen Modulen:
    - learning: Meldet interessante Entdeckungen als Lerngelegenheit
    - consciousness: Teilt Neugier-Gedanken mit
    """

    def __init__(self, data_dir: Path = None, db: 'HoloDatabaseManager' = None):
        self.db = db  # HoloDatabaseManager für zentrale Speicherung
        self.data_dir = data_dir or Path("data/web_curiosity")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # === VERBINDUNGEN ZU ANDEREN MODULEN ===
        # Werden von holo_brain._connect_all_cognitive_modules() gesetzt
        self.learning = None           # AdvancedLearningEngine
        self.consciousness = None      # ConsciousnessEngine
        self.drive_system = None       # HoloDriveSystem - Neugier befriedigen

        # Komponenten - nutzen jetzt HoloDatabaseManager
        self.trusted_sources = TrustedSourcesDB(
            self.data_dir / "custom_sources.json"
        )
        self.verifier = FactVerificationEngine(self.trusted_sources)
        self.discovery = InterestDiscoveryEngine(db=db)
        self.facts_db = WebFactsDB(db=db)

        # Search-Tracking
        self.search_history: List[SearchQuery] = []
        self.last_search_time: Optional[datetime] = None
        self.last_search: Optional[str] = None         # Letzte Suchanfrage
        self.last_results: List[Dict] = []             # Letzte Ergebnisse
        self.is_searching: bool = False                # Gerade am Suchen?
        self.facts_learned: int = 0                    # Gelernte Fakten insgesamt

        logger.info("🔍 HoloWebCuriosity initialisiert (mit Web-Suche)")

    def connect_database(self, db: 'HoloDatabaseManager'):
        """Verbindet mit HoloDatabaseManager für persistente Speicherung"""
        self.db = db
        self.discovery.connect_database(db)
        self.facts_db.connect_database(db)

    # =========================================================================
    # KRITISCHES DENKEN
    # =========================================================================

    def evaluate_source(self, url: str) -> Dict:
        """
        Bewertet eine Quelle kritisch.

        Returns:
            Dict mit trust_score, is_trustworthy, reason, suggestions
        """
        trust_score, reason = self.trusted_sources.get_trust_score(url)

        return {
            "url": url,
            "trust_score": trust_score,
            "is_trustworthy": trust_score >= 0.6,
            "reason": reason,
            "should_verify": trust_score < 0.7,
            "skeptical_thought": self.verifier.get_skeptical_thought() if trust_score < 0.7 else None
        }

    def evaluate_content(self, content: str, source_url: str,
                        topics: List[str] = None) -> Dict:
        """
        Bewertet einen Inhalt kritisch.

        Returns:
            Dict mit allen Bewertungen
        """
        # Quellen-Vertrauen
        source_trust, source_reason = self.trusted_sources.get_trust_score(source_url)

        # Soll verifiziert werden?
        should_verify, verify_reason = self.verifier.should_verify(content, source_trust)

        # Themen prüfen
        topics = topics or []
        discovered_interest = self.discovery.check_for_discovery(topics, content)

        # === VERBUNDENE MODULE INFORMIEREN ===
        if discovered_interest:
            self._notify_discovery(discovered_interest, content, topics)

        # Ergebnis
        result = {
            "content_preview": content[:200] + "..." if len(content) > 200 else content,
            "source": {
                "url": source_url,
                "trust_score": source_trust,
                "reason": source_reason
            },
            "should_verify": should_verify,
            "verify_reason": verify_reason,
            "topics": topics,
            "new_interest_discovered": discovered_interest.name if discovered_interest else None,
            "holos_thought": self._generate_evaluation_thought(
                source_trust, should_verify, discovered_interest
            )
        }

        return result

    def _notify_discovery(self, discovery, content: str, topics: List[str]):
        """Informiert verbundene Module über eine Entdeckung"""
        try:
            # Learning über interessantes Thema informieren
            if self.learning and hasattr(self.learning, 'register_learning_opportunity'):
                self.learning.register_learning_opportunity(
                    source="web_curiosity",
                    content=f"Neues Interesse entdeckt: {discovery.name}. "
                            f"Themen: {', '.join(topics[:3])}. "
                            f"Kontext: {content[:200]}",
                    importance=0.7
                )

            # Consciousness über Neugier-Moment informieren
            if self.consciousness:
                self.consciousness.think(
                    trigger=f"Wie interessant! Ich habe etwas über {discovery.name} entdeckt!",
                    context={
                        "discovery": discovery.name,
                        "topics": topics,
                        "source": "web_curiosity"
                    }
                )

            # DriveSystem: Neugier befriedigen!
            if self.drive_system and hasattr(self.drive_system, 'drives'):
                # Entdeckung befriedigt Neugier (drain = verbrauchen/befriedigen)
                self.drive_system.drives.drain('curiosity', 0.15)
                logger.debug(f"[WEBCURIOSITY] Neugier befriedigt durch Entdeckung: {discovery.name}")

        except Exception as e:
            logger.debug(f"[WEBCURIOSITY] Notification failed: {e}")

    def _generate_evaluation_thought(self, trust: float, should_verify: bool,
                                     discovery: Optional[DiscoveredInterest]) -> str:
        """Generiert Holos Gedanken zur Bewertung"""
        thoughts = []

        # Über Vertrauen
        if trust >= 0.8:
            thoughts.append("Die Quelle ist vertrauenswürdig.")
        elif trust >= 0.5:
            thoughts.append("Hmm, die Quelle ist okay, aber ich bleibe vorsichtig.")
        else:
            thoughts.append(self.verifier.get_skeptical_thought())

        # Über Verifizierung
        if should_verify:
            thoughts.append("Das sollte ich auf anderen Seiten nachprüfen.")

        # Über Entdeckung
        if discovery:
            thoughts.append(f"Oh! {discovery.name} - das ist ein interessantes neues Thema!")

        return " ".join(thoughts)

    # =========================================================================
    # FAKTEN-MANAGEMENT
    # =========================================================================

    def learn_fact(self, content: str, topic: str, source_url: str,
                   related_topics: List[str] = None) -> Dict:
        """
        Lernt einen neuen Fakt.

        Returns:
            Dict mit fact_id, trust_score, status, holos_response
        """
        # Quellen-Vertrauen
        source_trust, _ = self.trusted_sources.get_trust_score(source_url)

        # Fakt speichern
        fact = self.facts_db.add_fact(
            content=content,
            topic=topic,
            source_url=source_url,
            source_trust=source_trust,
            related_topics=related_topics
        )

        # Status berechnen
        fact.status = self.verifier.calculate_fact_status(fact)

        # Interesse prüfen
        all_topics = [topic] + (related_topics or [])
        discovery = self.discovery.check_for_discovery(all_topics, content)

        # Antwort generieren
        if fact.times_encountered > 1:
            response = f"Das habe ich schon mal gehört. Jetzt von {len(fact.sources)} Quellen bestätigt."
        elif fact.status == FactStatus.VERIFIED:
            response = "Das ist gut belegt. Ich merke mir das."
        elif source_trust >= 0.7:
            response = "Interessant! Die Quelle ist seriös, ich vertraue dem erstmal."
        else:
            response = f"Hmm, interessant... aber {self.verifier.get_skeptical_thought()}"

        if discovery:
            response += f" {self.discovery.express_discovery(discovery)}"

        return {
            "fact_id": fact.fact_id,
            "trust_score": fact.trust_score,
            "status": fact.status.value,
            "is_new": fact.times_encountered == 1,
            "sources_count": len(fact.sources),
            "new_interest": discovery.name if discovery else None,
            "holos_response": response
        }

    def what_do_i_know(self, topic: str) -> Dict:
        """
        Was weiß Holo über ein Thema?

        Returns:
            Dict mit facts, trust_level, summary
        """
        facts = self.facts_db.get_facts_by_topic(topic)
        verified = [f for f in facts if f.status == FactStatus.VERIFIED]

        if not facts:
            return {
                "topic": topic,
                "facts_count": 0,
                "summary": f"Über {topic} weiß ich noch nicht viel. Das könnte ich recherchieren!",
                "confidence": 0.0
            }

        avg_trust = sum(f.trust_score for f in facts) / len(facts)

        # Top-Fakten
        top_facts = sorted(facts, key=lambda x: x.trust_score, reverse=True)[:5]

        return {
            "topic": topic,
            "facts_count": len(facts),
            "verified_count": len(verified),
            "average_trust": avg_trust,
            "top_facts": [f.content for f in top_facts],
            "confidence": avg_trust,
            "summary": self._generate_knowledge_summary(topic, facts, avg_trust)
        }

    def _generate_knowledge_summary(self, topic: str, facts: List[WebFact],
                                    avg_trust: float) -> str:
        """Generiert Zusammenfassung des Wissens"""
        if avg_trust >= 0.8:
            return f"Über {topic} weiß ich einiges und bin mir ziemlich sicher."
        elif avg_trust >= 0.6:
            return f"Ich habe etwas über {topic} gelernt, aber nicht alles ist gut belegt."
        elif avg_trust >= 0.4:
            return f"Ich habe was über {topic} gehört, aber ich bin vorsichtig - nicht alles ist verifiziert."
        else:
            return f"Was ich über {topic} weiß ist nicht gut belegt. Ich sollte das besser recherchieren."

    # =========================================================================
    # INTERESSEN-ENTDECKUNG
    # =========================================================================

    def get_discovered_interests(self) -> List[Dict]:
        """Gibt alle entdeckten Interessen zurück"""
        interests = self.discovery.get_all_discovered()
        return [
            {
                "name": i.name,
                "parent_topics": i.parent_topics,
                "interest_level": i.interest_level,
                "facts_collected": i.facts_collected,
                "description": i.description
            }
            for i in interests
        ]

    def suggest_explorations(self, current_interests: List[str]) -> List[str]:
        """Schlägt neue Erkundungen vor"""
        return self.discovery.get_discovery_suggestions(current_interests)

    # =========================================================================
    # PROAKTIVES LERNEN AUS GESPRÄCHEN
    # =========================================================================

    def learn_from_conversation(self, user_message: str, holo_response: str = None,
                                 context: Dict = None) -> Dict:
        """
        Lernt proaktiv aus Gesprächen.

        Extrahiert interessante Fakten aus:
        - User-Nachrichten (der User erzählt etwas)
        - Holo's eigenen Antworten (zur Konsistenz)

        Args:
            user_message: Die Nachricht des Users
            holo_response: Holo's Antwort (optional)
            context: Zusätzlicher Kontext (topic, entities, etc.)

        Returns:
            Dict mit gelernten Fakten
        """
        learned = []
        context = context or {}

        # === 1. Fakten aus User-Nachricht extrahieren ===
        user_facts = self._extract_facts_from_text(user_message, source="user")
        for fact in user_facts:
            try:
                result = self.learn_fact(
                    content=fact['content'],
                    topic=fact.get('topic', 'conversation'),
                    source_url="user_conversation",
                    trust_score=0.6  # User-Info ist mittelmäßig vertrauenswürdig
                )
                learned.append({
                    "source": "user",
                    "fact": fact['content'][:100],
                    "stored": True
                })
            except Exception as e:
                logger.debug(f"[LEARN] Fakt speichern fehlgeschlagen: {e}")

        # === 2. Eigene Aussagen merken (für Konsistenz) ===
        if holo_response:
            holo_facts = self._extract_facts_from_text(holo_response, source="holo")
            for fact in holo_facts:
                try:
                    result = self.learn_fact(
                        content=fact['content'],
                        topic=fact.get('topic', 'holo_statement'),
                        source_url="self_statement",
                        trust_score=0.8  # Eigene Aussagen hoch bewerten
                    )
                    learned.append({
                        "source": "self",
                        "fact": fact['content'][:100],
                        "stored": True
                    })
                except Exception:
                    pass

        logger.debug(f"[LEARN] {len(learned)} Fakten aus Gespräch gelernt")

        return {
            "learned_count": len(learned),
            "facts": learned,
            "timestamp": datetime.now().isoformat()
        }

    def _extract_facts_from_text(self, text: str, source: str = "unknown") -> List[Dict]:
        """
        Extrahiert Fakten aus Text.

        Erkennt:
        - Definitionen: "X ist Y", "X bedeutet Y"
        - Behauptungen: "X hat Y", "X kann Y"
        - Persönliche Infos: "Ich mag X", "Mein Lieblings-X ist Y"
        """
        import re
        facts = []

        # Zu kurz oder nur Frage
        if len(text) < 20 or text.strip().endswith('?'):
            return facts

        # Pattern für Fakten
        fact_patterns = [
            # Definitionen
            (r'(\w+(?:\s+\w+)?)\s+ist\s+(?:ein[e]?\s+)?(.{10,80})', 'definition'),
            (r'(\w+(?:\s+\w+)?)\s+bedeutet\s+(.{10,80})', 'definition'),

            # Behauptungen
            (r'(\w+(?:\s+\w+)?)\s+hat\s+(.{10,80})', 'claim'),
            (r'(\w+(?:\s+\w+)?)\s+kann\s+(.{10,80})', 'claim'),

            # Persönliche Präferenzen (vom User)
            (r'(?:ich\s+)?mag\s+(.{5,50})', 'preference'),
            (r'mein[e]?\s+lieblings[-\s]?(\w+)\s+ist\s+(.{5,50})', 'preference'),
            (r'ich\s+(?:liebe|hasse|finde.*gut)\s+(.{5,50})', 'preference'),
        ]

        for pattern, fact_type in fact_patterns:
            matches = re.findall(pattern, text.lower(), re.IGNORECASE)
            for match in matches[:2]:  # Max 2 pro Pattern
                if isinstance(match, tuple):
                    content = ' '.join(match).strip()
                else:
                    content = match.strip()

                if len(content) > 15:  # Nicht zu kurz
                    facts.append({
                        'content': content[:200],
                        'type': fact_type,
                        'topic': self._guess_topic(content),
                        'source': source
                    })

        return facts[:5]  # Max 5 Fakten pro Text

    def _guess_topic(self, text: str) -> str:
        """Rät das Thema eines Textes"""
        text_lower = text.lower()

        topic_keywords = {
            'gaming': ['spiel', 'game', 'zocken', 'steam', 'playstation', 'xbox', 'nintendo'],
            'anime': ['anime', 'manga', 'japan', 'otaku', 'cosplay'],
            'musik': ['musik', 'song', 'band', 'album', 'konzert', 'spotify'],
            'tech': ['computer', 'software', 'app', 'internet', 'ki', 'ai', 'programmier'],
            'essen': ['essen', 'kochen', 'rezept', 'lecker', 'geschmack'],
            'film': ['film', 'movie', 'kino', 'serie', 'netflix'],
        }

        for topic, keywords in topic_keywords.items():
            if any(kw in text_lower for kw in keywords):
                return topic

        return 'general'

    # =========================================================================
    # PROMPT-KONTEXT
    # =========================================================================

    def get_prompt_context(self) -> str:
        """Generiert Kontext für System-Prompt"""
        sections = []

        # Entdeckte Interessen
        interests = self.get_discovered_interests()
        if interests:
            lines = ["=== ENTDECKTE INTERESSEN ==="]
            for i in interests[:3]:
                lines.append(f"• {i['name']}: {i['description']}")
            sections.append("\n".join(lines))

        # Wissen-Überblick
        verified_count = len(self.facts_db.get_verified_facts())
        total_count = len(self.facts_db.facts)

        if total_count > 0:
            sections.append(
                f"=== WISSEN ===\n"
                f"Fakten gesammelt: {total_count} ({verified_count} verifiziert)\n"
                f"Kritisches Denken: Aktiv 🛡️"
            )

        return "\n\n".join(sections) if sections else ""

    # =========================================================================
    # EXPRESSIONS
    # =========================================================================

    def express_skepticism(self, about: str = "") -> str:
        """Drückt Skepsis aus"""
        expressions = [
            f"Hmm, {about}... das klingt interessant, aber ich sollte das prüfen.",
            "Moment, eine Quelle reicht mir nicht. *tippt mit dem Hände*",
            f"Ich bin skeptisch bei {about}. Wo steht das noch?",
            "Das Internet ist voller Unsinn... lass mich das verifizieren.",
            "*Augen zucken misstrauisch* Das glaube ich erst wenn ich es bestätigt habe.",
        ]
        return random.choice(expressions)

    def express_verification_success(self, topic: str) -> str:
        """Drückt erfolgreiche Verifizierung aus"""
        expressions = [
            f"✅ Ja! Ich habe {topic} auf mehreren seriösen Seiten gefunden. Das stimmt!",
            f"Bestätigt! {topic} ist wahr - mehrere gute Quellen sagen das.",
            f"*Augen stellen sich zufrieden auf* {topic} ist verifiziert!",
        ]
        return random.choice(expressions)

    def express_verification_failure(self, topic: str) -> str:
        """Drückt fehlgeschlagene Verifizierung aus"""
        expressions = [
            f"⚠️ Vorsicht! Ich konnte {topic} nicht verifizieren.",
            f"Hmm, {topic} finde ich nirgends bestätigt. Das ist verdächtig...",
            f"*Hände zuckt nervös* {topic} scheint nicht zu stimmen.",
        ]
        return random.choice(expressions)

    # =========================================================================
    # WEB-SUCHE (NEU!)
    # =========================================================================

    def search_web(self, query: str, intent: SearchIntent = None,
                   limit: int = 5, auto_learn: bool = True) -> List[Dict]:
        """
        Führt eine Web-Suche durch (DuckDuckGo).

        Args:
            query: Die Suchanfrage
            intent: Warum wird gesucht (CURIOSITY, LEARNING, USER_REQUEST, etc.)
            limit: Maximale Anzahl Ergebnisse
            auto_learn: Automatisch Fakten aus Ergebnissen lernen

        Returns:
            Liste von Suchergebnissen mit title, url, snippet
        """
        import urllib.parse
        import re

        try:
            import requests
        except ImportError:
            logger.warning("[WEBCURIOSITY] requests nicht verfügbar")
            return []

        intent = intent or SearchIntent.USER_REQUEST
        search_id = f"search_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        logger.info(f"[WEBCURIOSITY] 🔍 Web-Suche: '{query}' (intent: {intent.value})")

        try:
            # DuckDuckGo HTML-Suche (kein API-Key nötig)
            encoded_query = urllib.parse.quote_plus(query)
            search_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            resp = requests.get(search_url, headers=headers, timeout=15)

            if resp.status_code != 200:
                logger.warning(f"[WEBCURIOSITY] DuckDuckGo HTTP {resp.status_code}")
                return []

            # Parse Ergebnisse
            results = []
            html = resp.text

            # DuckDuckGo HTML Format: <a class="result__a" href="...">Title</a>
            link_pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>([^<]*)</a>'
            matches = re.findall(link_pattern, html, re.IGNORECASE)

            # Snippets extrahieren
            snippet_pattern = r'<a[^>]*class="result__snippet"[^>]*>([^<]*)</a>'
            snippets = re.findall(snippet_pattern, html, re.IGNORECASE)

            for i, (url, title) in enumerate(matches[:limit]):
                # URL dekodieren (DuckDuckGo wrapped URLs)
                if "uddg=" in url:
                    url_match = re.search(r'uddg=([^&]*)', url)
                    if url_match:
                        url = urllib.parse.unquote(url_match.group(1))

                snippet = snippets[i].strip() if i < len(snippets) else ""

                results.append({
                    "title": title.strip(),
                    "url": url,
                    "snippet": snippet,
                    "trust_score": self.trusted_sources.get_trust_score(url)[0]
                })

            # Search-Tracking aktualisieren
            self.last_search = query
            self.last_results = results
            self.last_search_time = datetime.now()
            self.is_searching = False

            # Such-History speichern
            search_query = SearchQuery(
                query_id=search_id,
                query=query,
                intent=intent,
                topics=self._extract_topics(query),
                results_count=len(results),
                timestamp=datetime.now().isoformat(),
                was_successful=len(results) > 0
            )
            self.search_history.append(search_query)

            # Automatisch Fakten lernen
            if auto_learn and results:
                facts_learned = self._auto_learn_from_results(query, results[:3])
                search_query.facts_extracted = facts_learned
                self.facts_learned = getattr(self, 'facts_learned', 0) + facts_learned

            logger.info(f"[WEBCURIOSITY] ✅ {len(results)} Ergebnisse gefunden")
            return results

        except Exception as e:
            logger.warning(f"[WEBCURIOSITY] Search error: {e}")
            self.is_searching = False
            return []

    def _extract_topics(self, query: str) -> List[str]:
        """Extrahiert Themen aus einer Suchanfrage"""
        # Einfache Wort-Extraktion (Stoppwörter filtern)
        stopwords = {'was', 'ist', 'wie', 'wer', 'wo', 'wann', 'warum',
                     'der', 'die', 'das', 'ein', 'eine', 'und', 'oder',
                     'über', 'von', 'zu', 'mit', 'für', 'auf', 'in'}
        words = query.lower().split()
        topics = [w for w in words if w not in stopwords and len(w) > 2]
        return topics[:5]

    def _auto_learn_from_results(self, query: str, results: List[Dict]) -> int:
        """Lernt automatisch Fakten aus Suchergebnissen"""
        facts_learned = 0

        for result in results:
            snippet = result.get('snippet', '')
            url = result.get('url', '')
            trust_score = result.get('trust_score', 0.5)

            # Nur von vertrauenswürdigen Quellen lernen
            if trust_score < 0.5 or not snippet:
                continue

            # Snippet als Fakt speichern (gekürzt)
            if len(snippet) > 50:
                try:
                    self.learn_fact(
                        content=snippet[:300],
                        topic=query,
                        source_url=url,
                        trust_score=trust_score
                    )
                    facts_learned += 1
                except Exception as e:
                    logger.debug(f"[WEBCURIOSITY] Fakt speichern fehlgeschlagen: {e}")

        return facts_learned

    def should_auto_research(self, query: str) -> bool:
        """
        Prüft ob eine Anfrage automatisch recherchiert werden sollte.

        Automatische Recherche bei:
        - Aktuelle Ereignisse (News, heute, aktuell)
        - Explizite Wissens-Lücken
        - Verifizierungs-Anfragen
        """
        query_lower = query.lower()

        # Aktualitäts-Keywords
        current_keywords = [
            'aktuell', 'heute', 'news', 'neueste', 'gerade',
            'passiert', 'ereignis', 'breaking', 'neu erschienen',
            'update', 'stand von', 'letzte woche', 'gestern'
        ]

        # Verifizierungs-Keywords
        verify_keywords = [
            'stimmt es', 'ist es wahr', 'verifizier', 'check',
            'wirklich', 'tatsächlich', 'echt dass'
        ]

        for kw in current_keywords + verify_keywords:
            if kw in query_lower:
                return True

        return False

    def get_search_stats(self) -> Dict:
        """Gibt Such-Statistiken zurück"""
        total_searches = len(self.search_history)
        successful = sum(1 for s in self.search_history if s.was_successful)
        total_facts = sum(s.facts_extracted for s in self.search_history)

        return {
            "total_searches": total_searches,
            "successful_searches": successful,
            "success_rate": successful / total_searches if total_searches > 0 else 0,
            "total_facts_learned": total_facts,
            "last_search": self.last_search if hasattr(self, 'last_search') else None,
            "last_search_time": self.last_search_time.isoformat() if self.last_search_time else None
        }

    def get_recent_searches(self, limit: int = 5) -> List[Dict]:
        """Gibt die letzten Suchen zurück"""
        recent = self.search_history[-limit:] if self.search_history else []
        return [
            {
                "query": s.query,
                "intent": s.intent.value,
                "results": s.results_count,
                "facts_learned": s.facts_extracted,
                "timestamp": s.timestamp,
                "success": s.was_successful
            }
            for s in reversed(recent)
        ]


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("HOLO WEB CURIOSITY TEST")
    print("=" * 60)

    curiosity = HoloWebCuriosity(Path("/tmp/test_web_curiosity"))

    # Test 1: Quellen-Bewertung
    print("\n1️⃣ QUELLEN-BEWERTUNG:")
    print("-" * 40)

    test_urls = [
        "https://www.tagesschau.de/article/123",
        "https://www.nature.com/article/abc",
        "https://random-blog.xyz/shocking-truth",
        "https://www.heise.de/news/test",
    ]

    for url in test_urls:
        result = curiosity.evaluate_source(url)
        emoji = "✅" if result["is_trustworthy"] else "⚠️"
        print(f"{emoji} {url[:40]}...")
        print(f"   Trust: {result['trust_score']:.0%} | {result['reason']}")
        if result.get("skeptical_thought"):
            print(f"   💭 {result['skeptical_thought']}")
        print()

    # Test 2: Fakt lernen
    print("\n2️⃣ FAKTEN LERNEN:")
    print("-" * 40)

    # Fakt von guter Quelle
    result = curiosity.learn_fact(
        content="Wölfe kommunizieren durch Heulen über große Distanzen",
        topic="wölfe",
        source_url="https://www.nature.com/wolves",
        related_topics=["kommunikation", "tiere"]
    )
    print(f"Fakt 1: {result['holos_response']}")
    print(f"   Trust: {result['trust_score']:.0%} | Status: {result['status']}")

    # Fakt von fragwürdiger Quelle
    result = curiosity.learn_fact(
        content="Wölfe können mit Gedanken kommunizieren",
        topic="wölfe",
        source_url="https://mystery-facts.xyz/wolves",
        related_topics=["kommunikation"]
    )
    print(f"\nFakt 2: {result['holos_response']}")
    print(f"   Trust: {result['trust_score']:.0%} | Status: {result['status']}")

    # Test 3: Interessen-Entdeckung
    print("\n3️⃣ INTERESSEN-ENTDECKUNG:")
    print("-" * 40)

    result = curiosity.learn_fact(
        content="Quanteneffekte spielen eine Rolle in der Photosynthese",
        topic="physik",
        source_url="https://www.nature.com/quantum",
        related_topics=["quantenphysik", "biologie"]
    )
    print(f"Fakt: {result['holos_response']}")
    if result.get("new_interest"):
        print(f"🌟 Neues Interesse entdeckt: {result['new_interest']}")

    # Test 4: Was weiß ich?
    print("\n4️⃣ WAS WEISS ICH:")
    print("-" * 40)

    knowledge = curiosity.what_do_i_know("wölfe")
    print(f"Thema: {knowledge['topic']}")
    print(f"Fakten: {knowledge['facts_count']} (davon {knowledge.get('verified_count', 0)} verifiziert)")
    print(f"Konfidenz: {knowledge['confidence']:.0%}")
    print(f"💭 {knowledge['summary']}")

    # Test 5: Entdeckte Interessen
    print("\n5️⃣ ENTDECKTE INTERESSEN:")
    print("-" * 40)

    for interest in curiosity.get_discovered_interests():
        print(f"• {interest['name']}")
        print(f"  Parent: {interest['parent_topics']}")
        print(f"  Level: {interest['interest_level']:.0%}")

    # Test 6: Skepsis ausdrücken
    print("\n6️⃣ SKEPSIS:")
    print("-" * 40)
    print(curiosity.express_skepticism("diese Behauptung"))

    # Test 7: Prompt-Kontext
    print("\n7️⃣ PROMPT-KONTEXT:")
    print("-" * 40)
    print(curiosity.get_prompt_context())

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
