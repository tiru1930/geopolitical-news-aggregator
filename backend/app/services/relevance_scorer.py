import re
import logging
from typing import Dict, Tuple
from app.config import settings

logger = logging.getLogger(__name__)


class RelevanceScorer:
    """
    Calculates strategic relevance scores for news articles.
    Combines rule-based scoring with keyword analysis.
    """

    # Geographic relevance keywords (India-centric)
    GEO_KEYWORDS = {
        "high": [
            "india", "indian", "delhi", "modi", "rajnath", "jaishankar",
            "pakistan", "china", "chinese", "pla", "lac", "loc",
            "kashmir", "j&k", "jammu", "ladakh", "arunachal", "sikkim", "doklam",
            "poonch", "rajouri", "kupwara", "baramulla", "srinagar", "pulwama",
            "galwan", "pangong", "tawang", "nathu la", "chumar",
            "indo-pacific", "indian ocean", "andaman", "nicobar",
            "bangladesh", "nepal", "sri lanka", "maldives", "bhutan",
            "quad", "brics", "sco"
        ],
        "medium": [
            "asia", "asian", "south asia", "southeast asia", "east asia",
            "afghanistan", "myanmar", "tibet", "xinjiang", "taiwan",
            "japan", "australia", "usa", "america", "russia", "russian",
            "middle east", "iran", "saudi", "uae", "israel",
            "asean", "aukus", "ukraine", "north korea", "dprk"
        ],
        "low": [
            "europe", "european", "africa", "african", "latin america",
            "nato", "eu", "un", "united nations"
        ]
    }

    # Military/Security keywords
    MILITARY_KEYWORDS = {
        "high": [
            "military", "army", "navy", "air force", "defence", "defense",
            "missile", "nuclear", "weapon", "fighter jet", "warship",
            "submarine", "aircraft carrier", "tank", "artillery",
            "border", "intrusion", "incursion", "clash", "skirmish",
            "war", "conflict", "attack", "strike", "bombing",
            "terrorist", "terrorism", "insurgent", "militant",
            "special forces", "commando", "intelligence", "espionage",
            "operations", "ops", "counter-terror", "anti-terror",
            "search operation", "cordon", "encounter", "ambush",
            "ceasefire", "violation", "firing", "shelling"
        ],
        "medium": [
            "soldier", "troops", "battalion", "regiment", "division",
            "exercise", "drill", "deployment", "patrol",
            "security", "surveillance", "reconnaissance",
            "drone", "uav", "satellite", "radar",
            "arms", "ammunition", "procurement", "deal",
            "jawan", "martyred", "shaheed", "bsf", "crpf", "itbp"
        ]
    }

    # Diplomatic keywords
    DIPLOMATIC_KEYWORDS = {
        "high": [
            "summit", "bilateral", "treaty", "agreement", "pact",
            "sanctions", "embargo", "diplomatic", "ambassador",
            "foreign minister", "state visit", "talks", "negotiation",
            "alliance", "partnership", "cooperation"
        ],
        "medium": [
            "relations", "ties", "dialogue", "meeting", "visit",
            "statement", "declaration", "resolution", "vote"
        ]
    }

    # Economic/Strategic keywords
    ECONOMIC_KEYWORDS = {
        "high": [
            "trade war", "tariff", "sanctions", "embargo",
            "oil", "energy", "gas", "pipeline",
            "port", "infrastructure", "bri", "belt and road",
            "strategic", "critical minerals", "semiconductors",
            "supply chain", "economic warfare"
        ],
        "medium": [
            "trade", "export", "import", "investment", "economy",
            "gdp", "market", "currency", "debt"
        ]
    }

    def __init__(self):
        self.geo_weight = settings.geo_weight
        self.military_weight = settings.military_weight
        self.diplomatic_weight = settings.diplomatic_weight
        self.economic_weight = settings.economic_weight

    def _count_keyword_matches(self, text: str, keywords: Dict[str, list]) -> Tuple[int, int, int]:
        """Count high, medium, and low priority keyword matches"""
        text_lower = text.lower()

        high_count = sum(1 for kw in keywords.get("high", []) if kw in text_lower)
        medium_count = sum(1 for kw in keywords.get("medium", []) if kw in text_lower)
        low_count = sum(1 for kw in keywords.get("low", []) if kw in text_lower)

        return high_count, medium_count, low_count

    def _calculate_category_score(self, text: str, keywords: Dict[str, list]) -> float:
        """Calculate score for a category (0-1 scale)"""
        high, medium, low = self._count_keyword_matches(text, keywords)

        # Weighted scoring
        raw_score = (high * 1.0) + (medium * 0.5) + (low * 0.2)

        # Normalize to 0-1 (cap at certain threshold)
        # Using 5.0 divisor for better sensitivity on strategic articles
        normalized = min(raw_score / 5.0, 1.0)

        return round(normalized, 3)

    def calculate_scores(self, title: str, content: str) -> Dict[str, float]:
        """
        Calculate all relevance scores for an article.

        Returns:
            Dict with geo_score, military_score, diplomatic_score,
            economic_score, relevance_score, and relevance_level
        """
        full_text = f"{title} {content}"

        # Calculate individual category scores
        geo_score = self._calculate_category_score(full_text, self.GEO_KEYWORDS)
        military_score = self._calculate_category_score(full_text, self.MILITARY_KEYWORDS)
        diplomatic_score = self._calculate_category_score(full_text, self.DIPLOMATIC_KEYWORDS)
        economic_score = self._calculate_category_score(full_text, self.ECONOMIC_KEYWORDS)

        # Calculate weighted total score
        relevance_score = (
            geo_score * self.geo_weight +
            military_score * self.military_weight +
            diplomatic_score * self.diplomatic_weight +
            economic_score * self.economic_weight
        )

        relevance_score = round(relevance_score, 3)

        # Determine relevance level (adjusted thresholds)
        if relevance_score >= 0.3:
            relevance_level = "high"
        elif relevance_score >= 0.15:
            relevance_level = "medium"
        else:
            relevance_level = "low"

        return {
            "geo_score": geo_score,
            "military_score": military_score,
            "diplomatic_score": diplomatic_score,
            "economic_score": economic_score,
            "relevance_score": relevance_score,
            "relevance_level": relevance_level
        }

    def is_strategically_relevant(self, title: str, content: str, threshold: float = 0.2) -> bool:
        """Quick check if article meets minimum relevance threshold"""
        scores = self.calculate_scores(title, content)
        return scores["relevance_score"] >= threshold

    def extract_region_theme(self, title: str, content: str) -> Dict[str, str]:
        """
        Extract region, country, theme, domain from keywords (fallback when AI unavailable)
        """
        text = f"{title} {content}".lower()

        # Region detection
        region = "Global"
        region_keywords = {
            "South Asia": ["india", "pakistan", "bangladesh", "nepal", "sri lanka", "bhutan", "maldives", "kashmir", "ladakh"],
            "East Asia": ["china", "japan", "korea", "taiwan", "hong kong", "beijing", "tokyo", "seoul", "pyongyang"],
            "Indo-Pacific": ["indo-pacific", "quad", "aukus", "pacific", "asean", "south china sea", "andaman"],
            "Middle East": ["iran", "israel", "saudi", "uae", "iraq", "syria", "gaza", "yemen", "gulf"],
            "Europe": ["nato", "russia", "ukraine", "eu", "european", "moscow", "kyiv", "london", "paris", "berlin"],
            "Central Asia": ["afghanistan", "kazakhstan", "uzbekistan", "tajikistan", "turkmenistan"],
            "Africa": ["africa", "african", "egypt", "libya", "sudan", "ethiopia", "nigeria", "kenya"],
            "Americas": ["america", "usa", "us ", "washington", "pentagon", "canada", "mexico", "brazil"],
        }
        for reg, keywords in region_keywords.items():
            if any(kw in text for kw in keywords):
                region = reg
                break

        # Country detection (primary)
        country = ""
        country_keywords = {
            "India": ["india", "indian", "delhi", "modi", "rajnath"],
            "China": ["china", "chinese", "beijing", "xi jinping", "pla"],
            "Pakistan": ["pakistan", "pakistani", "islamabad", "rawalpindi"],
            "Russia": ["russia", "russian", "moscow", "putin", "kremlin"],
            "USA": ["usa", "united states", "america", "washington", "pentagon", "biden"],
            "Ukraine": ["ukraine", "ukrainian", "kyiv", "zelensky"],
            "Taiwan": ["taiwan", "taiwanese", "taipei"],
            "Iran": ["iran", "iranian", "tehran", "khamenei"],
            "Israel": ["israel", "israeli", "tel aviv", "netanyahu", "idf"],
            "North Korea": ["north korea", "dprk", "pyongyang", "kim jong"],
            "Japan": ["japan", "japanese", "tokyo"],
        }
        for ctry, keywords in country_keywords.items():
            if any(kw in text for kw in keywords):
                country = ctry
                break

        # Theme detection
        theme = "General Security"
        theme_keywords = {
            "Great Power Competition": ["great power", "superpower", "hegemony", "rivalry", "strategic competition"],
            "Border Security": ["border", "lac", "loc", "incursion", "infiltration", "territorial"],
            "Maritime Security": ["maritime", "navy", "naval", "ship", "submarine", "carrier", "south china sea", "indian ocean"],
            "Defense Technology": ["missile", "hypersonic", "drone", "uav", "fighter jet", "weapon", "s-400", "f-35", "rafale"],
            "Nuclear Affairs": ["nuclear", "atomic", "warhead", "icbm", "ballistic", "nonproliferation"],
            "Terrorism": ["terror", "terrorist", "extremist", "militant", "isis", "al-qaeda", "taliban"],
            "Cyber Security": ["cyber", "hacking", "malware", "ransomware", "digital attack"],
            "Space": ["satellite", "space", "orbit", "anti-satellite", "asat"],
            "Diplomacy": ["summit", "treaty", "agreement", "bilateral", "talks", "diplomatic"],
            "Economic Security": ["sanctions", "trade war", "tariff", "embargo", "economic warfare"],
        }
        for thm, keywords in theme_keywords.items():
            if any(kw in text for kw in keywords):
                theme = thm
                break

        # Domain detection
        domain = "multi-domain"
        domain_keywords = {
            "land": ["army", "ground", "tank", "artillery", "infantry", "border"],
            "maritime": ["navy", "naval", "ship", "submarine", "maritime", "fleet"],
            "air": ["air force", "fighter", "aircraft", "bomber", "airspace"],
            "cyber": ["cyber", "hacking", "digital", "network"],
            "space": ["satellite", "space", "orbit"],
            "nuclear": ["nuclear", "atomic", "warhead"],
            "diplomatic": ["diplomatic", "summit", "treaty", "ambassador"],
        }
        for dom, keywords in domain_keywords.items():
            if any(kw in text for kw in keywords):
                domain = dom
                break

        return {
            "region": region,
            "country": country,
            "theme": theme,
            "domain": domain
        }


# Singleton instance
_scorer: RelevanceScorer = None


def get_relevance_scorer() -> RelevanceScorer:
    """Get or create relevance scorer instance"""
    global _scorer
    if _scorer is None:
        _scorer = RelevanceScorer()
    return _scorer
