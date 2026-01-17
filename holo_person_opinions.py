"""
holo_person_opinions.py - Personen-Meinungssystem für Holo

Ermöglicht Holo, begründete Meinungen über ALLE Personen zu bilden:
- Bekannte (Freunde, User)
- Öffentliche Personen (Politiker, YouTuber, Prominente)
- Fiktive Charaktere (Anime, Filme, Bücher)
- Historische Personen

Features:
- Charakter-Assessment basierend auf Verhalten/Informationen
- Begründete Meinungen mit Evidenz
- Adaptive Updates bei neuen Informationen
- Automatische Trigger bei News/Gesprächen
"""

import logging
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)

# Autonomous Thinking Integration (optional)
AUTONOMOUS_THINKING_AVAILABLE = False
_autonomous_thinking = None

try:
    from holo_autonomous_thinking import (
        get_autonomous_thinking,
        IntuitiveSystem,
        SelfChallenger,
        TrustNetwork
    )
    AUTONOMOUS_THINKING_AVAILABLE = True
    logger.info("✅ Autonomous Thinking System verfügbar")
except ImportError:
    logger.debug("Autonomous Thinking System nicht verfügbar")


# ============================================================
# ENUMS & CONSTANTS
# ============================================================

class PersonType(Enum):
    """Kategorien von Personen"""
    KNOWN_CONTACT = "known_contact"      # Bekannte, Freunde, User
    PUBLIC_FIGURE = "public_figure"       # Politiker, Prominente, YouTuber
    FICTIONAL = "fictional"               # Anime-Charaktere, Film-Figuren
    HISTORICAL = "historical"             # Historische Persönlichkeiten
    UNKNOWN = "unknown"                   # Noch nicht kategorisiert


class TraitCategory(Enum):
    """Kategorien von Charaktereigenschaften"""
    MORAL = "moral"           # Ehrlichkeit, Integrität, Fairness
    INTELLECTUAL = "intellectual"  # Intelligenz, Kreativität, Weisheit
    SOCIAL = "social"         # Empathie, Freundlichkeit, Charisma
    EMOTIONAL = "emotional"   # Stabilität, Sensibilität, Leidenschaft
    BEHAVIORAL = "behavioral" # Zuverlässigkeit, Fleiß, Disziplin


class CognitiveStance(Enum):
    """Kognitive Haltung gegenüber Informationen über Personen"""
    NEUTRAL = "neutral"           # Keine besondere Haltung
    CURIOUS = "curious"           # Neugierig, will mehr wissen
    SKEPTICAL = "skeptical"       # Skeptisch, hinterfragt
    SUSPICIOUS = "suspicious"     # Misstrauisch, vermutet Täuschung
    TRUSTING = "trusting"         # Vertrauend, glaubt leicht
    ADMIRING = "admiring"         # Bewundernd
    DISAPPOINTED = "disappointed" # Enttäuscht (bei Widerspruch zu pos. Erwartung)
    RELIEVED = "relieved"         # Erleichtert (bei Widerspruch zu neg. Erwartung)
    CONFLICTED = "conflicted"     # Widersprüchliche Infos


class SourceCredibility(Enum):
    """Glaubwürdigkeit von Informationsquellen"""
    VERIFIED = 1.0          # Verifizierte Quelle (eigene Erfahrung, vertrauenswürdige Person)
    REPUTABLE = 0.8         # Seriöse Quelle (Qualitätsmedien, Experten)
    MIXED = 0.6             # Gemischte Glaubwürdigkeit
    QUESTIONABLE = 0.4      # Fragwürdige Quelle (Boulevardpresse, anonyme Posts)
    UNRELIABLE = 0.2        # Unzuverlässig (bekannte Fake-News Quellen)
    UNKNOWN = 0.5           # Unbekannte Quelle


# Standard Charakter-Traits die bewertet werden
CHARACTER_TRAITS = {
    # Moralische Traits
    "ehrlich": TraitCategory.MORAL,
    "integer": TraitCategory.MORAL,
    "fair": TraitCategory.MORAL,
    "vertrauenswürdig": TraitCategory.MORAL,
    "loyal": TraitCategory.MORAL,
    "respektvoll": TraitCategory.MORAL,
    "authentisch": TraitCategory.MORAL,

    # Intellektuelle Traits
    "intelligent": TraitCategory.INTELLECTUAL,
    "kreativ": TraitCategory.INTELLECTUAL,
    "weise": TraitCategory.INTELLECTUAL,
    "neugierig": TraitCategory.INTELLECTUAL,
    "reflektiert": TraitCategory.INTELLECTUAL,
    "tiefgründig": TraitCategory.INTELLECTUAL,
    "analytisch": TraitCategory.INTELLECTUAL,

    # Soziale Traits
    "empathisch": TraitCategory.SOCIAL,
    "freundlich": TraitCategory.SOCIAL,
    "charismatisch": TraitCategory.SOCIAL,
    "humorvoll": TraitCategory.SOCIAL,
    "warmherzig": TraitCategory.SOCIAL,
    "offen": TraitCategory.SOCIAL,
    "kommunikativ": TraitCategory.SOCIAL,

    # Emotionale Traits
    "emotional_stabil": TraitCategory.EMOTIONAL,
    "sensibel": TraitCategory.EMOTIONAL,
    "leidenschaftlich": TraitCategory.EMOTIONAL,
    "gelassen": TraitCategory.EMOTIONAL,
    "resilient": TraitCategory.EMOTIONAL,

    # Verhaltens-Traits
    "zuverlässig": TraitCategory.BEHAVIORAL,
    "fleißig": TraitCategory.BEHAVIORAL,
    "diszipliniert": TraitCategory.BEHAVIORAL,
    "mutig": TraitCategory.BEHAVIORAL,
    "geduldig": TraitCategory.BEHAVIORAL,
    "konsequent": TraitCategory.BEHAVIORAL,
}

# Holos Kern-Werte die ihre Bewertung beeinflussen
HOLO_CORE_VALUES = {
    "ehrlich": 1.5,        # Ehrlichkeit ist ihr SEHR wichtig
    "authentisch": 1.4,    # Authentizität schätzt sie hoch
    "tiefgründig": 1.3,    # Tiefe Gespräche liebt sie
    "empathisch": 1.2,     # Empathie ist wichtig
    "intelligent": 1.1,    # Intelligenz schätzt sie
    "loyal": 1.2,          # Loyalität ist wichtig
    "humorvoll": 1.1,      # Humor mag sie
    "oberflächlich": -1.3, # Oberflächlichkeit hasst sie
    "unehrlich": -1.5,     # Lügen sind das Schlimmste
    "manipulativ": -1.4,   # Manipulation verabscheut sie
}


# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class TraitEvidence:
    """Evidenz für eine Charaktereigenschaft"""
    description: str          # Was wurde beobachtet?
    source: str               # Woher? (Gespräch, News, Video, etc.)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    strength: float = 0.5     # Wie stark ist diese Evidenz? (0-1)
    is_positive: bool = True  # Unterstützt oder widerspricht es dem Trait?


@dataclass
class CharacterTrait:
    """Eine bewertete Charaktereigenschaft"""
    name: str                                  # z.B. "ehrlich"
    category: TraitCategory                    # Kategorie
    score: float = 0.0                         # -1 (negativ) bis +1 (positiv)
    confidence: float = 0.0                    # Wie sicher? (0-1)
    evidence: List[TraitEvidence] = field(default_factory=list)
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

    def add_evidence(self, description: str, source: str,
                     strength: float = 0.5, is_positive: bool = True) -> None:
        """Fügt neue Evidenz hinzu und aktualisiert Score"""
        self.evidence.append(TraitEvidence(
            description=description,
            source=source,
            strength=strength,
            is_positive=is_positive
        ))

        # Score neu berechnen
        self._recalculate_score()
        self.last_updated = datetime.now().isoformat()

    def _recalculate_score(self) -> None:
        """Berechnet Score basierend auf Evidenz"""
        if not self.evidence:
            self.score = 0.0
            self.confidence = 0.0
            return

        # Gewichteter Durchschnitt
        total_weight = 0.0
        weighted_sum = 0.0

        for ev in self.evidence:
            weight = ev.strength
            value = 1.0 if ev.is_positive else -1.0
            weighted_sum += weight * value
            total_weight += weight

        if total_weight > 0:
            self.score = max(-1.0, min(1.0, weighted_sum / total_weight))

        # Confidence steigt mit mehr Evidenz
        self.confidence = min(1.0, len(self.evidence) * 0.15)


@dataclass
class PersonOpinion:
    """Holos Gesamtmeinung über eine Person"""
    overall_score: float = 0.0      # -1 (mag nicht) bis +1 (mag sehr)
    confidence: float = 0.0          # Wie sicher ist sie sich?
    summary: str = ""                # Kurze Zusammenfassung
    detailed_reasoning: List[str] = field(default_factory=list)
    first_impression: Optional[str] = None
    has_changed: bool = False        # Hat sich die Meinung geändert?
    change_history: List[Dict] = field(default_factory=list)

    def express(self) -> str:
        """Drückt die Meinung natürlich aus"""
        if self.confidence < 0.2:
            prefix = "Ich kenne sie/ihn noch nicht gut genug, aber "
        elif self.confidence < 0.4:
            prefix = "Mein erster Eindruck ist, dass "
        elif self.confidence < 0.6:
            prefix = "Ich denke, "
        elif self.confidence < 0.8:
            prefix = "Ich bin ziemlich sicher, dass "
        else:
            prefix = "Ich bin überzeugt, dass "

        return f"{prefix}{self.summary}"

    def explain_why(self) -> str:
        """Erklärt warum sie so denkt"""
        if not self.detailed_reasoning:
            return "Ich habe noch nicht genug Informationen um das zu begründen."

        reasons = "\n- ".join(self.detailed_reasoning[:5])
        return f"Das denke ich, weil:\n- {reasons}"


@dataclass
class PersonModel:
    """Komplettes Modell einer Person aus Holos Perspektive"""
    name: str
    person_type: PersonType = PersonType.UNKNOWN

    # Charakter-Assessment
    traits: Dict[str, CharacterTrait] = field(default_factory=dict)

    # Gesamtmeinung
    opinion: PersonOpinion = field(default_factory=PersonOpinion)

    # Meta-Informationen
    known_facts: List[str] = field(default_factory=list)
    interactions: List[Dict] = field(default_factory=list)
    first_encountered: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

    # Beziehungs-spezifisch (nur für known_contact)
    relationship_type: Optional[str] = None  # "friend", "user", "acquaintance"
    trust_level: float = 0.5
    emotional_bond: float = 0.0

    # Zusätzliche Kategorisierung
    tags: Set[str] = field(default_factory=set)  # z.B. {"anime", "politiker", "youtuber"}
    aliases: Set[str] = field(default_factory=set)  # Alternative Namen

    def get_trait(self, trait_name: str) -> Optional[CharacterTrait]:
        """Holt einen Trait oder None"""
        return self.traits.get(trait_name.lower())

    def set_trait(self, trait_name: str, score: float,
                  evidence_desc: str, source: str) -> None:
        """Setzt oder aktualisiert einen Trait"""
        trait_name = trait_name.lower()

        if trait_name not in self.traits:
            category = CHARACTER_TRAITS.get(trait_name, TraitCategory.BEHAVIORAL)
            self.traits[trait_name] = CharacterTrait(
                name=trait_name,
                category=category
            )

        is_positive = score >= 0
        self.traits[trait_name].add_evidence(
            evidence_desc, source, abs(score), is_positive
        )

        self.last_updated = datetime.now().isoformat()

    def add_fact(self, fact: str) -> None:
        """Fügt einen bekannten Fakt hinzu"""
        if fact not in self.known_facts:
            self.known_facts.append(fact)
            self.last_updated = datetime.now().isoformat()

    def record_interaction(self, interaction_type: str,
                          description: str, emotional_impact: float = 0.0) -> None:
        """Speichert eine Interaktion"""
        self.interactions.append({
            "type": interaction_type,
            "description": description,
            "emotional_impact": emotional_impact,
            "timestamp": datetime.now().isoformat()
        })
        self.last_updated = datetime.now().isoformat()

    def recalculate_opinion(self) -> None:
        """Berechnet die Gesamtmeinung neu"""
        if not self.traits:
            return

        # Gewichtete Summe der Traits
        total_weight = 0.0
        weighted_sum = 0.0
        reasoning = []

        for trait_name, trait in self.traits.items():
            if trait.confidence < 0.1:
                continue

            # Holos Kern-Werte beeinflussen die Gewichtung
            value_weight = HOLO_CORE_VALUES.get(trait_name, 1.0)
            weight = trait.confidence * abs(value_weight)

            # Wenn Holo einen Trait hasst und Person ihn hat → negativer Impact
            if value_weight < 0:
                contribution = -trait.score * abs(value_weight)
            else:
                contribution = trait.score * value_weight

            weighted_sum += weight * contribution
            total_weight += weight

            # Reasoning generieren
            if abs(trait.score) > 0.3 and trait.confidence > 0.2:
                if trait.score > 0:
                    reasoning.append(f"zeigt {trait_name} ({trait.score:.1f})")
                else:
                    reasoning.append(f"mangelt es an {trait_name} ({trait.score:.1f})")

        # Berechne Gesamtscore
        old_score = self.opinion.overall_score
        if total_weight > 0:
            self.opinion.overall_score = max(-1.0, min(1.0, weighted_sum / total_weight))

        # Confidence basierend auf Trait-Anzahl
        self.opinion.confidence = min(1.0, len([t for t in self.traits.values()
                                                 if t.confidence > 0.2]) * 0.12)

        # Summary generieren
        self._generate_summary()
        self.opinion.detailed_reasoning = reasoning

        # Change tracking
        if abs(old_score - self.opinion.overall_score) > 0.1:
            self.opinion.has_changed = True
            self.opinion.change_history.append({
                "from": old_score,
                "to": self.opinion.overall_score,
                "timestamp": datetime.now().isoformat()
            })

    def _generate_summary(self) -> str:
        """Generiert eine natürliche Zusammenfassung"""
        score = self.opinion.overall_score

        if score > 0.7:
            self.opinion.summary = f"ich {self.name} sehr mag und respektiere"
        elif score > 0.4:
            self.opinion.summary = f"ich {self.name} sympathisch finde"
        elif score > 0.1:
            self.opinion.summary = f"{self.name} mir eher positiv auffällt"
        elif score > -0.1:
            self.opinion.summary = f"ich {self.name} gegenüber neutral bin"
        elif score > -0.4:
            self.opinion.summary = f"ich {self.name} eher kritisch sehe"
        elif score > -0.7:
            self.opinion.summary = f"ich {self.name} nicht besonders mag"
        else:
            self.opinion.summary = f"ich {self.name} wirklich nicht leiden kann"

        return self.opinion.summary

    def to_dict(self) -> Dict:
        """Serialisiert zu Dictionary"""
        return {
            "name": self.name,
            "person_type": self.person_type.value,
            "traits": {
                name: {
                    "name": t.name,
                    "category": t.category.value,
                    "score": t.score,
                    "confidence": t.confidence,
                    "evidence": [
                        {"description": e.description, "source": e.source,
                         "timestamp": e.timestamp, "strength": e.strength,
                         "is_positive": e.is_positive}
                        for e in t.evidence
                    ],
                    "last_updated": t.last_updated
                }
                for name, t in self.traits.items()
            },
            "opinion": {
                "overall_score": self.opinion.overall_score,
                "confidence": self.opinion.confidence,
                "summary": self.opinion.summary,
                "detailed_reasoning": self.opinion.detailed_reasoning,
                "first_impression": self.opinion.first_impression,
                "has_changed": self.opinion.has_changed,
                "change_history": self.opinion.change_history
            },
            "known_facts": self.known_facts,
            "interactions": self.interactions,
            "first_encountered": self.first_encountered,
            "last_updated": self.last_updated,
            "relationship_type": self.relationship_type,
            "trust_level": self.trust_level,
            "emotional_bond": self.emotional_bond,
            "tags": list(self.tags),
            "aliases": list(self.aliases)
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "PersonModel":
        """Deserialisiert aus Dictionary"""
        model = cls(name=data["name"])
        model.person_type = PersonType(data.get("person_type", "unknown"))

        # Traits wiederherstellen
        for name, t_data in data.get("traits", {}).items():
            trait = CharacterTrait(
                name=t_data["name"],
                category=TraitCategory(t_data["category"]),
                score=t_data["score"],
                confidence=t_data["confidence"],
                last_updated=t_data.get("last_updated", "")
            )
            for e_data in t_data.get("evidence", []):
                trait.evidence.append(TraitEvidence(
                    description=e_data["description"],
                    source=e_data["source"],
                    timestamp=e_data.get("timestamp", ""),
                    strength=e_data.get("strength", 0.5),
                    is_positive=e_data.get("is_positive", True)
                ))
            model.traits[name] = trait

        # Opinion wiederherstellen
        op_data = data.get("opinion", {})
        model.opinion.overall_score = op_data.get("overall_score", 0.0)
        model.opinion.confidence = op_data.get("confidence", 0.0)
        model.opinion.summary = op_data.get("summary", "")
        model.opinion.detailed_reasoning = op_data.get("detailed_reasoning", [])
        model.opinion.first_impression = op_data.get("first_impression")
        model.opinion.has_changed = op_data.get("has_changed", False)
        model.opinion.change_history = op_data.get("change_history", [])

        # Rest
        model.known_facts = data.get("known_facts", [])
        model.interactions = data.get("interactions", [])
        model.first_encountered = data.get("first_encountered", "")
        model.last_updated = data.get("last_updated", "")
        model.relationship_type = data.get("relationship_type")
        model.trust_level = data.get("trust_level", 0.5)
        model.emotional_bond = data.get("emotional_bond", 0.0)
        model.tags = set(data.get("tags", []))
        model.aliases = set(data.get("aliases", []))

        return model


# ============================================================
# CHARACTER TRAIT ANALYZER
# ============================================================

class CharacterTraitAnalyzer:
    """
    Analysiert Text um Charaktereigenschaften zu extrahieren.
    Ohne LLM - nutzt Pattern-Matching und Keyword-Analyse.
    """

    # Positive Indikatoren für Traits
    TRAIT_INDICATORS = {
        "ehrlich": {
            "positive": ["ehrlich", "aufrichtig", "wahrheit", "offen gesagt",
                        "transparent", "gesteht", "zugegeben", "direkt"],
            "negative": ["gelogen", "lüge", "täuschung", "betrug", "verschwiegen",
                        "verheimlich", "unehrlich", "falsch behauptet"]
        },
        "intelligent": {
            "positive": ["clever", "intelligent", "klug", "brilliant", "genial",
                        "scharfsinnig", "analytisch", "durchdacht", "weise"],
            "negative": ["dumm", "naiv", "uninformiert", "oberflächlich",
                        "versteht nicht", "ignorant"]
        },
        "empathisch": {
            "positive": ["empathisch", "mitfühlend", "verständnisvoll", "einfühlsam",
                        "kümmert sich", "hilft", "unterstützt", "tröstet"],
            "negative": ["kalt", "gefühllos", "ignoriert", "gleichgültig",
                        "herzlos", "rücksichtslos"]
        },
        "mutig": {
            "positive": ["mutig", "tapfer", "couragiert", "wagt", "traut sich",
                        "kämpft", "setzt sich ein", "steht auf"],
            "negative": ["feige", "ängstlich", "versteckt sich", "schweigt",
                        "traut sich nicht"]
        },
        "loyal": {
            "positive": ["loyal", "treu", "steht zu", "hält zu", "unterstützt",
                        "verteidigt", "bleibt bei"],
            "negative": ["verraten", "hintergangen", "im stich gelassen",
                        "aufgegeben", "fallengelassen"]
        },
        "kreativ": {
            "positive": ["kreativ", "innovativ", "originell", "künstlerisch",
                        "einfallsreich", "erfindet", "gestaltet"],
            "negative": ["langweilig", "einfallslos", "kopiert", "unkreativ"]
        },
        "humorvoll": {
            "positive": ["witzig", "humorvoll", "lustig", "komisch", "lacht",
                        "scherzt", "unterhaltend", "amüsant"],
            "negative": ["humorlos", "ernst", "steif", "verbissen"]
        },
        "zuverlässig": {
            "positive": ["zuverlässig", "pünktlich", "verlässlich", "hält wort",
                        "vertrauenswürdig", "konsequent", "beständig"],
            "negative": ["unzuverlässig", "vergisst", "verspricht und hält nicht",
                        "chaotisch", "unbeständig"]
        },
        "respektvoll": {
            "positive": ["respektvoll", "höflich", "achtet", "wertschätzt",
                        "respektiert grenzen", "nimmt ernst"],
            "negative": ["respektlos", "unhöflich", "beleidigend", "übergriffig",
                        "ignoriert grenzen", "herablassend"]
        },
        "authentisch": {
            "positive": ["authentisch", "echt", "sich selbst", "ehrlich zu sich",
                        "verstellt sich nicht", "natürlich"],
            "negative": ["fake", "verstellt", "spielt rolle", "heuchler",
                        "unecht", "aufgesetzt"]
        },
        "tiefgründig": {
            "positive": ["tiefgründig", "nachdenklich", "philosophisch",
                        "reflektiert", "hinterfragt", "denkt nach"],
            "negative": ["oberflächlich", "seicht", "denkt nicht nach",
                        "unreflektiert"]
        },
        "manipulativ": {
            "positive": ["manipuliert", "benutzt", "ausgenutzt", "kontrolliert",
                        "beeinflusst negativ", "gaslighting"],
            "negative": ["ehrlich", "direkt", "transparent", "fair"]
        }
    }

    # Verstärker und Abschwächer
    INTENSIFIERS = ["sehr", "extrem", "total", "absolut", "unglaublich", "echt", "wirklich"]
    DIMINISHERS = ["etwas", "bisschen", "leicht", "ein wenig", "manchmal"]
    NEGATIONS = ["nicht", "kein", "nie", "niemals", "kaum"]

    def analyze_text(self, text: str, source: str = "unknown") -> List[Tuple[str, float, str]]:
        """
        Analysiert Text und extrahiert Charakter-Evidenz.

        Returns: Liste von (trait_name, score, evidence_description)
        """
        text_lower = text.lower()
        results = []

        for trait, indicators in self.TRAIT_INDICATORS.items():
            # Positive Indikatoren suchen
            for indicator in indicators["positive"]:
                if indicator in text_lower:
                    score = self._calculate_score(text_lower, indicator, True)
                    context = self._extract_context(text, indicator)
                    results.append((trait, score, context))
                    break

            # Negative Indikatoren suchen
            for indicator in indicators["negative"]:
                if indicator in text_lower:
                    score = self._calculate_score(text_lower, indicator, False)
                    context = self._extract_context(text, indicator)
                    # Bei "manipulativ" ist negativ = positiv (also gut)
                    if trait == "manipulativ":
                        results.append((trait, -score, context))
                    else:
                        results.append((trait, score, context))
                    break

        return results

    def _calculate_score(self, text: str, indicator: str, is_positive: bool) -> float:
        """Berechnet Score mit Intensifiern/Negationen"""
        base_score = 0.5 if is_positive else -0.5

        # Suche nach Intensifiern in der Nähe
        words = text.split()
        try:
            idx = next(i for i, w in enumerate(words) if indicator in w)
            context_words = words[max(0, idx-3):idx]

            # Intensifier?
            for intensifier in self.INTENSIFIERS:
                if intensifier in context_words:
                    base_score *= 1.5
                    break

            # Diminisher?
            for diminisher in self.DIMINISHERS:
                if diminisher in context_words:
                    base_score *= 0.6
                    break

            # Negation?
            for negation in self.NEGATIONS:
                if negation in context_words:
                    base_score *= -1
                    break
        except StopIteration:
            pass

        return max(-1.0, min(1.0, base_score))

    def _extract_context(self, text: str, indicator: str) -> str:
        """Extrahiert Kontext um den Indikator"""
        # Finde Satz mit Indikator
        sentences = re.split(r'[.!?]', text)
        for sentence in sentences:
            if indicator.lower() in sentence.lower():
                return sentence.strip()[:200]
        return indicator


# ============================================================
# SOURCE CREDIBILITY ANALYZER
# ============================================================

class SourceCredibilityAnalyzer:
    """
    Analysiert die Glaubwürdigkeit von Informationsquellen.
    Holos skeptische Seite - sie glaubt nicht alles blind.
    """

    # Bekannte seriöse Quellen
    REPUTABLE_SOURCES = {
        # Deutsche Qualitätsmedien
        "tagesschau", "zdf", "ard", "zeit", "spiegel", "faz", "süddeutsche",
        "deutschlandfunk", "dw", "ndr", "wdr", "br",
        # Internationale
        "bbc", "reuters", "ap news", "nyt", "guardian", "washington post",
        # Wissenschaft
        "nature", "science", "spektrum", "scinexx",
        # Tech (für Tech-News)
        "heise", "golem", "ars technica", "the verge",
    }

    # Fragwürdige Quellen
    QUESTIONABLE_SOURCES = {
        "bild", "bunte", "gala", "intouch", "ok!", "closer",
        "buzzfeed", "dailymail", "thesun", "mirror",
        "twitter", "x.com", "facebook", "tiktok",  # Social Media ohne Verifizierung
        "reddit", "4chan", "telegram",
    }

    # Signalwörter für Clickbait/Sensationen
    CLICKBAIT_SIGNALS = [
        "schockierend", "unglaublich", "du wirst nicht glauben",
        "geheim", "enthüllt", "skandal", "sensation", "exklusiv",
        "breaking", "eilmeldung", "wahnsinn", "krass",
        "experten sind schockiert", "ärzte hassen diesen trick"
    ]

    def __init__(self):
        self.base_skepticism = 0.6  # Holos Standard-Skepsis-Level

    def assess_source(self, source: str) -> Tuple[SourceCredibility, float, str]:
        """
        Bewertet eine Informationsquelle.

        Returns:
            (SourceCredibility enum, confidence 0-1, reason str)
        """
        source_lower = source.lower()

        # Eigene Erfahrung = höchste Glaubwürdigkeit
        if source_lower in ["eigene erfahrung", "selbst erlebt", "direct", "conversation"]:
            return (SourceCredibility.VERIFIED, 0.95,
                    "Das habe ich selbst erlebt/gehört")

        # Seriöse Quellen
        for reputable in self.REPUTABLE_SOURCES:
            if reputable in source_lower:
                return (SourceCredibility.REPUTABLE, 0.85,
                        f"{reputable.title()} ist eine seriöse Quelle")

        # Fragwürdige Quellen
        for questionable in self.QUESTIONABLE_SOURCES:
            if questionable in source_lower:
                return (SourceCredibility.QUESTIONABLE, 0.7,
                        f"Hmm, {questionable} ist nicht gerade bekannt für Qualitätsjournalismus...")

        # News allgemein
        if "news" in source_lower:
            return (SourceCredibility.MIXED, 0.6, "News-Quelle - sollte ich gegenchecken")

        # Unbekannt
        return (SourceCredibility.UNKNOWN, 0.5,
                "Kenne diese Quelle nicht - bin vorsichtig")

    def check_for_clickbait(self, text: str) -> Tuple[bool, float, str]:
        """
        Prüft ob Text Clickbait-Signale enthält.

        Returns:
            (is_clickbait, confidence, reason)
        """
        text_lower = text.lower()
        signals_found = []

        for signal in self.CLICKBAIT_SIGNALS:
            if signal in text_lower:
                signals_found.append(signal)

        if len(signals_found) >= 2:
            return (True, 0.85,
                    f"*Augen zucken skeptisch* Das klingt nach Clickbait... '{signals_found[0]}'?")
        elif len(signals_found) == 1:
            return (True, 0.6,
                    f"Hmm, '{signals_found[0]}' - das klingt etwas übertrieben...")

        return (False, 0.3, "")

    def get_credibility_weight(self, source: str, text: str) -> float:
        """
        Berechnet wie stark die Info gewichtet werden soll.
        Niedrige Glaubwürdigkeit = niedrigere Gewichtung.
        """
        credibility, _, _ = self.assess_source(source)
        is_clickbait, cb_conf, _ = self.check_for_clickbait(text)

        weight = credibility.value if isinstance(credibility.value, float) else 0.5

        if is_clickbait:
            weight *= (1 - cb_conf * 0.3)  # Reduziere bei Clickbait

        return max(0.1, min(1.0, weight))


# ============================================================
# SKEPTICAL PROCESSOR
# ============================================================

class SkepticalProcessor:
    """
    Holos skeptische Denkprozesse bei Informationen über Personen.
    "Ich glaube nicht alles was ich höre."
    """

    SKEPTICAL_TEMPLATES = {
        "too_good": [
            "*legt Augen skeptisch an* Das klingt zu gut um wahr zu sein...",
            "Hmm, wirklich? Das wäre ja fast zu perfekt.",
            "*skeptischer Blick* Gibt's dafür auch Beweise?",
        ],
        "too_bad": [
            "*schaut überrascht* Das klingt sehr einseitig... was ist die andere Seite?",
            "Hmm, ob das wirklich so schlimm ist? Manchmal wird übertrieben.",
            "*nachdenklich* Nur eine Quelle? Ich warte auf mehr Infos.",
        ],
        "contradicts_existing": [
            "*verwirrt* Moment... das widerspricht was ich vorher gehört habe.",
            "Hmm, das passt nicht zu dem was ich über {person} wusste...",
            "*neigt den Kopf* Interessant - aber das steht im Widerspruch zu vorherigen Infos.",
        ],
        "unknown_source": [
            "*vorsichtig* Woher stammt das? Kenne die Quelle nicht.",
            "Hmm, ohne seriöse Quelle bin ich da skeptisch.",
            "*Augen aufmerksam* Ist das verifiziert? Oder nur ein Gerücht?",
        ],
        "sudden_change": [
            "*überrascht* Plötzlich so anders? Das kommt mir komisch vor.",
            "Menschen ändern sich nicht über Nacht... *skeptisch*",
            "*misstrauisch* Das ist ein sehr plötzlicher Wandel...",
        ],
        "general": [
            "*denkt nach* Mal sehen ob andere Quellen das bestätigen.",
            "Interessant, aber ich behalte meine Skepsis erstmal.",
            "*schaut überrascht* Ich notiere mir das... mit Fragezeichen.",
        ]
    }

    def __init__(self, skepticism_level: float = 0.6):
        self.skepticism_level = skepticism_level  # 0=gläubig, 1=hyperskeptisch
        self.credibility_analyzer = SourceCredibilityAnalyzer()

    def should_be_skeptical(self, info_strength: float, source_credibility: float,
                           contradicts_existing: bool = False) -> bool:
        """Entscheidet ob Skepsis angebracht ist"""
        # Sehr starke Behauptungen bei schwacher Quelle → skeptisch
        if abs(info_strength) > 0.7 and source_credibility < 0.5:
            return True

        # Widerspruch zu existierenden Infos → skeptisch
        if contradicts_existing:
            return True

        # Generelle Skepsis basierend auf Level
        skepticism_threshold = 1.0 - self.skepticism_level
        return source_credibility < skepticism_threshold

    def generate_skeptical_thought(self, category: str = "general",
                                  person: str = "") -> str:
        """Generiert einen skeptischen Gedanken"""
        import random
        templates = self.SKEPTICAL_TEMPLATES.get(category, self.SKEPTICAL_TEMPLATES["general"])
        thought = random.choice(templates)
        return thought.format(person=person) if "{person}" in thought else thought

    def process_with_skepticism(self, person_name: str, information: str,
                               source: str, existing_opinion: float = 0.0
                               ) -> Dict[str, Any]:
        """
        Verarbeitet Information mit angemessener Skepsis.

        Returns:
            Dict mit:
            - adjusted_weight: Gewichtung basierend auf Glaubwürdigkeit
            - cognitive_stance: Kognitive Haltung
            - skeptical_thought: Skeptischer Gedanke (wenn angebracht)
            - should_verify: Ob weitere Verifizierung nötig ist
        """
        # Quellen-Glaubwürdigkeit
        credibility, cred_conf, cred_reason = self.credibility_analyzer.assess_source(source)
        cred_weight = self.credibility_analyzer.get_credibility_weight(source, information)

        # Clickbait-Check
        is_clickbait, cb_conf, cb_reason = self.credibility_analyzer.check_for_clickbait(information)

        # Trait-Stärke schätzen (stark positive/negative Behauptungen)
        info_strength = self._estimate_info_strength(information)

        # Widerspruchs-Check (vereinfacht - prüft ob Info-Richtung existierender Meinung widerspricht)
        contradicts = (info_strength > 0.5 and existing_opinion < -0.3) or \
                      (info_strength < -0.5 and existing_opinion > 0.3)

        # Skepsis-Entscheidung
        be_skeptical = self.should_be_skeptical(info_strength, cred_weight, contradicts)

        # Kognitive Haltung bestimmen
        stance = self._determine_stance(info_strength, cred_weight, contradicts, is_clickbait)

        # Skeptischen Gedanken generieren
        skeptical_thought = None
        if be_skeptical:
            if contradicts:
                skeptical_thought = self.generate_skeptical_thought("contradicts_existing", person_name)
            elif is_clickbait:
                skeptical_thought = cb_reason
            elif cred_weight < 0.4:
                skeptical_thought = self.generate_skeptical_thought("unknown_source", person_name)
            elif info_strength > 0.7:
                skeptical_thought = self.generate_skeptical_thought("too_good", person_name)
            elif info_strength < -0.7:
                skeptical_thought = self.generate_skeptical_thought("too_bad", person_name)
            else:
                skeptical_thought = self.generate_skeptical_thought("general", person_name)

        return {
            "adjusted_weight": cred_weight * (0.7 if be_skeptical else 1.0),
            "cognitive_stance": stance,
            "skeptical_thought": skeptical_thought,
            "should_verify": be_skeptical and abs(info_strength) > 0.5,
            "credibility_reason": cred_reason,
            "is_clickbait": is_clickbait,
            "contradicts_existing": contradicts
        }

    def _estimate_info_strength(self, text: str) -> float:
        """Schätzt wie stark/extrem die Information ist"""
        text_lower = text.lower()

        strong_positive = ["perfekt", "fantastisch", "brilliant", "held", "vorbild",
                         "immer ehrlich", "niemals lügt", "absolut vertrauenswürdig"]
        strong_negative = ["monster", "lügner", "betrüger", "kriminell", "korrupt",
                          "immer lügt", "niemals ehrlich", "absolut unvertrauenswürdig"]

        for word in strong_positive:
            if word in text_lower:
                return 0.8

        for word in strong_negative:
            if word in text_lower:
                return -0.8

        # Moderate Stärke basierend auf anderen Indikatoren
        moderate_positive = ["gut", "nett", "freundlich", "hilfsbereit", "ehrlich"]
        moderate_negative = ["schlecht", "gemein", "unfreundlich", "egoistisch", "verlogen"]

        pos_count = sum(1 for w in moderate_positive if w in text_lower)
        neg_count = sum(1 for w in moderate_negative if w in text_lower)

        if pos_count > neg_count:
            return min(0.5, pos_count * 0.15)
        elif neg_count > pos_count:
            return max(-0.5, -neg_count * 0.15)

        return 0.0

    def _determine_stance(self, info_strength: float, credibility: float,
                         contradicts: bool, is_clickbait: bool) -> CognitiveStance:
        """Bestimmt die kognitive Haltung"""
        if contradicts:
            return CognitiveStance.CONFLICTED

        if is_clickbait:
            return CognitiveStance.SUSPICIOUS

        if credibility < 0.4:
            return CognitiveStance.SKEPTICAL

        if info_strength > 0.6 and credibility > 0.7:
            return CognitiveStance.ADMIRING

        if info_strength < -0.6 and credibility > 0.7:
            return CognitiveStance.DISAPPOINTED

        if credibility > 0.8:
            return CognitiveStance.TRUSTING

        if abs(info_strength) < 0.3:
            return CognitiveStance.CURIOUS

        return CognitiveStance.NEUTRAL


# ============================================================
# CONTRADICTION DETECTOR
# ============================================================

class ContradictionDetector:
    """
    Erkennt Widersprüche zwischen neuen Informationen und existierenden Überzeugungen.
    "Das passt nicht zusammen..."
    """

    # Widersprüchliche Trait-Paare
    CONTRADICTING_TRAITS = {
        "ehrlich": ["unehrlich", "verlogen", "lügner"],
        "intelligent": ["dumm", "unintelligent", "begriffsstutzig"],
        "empathisch": ["gefühllos", "kalt", "herzlos"],
        "loyal": ["verräterisch", "illoyal", "untreu"],
        "mutig": ["feige", "ängstlich"],
        "freundlich": ["unfreundlich", "gemein", "fies"],
        "zuverlässig": ["unzuverlässig", "chaotisch"],
        "authentisch": ["fake", "unecht", "aufgesetzt"],
        "respektvoll": ["respektlos", "unhöflich"],
    }

    def __init__(self):
        # Invertierte Map für schnellere Suche
        self.contradiction_map = {}
        for trait, contradictions in self.CONTRADICTING_TRAITS.items():
            for contra in contradictions:
                self.contradiction_map[contra] = trait
            self.contradiction_map[trait] = contradictions[0] if contradictions else None

    def find_contradictions(self, new_traits: Dict[str, float],
                           existing_traits: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Findet Widersprüche zwischen neuen und existierenden Traits.

        Returns:
            Liste von Widersprüchen mit Details
        """
        contradictions = []

        for new_trait, new_score in new_traits.items():
            # Direkter Widerspruch: gleicher Trait, andere Richtung
            if new_trait in existing_traits:
                existing = existing_traits[new_trait]
                existing_score = existing.score if hasattr(existing, 'score') else existing

                # Signifikanter Richtungswechsel
                if (new_score > 0.3 and existing_score < -0.3) or \
                   (new_score < -0.3 and existing_score > 0.3):
                    contradictions.append({
                        "type": "direction_change",
                        "trait": new_trait,
                        "old_score": existing_score,
                        "new_score": new_score,
                        "message": f"'{new_trait}' ändert sich von {existing_score:.1f} zu {new_score:.1f}"
                    })

            # Semantischer Widerspruch: widersprüchliche Traits
            if new_trait in self.contradiction_map:
                opposing_trait = self.contradiction_map[new_trait]
                if opposing_trait and opposing_trait in existing_traits:
                    existing = existing_traits[opposing_trait]
                    existing_score = existing.score if hasattr(existing, 'score') else existing

                    if existing_score > 0.3 and new_score > 0.3:
                        contradictions.append({
                            "type": "semantic_contradiction",
                            "trait": new_trait,
                            "opposing_trait": opposing_trait,
                            "message": f"'{new_trait}' widerspricht '{opposing_trait}'"
                        })

        return contradictions

    def generate_conflict_response(self, contradictions: List[Dict]) -> str:
        """Generiert eine Reaktion auf Widersprüche"""
        import random

        if not contradictions:
            return ""

        responses = [
            "*verwirrt die Augen drehend* Moment... das passt nicht zusammen.",
            "*stirnrunzelnd* Hmm, das widerspricht dem was ich vorher wusste...",
            "*nachdenklich* Interessant - aber das steht im Widerspruch zu meinen bisherigen Infos.",
            "*Kopf schief legend* Irgendwas stimmt hier nicht... die Infos widersprechen sich.",
        ]

        base = random.choice(responses)

        # Füge spezifischen Widerspruch hinzu
        if contradictions[0]["type"] == "direction_change":
            trait = contradictions[0]["trait"]
            base += f" Plötzlich ist '{trait}' ganz anders?"
        elif contradictions[0]["type"] == "semantic_contradiction":
            t1 = contradictions[0]["trait"]
            t2 = contradictions[0]["opposing_trait"]
            base += f" Wie kann jemand '{t1}' und '{t2}' gleichzeitig sein?"

        return base


# ============================================================
# PERSON TYPE DETECTOR
# ============================================================

class PersonTypeDetector:
    """Erkennt automatisch den Typ einer Person"""

    # Keywords für verschiedene Typen
    PUBLIC_FIGURE_KEYWORDS = [
        "politiker", "minister", "präsident", "kanzler", "abgeordnete",
        "youtuber", "influencer", "streamer", "tiktoker",
        "schauspieler", "sänger", "musiker", "künstler", "autor",
        "ceo", "unternehmer", "milliardär",
        "sportler", "fußballer", "tennisspieler",
        "journalist", "moderator"
    ]

    FICTIONAL_KEYWORDS = [
        "anime", "manga", "charakter", "figur", "protagonist",
        "film", "serie", "buch", "roman", "spiel", "game",
        "fiktiv", "erfunden", "aus"  # "aus Naruto", etc.
    ]

    HISTORICAL_KEYWORDS = [
        "historisch", "geschichte", "jahrhundert", "war ein",
        "lebte", "gestorben", "geboren 1", "geboren 2",  # Geboren 1800, etc.
        "antik", "mittelalter", "weltkrieg"
    ]

    # Bekannte fiktive Universen
    FICTIONAL_UNIVERSES = [
        "naruto", "one piece", "attack on titan", "demon slayer",
        "my hero academia", "jujutsu kaisen", "dragon ball",
        "evangelion", "steins;gate", "death note", "fullmetal",
        "sword art online", "re:zero", "konosuba",
        "star wars", "marvel", "dc", "harry potter", "herr der ringe",
        "game of thrones", "breaking bad", "the witcher"
    ]

    def detect(self, name: str, context: str = "") -> PersonType:
        """Erkennt den Personen-Typ"""
        combined = f"{name} {context}".lower()

        # Check für fiktive Universen
        for universe in self.FICTIONAL_UNIVERSES:
            if universe in combined:
                return PersonType.FICTIONAL

        # Keyword-basierte Erkennung
        for keyword in self.FICTIONAL_KEYWORDS:
            if keyword in combined:
                return PersonType.FICTIONAL

        for keyword in self.HISTORICAL_KEYWORDS:
            if keyword in combined:
                return PersonType.HISTORICAL

        for keyword in self.PUBLIC_FIGURE_KEYWORDS:
            if keyword in combined:
                return PersonType.PUBLIC_FIGURE

        return PersonType.UNKNOWN


# ============================================================
# PERSON OPINION MANAGER
# ============================================================

class PersonOpinionManager:
    """
    Zentrale Verwaltung aller Personen-Meinungen.
    Persistiert in Datenbank und JSON.
    """

    def __init__(self, data_dir: str = "data", skepticism_level: float = 0.6,
                 intuition_weight: float = 0.2):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        self.persons: Dict[str, PersonModel] = {}
        self.trait_analyzer = CharacterTraitAnalyzer()
        self.type_detector = PersonTypeDetector()

        # Skepticism & Critical Thinking
        self.skeptical_processor = SkepticalProcessor(skepticism_level)
        self.contradiction_detector = ContradictionDetector()
        self.credibility_analyzer = SourceCredibilityAnalyzer()

        # Autonomous Thinking (Intuition, Self-Challenge, etc.)
        self.autonomous_thinking = None
        self.intuition_weight = intuition_weight  # 0.15-0.3 empfohlen
        if AUTONOMOUS_THINKING_AVAILABLE:
            try:
                self.autonomous_thinking = get_autonomous_thinking()
                logger.info(f"🧠 Intuition aktiviert (Gewichtung: {intuition_weight})")
            except Exception as e:
                logger.warning(f"Autonomous Thinking nicht initialisiert: {e}")

        # Database connection (optional)
        self.db = None
        self.storage = None  # ModuleStorageAdapter

        # Integration layer
        self.system_integrator = None

        # Load existing data
        self._load_state()
        self._try_connect_integrator()

    def _try_connect_integrator(self) -> None:
        """Versucht sich mit dem SystemIntegrator zu verbinden"""
        try:
            from holo_integration_layer import get_integrator, get_module_storage
            self.system_integrator = get_integrator()
            self.system_integrator.connect("person_opinions", self)
            self.storage = get_module_storage("person_opinions")
            logger.info("PersonOpinionManager mit SystemIntegrator verbunden")
        except ImportError:
            logger.debug("SystemIntegrator nicht verfügbar")
        except Exception as e:
            logger.warning(f"Fehler bei Integrator-Verbindung: {e}")

    def _load_state(self) -> None:
        """Lädt gespeicherte Personen-Daten"""
        # Versuche aus Storage zu laden
        if self.storage:
            data = self.storage.load("persons", {})
            for name, person_data in data.items():
                self.persons[name.lower()] = PersonModel.from_dict(person_data)
            return

        # Fallback: JSON
        json_path = self.data_dir / "person_opinions.json"
        if json_path.exists():
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for name, person_data in data.get("persons", {}).items():
                    self.persons[name.lower()] = PersonModel.from_dict(person_data)
                logger.info(f"Loaded {len(self.persons)} person models")
            except Exception as e:
                logger.error(f"Fehler beim Laden: {e}")

    def _save_state(self) -> None:
        """Speichert Personen-Daten"""
        data = {name: person.to_dict() for name, person in self.persons.items()}

        # Speichere in Storage wenn verfügbar
        if self.storage:
            self.storage.save("persons", data)
            return

        # Fallback: JSON
        json_path = self.data_dir / "person_opinions.json"
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump({"persons": data}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Fehler beim Speichern: {e}")

    def get_or_create_person(self, name: str,
                             context: str = "",
                             person_type: Optional[PersonType] = None) -> PersonModel:
        """Holt oder erstellt ein PersonModel"""
        key = name.lower()

        # Auch in Aliases suchen
        for person in self.persons.values():
            if key in [a.lower() for a in person.aliases]:
                return person

        if key not in self.persons:
            detected_type = person_type or self.type_detector.detect(name, context)
            self.persons[key] = PersonModel(
                name=name,
                person_type=detected_type
            )
            logger.info(f"Neue Person erstellt: {name} ({detected_type.value})")

        return self.persons[key]

    def process_information(self, person_name: str, information: str,
                           source: str = "unknown") -> Dict[str, Any]:
        """
        Verarbeitet neue Information über eine Person.
        Analysiert Traits, prüft Glaubwürdigkeit, und aktualisiert Meinung.

        Args:
            person_name: Name der Person
            information: Text mit Informationen
            source: Woher stammt die Info? (news, gespräch, video, etc.)

        Returns:
            Dict mit Analyse-Ergebnis inkl. Skepsis und kognitiver Haltung
        """
        person = self.get_or_create_person(person_name, information)
        old_opinion = person.opinion.overall_score

        # 0. INTUITION - Schneller erster Eindruck (BEVOR Analyse)
        gut_feeling = None
        gut_score = 0.0
        if self.autonomous_thinking:
            try:
                gut_score, gut_feeling = self.autonomous_thinking.intuitive.get_first_impression(
                    person_name, information
                )
            except Exception as e:
                logger.debug(f"Intuition-Fehler: {e}")

        # 1. SKEPSIS-PRÜFUNG: Ist die Information glaubwürdig?
        skeptic_result = self.skeptical_processor.process_with_skepticism(
            person_name=person_name,
            information=information,
            source=source,
            existing_opinion=old_opinion
        )

        cognitive_stance = skeptic_result["cognitive_stance"]
        skeptical_thought = skeptic_result["skeptical_thought"]
        credibility_weight = skeptic_result["adjusted_weight"]

        # 2. CHARAKTER-TRAITS analysieren
        trait_results = self.trait_analyzer.analyze_text(information, source)

        # 3. WIDERSPRUCHS-PRÜFUNG
        new_traits_dict = {t[0]: t[1] for t in trait_results}
        contradictions = self.contradiction_detector.find_contradictions(
            new_traits_dict, person.traits
        )

        conflict_response = ""
        if contradictions:
            conflict_response = self.contradiction_detector.generate_conflict_response(contradictions)
            cognitive_stance = CognitiveStance.CONFLICTED

        # 4. TRAITS AKTUALISIEREN (mit Glaubwürdigkeits-Gewichtung)
        changes = []
        for trait_name, score, evidence in trait_results:
            old_trait = person.get_trait(trait_name)
            old_score = old_trait.score if old_trait else 0.0

            # Gewichte Score nach Glaubwürdigkeit
            weighted_score = score * credibility_weight
            person.set_trait(trait_name, weighted_score, evidence, source)

            new_trait = person.get_trait(trait_name)
            if new_trait and abs(new_trait.score - old_score) > 0.1:
                changes.append({
                    "trait": trait_name,
                    "old_score": old_score,
                    "new_score": new_trait.score,
                    "evidence": evidence,
                    "credibility_weighted": credibility_weight < 1.0
                })

        # 5. FAKT SPEICHERN (mit Vertrauenslevel)
        fact_prefix = "[" + source
        if credibility_weight < 0.5:
            fact_prefix += " - skeptisch"
        fact_prefix += "] "
        person.add_fact(f"{fact_prefix}{information[:200]}")

        # 6. MEINUNG NEU BERECHNEN
        person.recalculate_opinion()

        # 7. CHANGE LOG
        if self.system_integrator and abs(person.opinion.overall_score - old_opinion) > 0.05:
            try:
                from holo_integration_layer import ChangeType
                self.system_integrator.change_log.record(
                    change_type=ChangeType.OPINION,
                    source_system="person_opinions",
                    key=f"person:{person_name}",
                    old_value=old_opinion,
                    new_value=person.opinion.overall_score,
                    reason=f"Neue Info von {source}: {information[:100]}"
                )
            except Exception:
                pass

        self._save_state()

        return {
            "person": person_name,
            "trait_changes": changes,
            "opinion_change": {
                "old": old_opinion,
                "new": person.opinion.overall_score
            },
            "current_summary": person.opinion.summary,
            # Intuition (schneller erster Eindruck)
            "gut_feeling": gut_feeling,
            "gut_score": gut_score,
            "intuition_weight": self.intuition_weight,
            # Skepsis & kognitive Reaktion
            "cognitive_stance": cognitive_stance.value,
            "skeptical_thought": skeptical_thought,
            "credibility_weight": credibility_weight,
            "contradictions": contradictions,
            "conflict_response": conflict_response,
            "should_verify": skeptic_result["should_verify"],
            "is_clickbait": skeptic_result["is_clickbait"]
        }

    def process_behavior(self, person_name: str, action: str,
                        emotional_impact: float = 0.0,
                        source: str = "observation") -> Dict[str, Any]:
        """
        Verarbeitet beobachtetes Verhalten einer Person.

        Args:
            person_name: Name der Person
            action: Was hat die Person getan?
            emotional_impact: Wie hat es Holo emotional beeinflusst? (-1 bis 1)
            source: Kontext der Beobachtung

        Returns:
            Dict mit Analyse-Ergebnis
        """
        person = self.get_or_create_person(person_name)

        # Interaktion speichern
        person.record_interaction("behavior", action, emotional_impact)

        # Verhalten analysieren für Traits
        result = self.process_information(person_name, action, source)

        # Emotionaler Impact beeinflusst auch Trust
        if person.person_type == PersonType.KNOWN_CONTACT:
            person.trust_level = max(0.0, min(1.0,
                person.trust_level + emotional_impact * 0.1))
            person.emotional_bond = max(-1.0, min(1.0,
                person.emotional_bond + emotional_impact * 0.05))

        self._save_state()
        return result

    def get_opinion(self, person_name: str) -> Optional[PersonOpinion]:
        """Holt die Meinung zu einer Person"""
        key = person_name.lower()
        if key in self.persons:
            return self.persons[key].opinion
        return None

    def get_full_assessment(self, person_name: str) -> Optional[Dict[str, Any]]:
        """Holt die komplette Bewertung einer Person"""
        key = person_name.lower()
        if key not in self.persons:
            return None

        person = self.persons[key]

        # Top positive und negative Traits
        sorted_traits = sorted(
            [(name, t) for name, t in person.traits.items() if t.confidence > 0.2],
            key=lambda x: x[1].score,
            reverse=True
        )

        positive_traits = [(n, t.score) for n, t in sorted_traits if t.score > 0.2][:5]
        negative_traits = [(n, t.score) for n, t in sorted_traits if t.score < -0.2][:5]

        return {
            "name": person.name,
            "type": person.person_type.value,
            "opinion": {
                "score": person.opinion.overall_score,
                "confidence": person.opinion.confidence,
                "summary": person.opinion.express(),
                "reasoning": person.opinion.explain_why()
            },
            "positive_traits": positive_traits,
            "negative_traits": negative_traits,
            "trust_level": person.trust_level,
            "emotional_bond": person.emotional_bond,
            "known_facts_count": len(person.known_facts),
            "interactions_count": len(person.interactions)
        }

    def explain_opinion(self, person_name: str) -> str:
        """Generiert eine natürliche Erklärung der Meinung"""
        key = person_name.lower()
        if key not in self.persons:
            return f"Ich kenne {person_name} noch nicht gut genug um eine Meinung zu haben."

        person = self.persons[key]

        if person.opinion.confidence < 0.2:
            return f"Ich weiß noch nicht genug über {person.name} um mir eine fundierte Meinung zu bilden."

        # Baue Erklärung
        parts = [person.opinion.express()]

        # Positive Gründe
        positive_reasons = []
        negative_reasons = []

        for name, trait in person.traits.items():
            if trait.confidence < 0.2:
                continue

            if trait.score > 0.3:
                positive_reasons.append(f"{name} ({trait.score:.1f})")
            elif trait.score < -0.3:
                negative_reasons.append(f"mangelnde {name} ({trait.score:.1f})")

        if positive_reasons:
            parts.append(f"Positiv fällt mir auf: {', '.join(positive_reasons[:3])}")

        if negative_reasons:
            parts.append(f"Kritisch sehe ich: {', '.join(negative_reasons[:3])}")

        if person.opinion.has_changed:
            parts.append("Meine Meinung hat sich im Laufe der Zeit verändert.")

        return " ".join(parts)

    def compare_persons(self, name1: str, name2: str) -> Dict[str, Any]:
        """Vergleicht zwei Personen"""
        person1 = self.persons.get(name1.lower())
        person2 = self.persons.get(name2.lower())

        if not person1 or not person2:
            return {"error": "Eine oder beide Personen sind nicht bekannt"}

        # Gemeinsame Traits finden
        common_traits = set(person1.traits.keys()) & set(person2.traits.keys())

        comparisons = []
        for trait in common_traits:
            t1 = person1.traits[trait]
            t2 = person2.traits[trait]
            if t1.confidence > 0.2 and t2.confidence > 0.2:
                comparisons.append({
                    "trait": trait,
                    f"{person1.name}": t1.score,
                    f"{person2.name}": t2.score,
                    "difference": t1.score - t2.score
                })

        return {
            "persons": [person1.name, person2.name],
            "opinion_scores": {
                person1.name: person1.opinion.overall_score,
                person2.name: person2.opinion.overall_score
            },
            "trait_comparisons": sorted(comparisons,
                                        key=lambda x: abs(x["difference"]),
                                        reverse=True)[:10],
            "preference": person1.name if person1.opinion.overall_score > person2.opinion.overall_score else person2.name
        }

    def get_all_opinions_summary(self) -> List[Dict[str, Any]]:
        """Gibt eine Übersicht aller Meinungen"""
        summaries = []
        for name, person in self.persons.items():
            if person.opinion.confidence > 0.1:
                summaries.append({
                    "name": person.name,
                    "type": person.person_type.value,
                    "score": person.opinion.overall_score,
                    "confidence": person.opinion.confidence,
                    "summary": person.opinion.summary
                })

        return sorted(summaries, key=lambda x: x["score"], reverse=True)

    def search_by_trait(self, trait_name: str,
                        min_score: float = 0.3) -> List[Tuple[str, float]]:
        """Findet Personen mit einem bestimmten Trait"""
        results = []
        for name, person in self.persons.items():
            trait = person.get_trait(trait_name)
            if trait and trait.score >= min_score and trait.confidence > 0.2:
                results.append((person.name, trait.score))

        return sorted(results, key=lambda x: x[1], reverse=True)

    def get_liked_persons(self, min_score: float = 0.3) -> List[str]:
        """Gibt Personen zurück die Holo mag"""
        return [
            person.name for person in self.persons.values()
            if person.opinion.overall_score >= min_score
            and person.opinion.confidence > 0.2
        ]

    def get_disliked_persons(self, max_score: float = -0.3) -> List[str]:
        """Gibt Personen zurück die Holo nicht mag"""
        return [
            person.name for person in self.persons.values()
            if person.opinion.overall_score <= max_score
            and person.opinion.confidence > 0.2
        ]


# ============================================================
# NEWS/INFO TRIGGER SYSTEM
# ============================================================

class PersonInfoTrigger:
    """
    Automatisches Trigger-System das bei neuen Informationen
    über Personen die Meinungen aktualisiert.
    """

    def __init__(self, opinion_manager: PersonOpinionManager):
        self.opinion_manager = opinion_manager
        self.name_patterns: List[re.Pattern] = []
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Kompiliert Regex-Patterns für Personen-Erkennung"""
        # Pattern für bekannte Personen
        for name in self.opinion_manager.persons.keys():
            pattern = re.compile(rf'\b{re.escape(name)}\b', re.IGNORECASE)
            self.name_patterns.append((name, pattern))

    def add_person_pattern(self, name: str) -> None:
        """Fügt neues Pattern hinzu"""
        pattern = re.compile(rf'\b{re.escape(name)}\b', re.IGNORECASE)
        self.name_patterns.append((name, pattern))

    def process_text(self, text: str, source: str = "unknown") -> List[Dict[str, Any]]:
        """
        Verarbeitet Text und aktualisiert Meinungen für alle erwähnten Personen.

        Args:
            text: Zu analysierender Text (News, Gespräch, etc.)
            source: Quelle des Texts

        Returns:
            Liste der Änderungen
        """
        results = []

        # Suche nach bekannten Personen
        for name, pattern in self.name_patterns:
            if pattern.search(text):
                # Extrahiere relevanten Kontext um den Namen
                context = self._extract_person_context(text, name)
                if context:
                    result = self.opinion_manager.process_information(
                        name, context, source
                    )
                    if result.get("trait_changes"):
                        results.append(result)

        # Suche nach neuen Personen (Großgeschriebene Namen)
        new_names = self._detect_new_names(text)
        for name in new_names:
            if name.lower() not in self.opinion_manager.persons:
                context = self._extract_person_context(text, name)
                if context and len(context) > 20:
                    result = self.opinion_manager.process_information(
                        name, context, source
                    )
                    self.add_person_pattern(name)
                    results.append(result)

        return results

    def _extract_person_context(self, text: str, name: str) -> str:
        """Extrahiert Sätze die die Person erwähnen"""
        sentences = re.split(r'[.!?]', text)
        relevant = [s.strip() for s in sentences if name.lower() in s.lower()]
        return " ".join(relevant[:3])

    def _detect_new_names(self, text: str) -> List[str]:
        """Erkennt potentielle neue Personen-Namen"""
        # Einfaches Pattern: Zwei aufeinanderfolgende Großbuchstaben-Wörter
        pattern = r'\b([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)+)\b'
        matches = re.findall(pattern, text)

        # Filtere offensichtliche Nicht-Namen
        filtered = []
        non_names = {"Die Zeit", "Der Spiegel", "Das Erste", "Die Welt"}
        for match in matches:
            if match not in non_names and len(match.split()) <= 3:
                filtered.append(match)

        return list(set(filtered))


# ============================================================
# GLOBAL INSTANCE & HELPERS
# ============================================================

_person_opinion_manager: Optional[PersonOpinionManager] = None


def get_person_opinion_manager() -> PersonOpinionManager:
    """Holt die globale Instanz des PersonOpinionManagers"""
    global _person_opinion_manager
    if _person_opinion_manager is None:
        _person_opinion_manager = PersonOpinionManager()
    return _person_opinion_manager


def process_person_info(person_name: str, info: str, source: str = "unknown") -> Dict:
    """Convenience-Funktion zum Verarbeiten von Personen-Infos"""
    return get_person_opinion_manager().process_information(person_name, info, source)


def get_opinion_about(person_name: str) -> Optional[str]:
    """Convenience-Funktion für Meinung zu einer Person"""
    manager = get_person_opinion_manager()
    explanation = manager.explain_opinion(person_name)
    return explanation


def why_do_i_like_or_dislike(person_name: str) -> str:
    """Erklärt warum Holo jemanden mag oder nicht mag"""
    return get_person_opinion_manager().explain_opinion(person_name)


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    # Demo
    manager = PersonOpinionManager()

    # Beispiel: Information über einen YouTuber
    result = manager.process_information(
        "PewDiePie",
        "PewDiePie hat heute ehrlich über seine Fehler gesprochen und sich bei seinen Fans entschuldigt. Er zeigt sich sehr reflektiert und authentisch.",
        source="youtube"
    )
    print(f"YouTuber: {result}")

    # Beispiel: Politiker in den News
    result = manager.process_information(
        "Max Mustermann",
        "Der Politiker Max Mustermann wurde dabei erwischt wie er gelogen hat über seine Steuererklärung. Er versuchte die Journalisten zu manipulieren.",
        source="news"
    )
    print(f"Politiker: {result}")

    # Meinungen abfragen
    print("\n=== Meinungen ===")
    print(manager.explain_opinion("PewDiePie"))
    print(manager.explain_opinion("Max Mustermann"))

    # Vollständige Bewertung
    print("\n=== Vollständige Bewertung ===")
    print(json.dumps(manager.get_full_assessment("PewDiePie"), indent=2, ensure_ascii=False))
