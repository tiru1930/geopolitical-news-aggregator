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

    # HIGHEST PRIORITY - India and immediate neighbors (always prioritize)
    INDIA_NEIGHBORS = [
        "india", "indian", "pakistan", "pakistani", "china", "chinese",
        "bangladesh", "bangladeshi", "nepal", "nepalese", "nepali",
        "sri lanka", "sri lankan", "myanmar", "burmese",
        "afghanistan", "afghan", "maldives", "maldivian", "bhutan", "bhutanese"
    ]

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
        """Count high, medium, and low priority keyword matches using word boundaries"""
        text_lower = text.lower()

        def count_with_boundary(keyword_list):
            count = 0
            for kw in keyword_list:
                # Use word boundary matching to avoid false positives
                pattern = r'\b' + re.escape(kw) + r'\b'
                if re.search(pattern, text_lower):
                    count += 1
            return count

        high_count = count_with_boundary(keywords.get("high", []))
        medium_count = count_with_boundary(keywords.get("medium", []))
        low_count = count_with_boundary(keywords.get("low", []))

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

    def _is_india_neighbor_article(self, text: str) -> bool:
        """Check if article mentions India or its neighbors"""
        text_lower = text.lower()
        for keyword in self.INDIA_NEIGHBORS:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text_lower):
                return True
        return False

    def calculate_scores(self, title: str, content: str) -> Dict[str, float]:
        """
        Calculate all relevance scores for an article.

        Returns:
            Dict with geo_score, military_score, diplomatic_score,
            economic_score, relevance_score, relevance_level, and is_priority
        """
        full_text = f"{title} {content}"

        # Check if this is about India or neighbors (HIGHEST PRIORITY)
        is_priority = self._is_india_neighbor_article(full_text)

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

        # BOOST score for India and neighbors - these are always priority
        if is_priority:
            relevance_score = max(relevance_score, 0.4)  # Minimum score for priority countries
            # Additional boost if military/security related
            if military_score > 0.1:
                relevance_score = max(relevance_score, 0.6)

        relevance_score = round(min(relevance_score, 1.0), 3)

        # Determine relevance level (adjusted thresholds)
        if relevance_score >= 0.3 or is_priority:
            relevance_level = "high" if relevance_score >= 0.3 else "medium"
        elif relevance_score >= 0.15:
            relevance_level = "medium"
        else:
            relevance_level = "low"

        # Priority articles are at least medium
        if is_priority and relevance_level == "low":
            relevance_level = "medium"

        return {
            "geo_score": geo_score,
            "military_score": military_score,
            "diplomatic_score": diplomatic_score,
            "economic_score": economic_score,
            "relevance_score": relevance_score,
            "relevance_level": relevance_level,
            "is_priority": is_priority
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

        # Region detection with word boundaries
        region = "Global"
        region_keywords = {
            "South Asia": ["india", "pakistan", "bangladesh", "nepal", "sri lanka", "bhutan", "maldives", "kashmir", "ladakh", "indian", "pakistani"],
            "East Asia": ["china", "japan", "korea", "taiwan", "hong kong", "beijing", "tokyo", "seoul", "pyongyang", "chinese", "japanese", "korean"],
            "Indo-Pacific": ["indo-pacific", "quad", "aukus", "pacific", "asean", "south china sea", "andaman", "indian ocean"],
            "Middle East": ["iran", "israel", "saudi", "uae", "iraq", "syria", "gaza", "yemen", "gulf", "lebanon", "jordan", "iranian", "israeli", "palestinian"],
            "Europe": ["nato", "russia", "ukraine", "eu", "european", "moscow", "kyiv", "london", "paris", "berlin", "russian", "ukrainian", "british", "french", "german"],
            "Central Asia": ["afghanistan", "kazakhstan", "uzbekistan", "tajikistan", "turkmenistan", "kyrgyzstan", "afghan"],
            "Africa": ["africa", "african", "egypt", "libya", "sudan", "ethiopia", "nigeria", "kenya", "south africa", "egyptian"],
            "Americas": ["america", "american", "usa", "washington", "pentagon", "canada", "mexico", "brazil", "canadian", "united states"],
        }
        for reg, keywords in region_keywords.items():
            for kw in keywords:
                pattern = r'\b' + re.escape(kw) + r'\b'
                if re.search(pattern, text):
                    region = reg
                    break
            if region != "Global":
                break

        # Country detection (primary) - expanded list
        country = ""
        country_keywords = {
            # South Asia
            "India": ["india", "indian", "delhi", "mumbai", "modi", "rajnath", "jaishankar", "new delhi"],
            "Pakistan": ["pakistan", "pakistani", "islamabad", "rawalpindi", "karachi", "lahore"],
            "Bangladesh": ["bangladesh", "bangladeshi", "dhaka", "hasina"],
            "Nepal": ["nepal", "nepalese", "nepali", "kathmandu"],
            "Sri Lanka": ["sri lanka", "sri lankan", "colombo", "srilanka"],
            "Maldives": ["maldives", "maldivian", "male"],
            "Bhutan": ["bhutan", "bhutanese", "thimphu"],
            "Afghanistan": ["afghanistan", "afghan", "kabul", "taliban"],
            # East Asia
            "China": ["china", "chinese", "beijing", "xi jinping", "pla", "ccp", "prc"],
            "Japan": ["japan", "japanese", "tokyo", "kishida"],
            "South Korea": ["south korea", "korean", "seoul", "rok"],
            "North Korea": ["north korea", "dprk", "pyongyang", "kim jong"],
            "Taiwan": ["taiwan", "taiwanese", "taipei"],
            "Mongolia": ["mongolia", "mongolian", "ulaanbaatar"],
            # Southeast Asia
            "Myanmar": ["myanmar", "burmese", "naypyidaw", "yangon", "burma"],
            "Thailand": ["thailand", "thai", "bangkok"],
            "Vietnam": ["vietnam", "vietnamese", "hanoi", "ho chi minh"],
            "Indonesia": ["indonesia", "indonesian", "jakarta"],
            "Malaysia": ["malaysia", "malaysian", "kuala lumpur"],
            "Philippines": ["philippines", "filipino", "manila", "marcos"],
            "Singapore": ["singapore", "singaporean"],
            "Cambodia": ["cambodia", "cambodian", "phnom penh"],
            # Middle East
            "Iran": ["iran", "iranian", "tehran", "khamenei", "raisi"],
            "Israel": ["israel", "israeli", "tel aviv", "netanyahu", "idf", "jerusalem"],
            "Palestine": ["palestine", "palestinian", "gaza", "west bank", "hamas"],
            "Saudi Arabia": ["saudi", "riyadh", "mbs", "saudi arabia"],
            "UAE": ["uae", "emirates", "dubai", "abu dhabi", "emirati"],
            "Turkey": ["turkey", "turkish", "ankara", "erdogan", "turkiye"],
            "Iraq": ["iraq", "iraqi", "baghdad"],
            "Syria": ["syria", "syrian", "damascus", "assad"],
            "Yemen": ["yemen", "yemeni", "sanaa", "houthi"],
            "Lebanon": ["lebanon", "lebanese", "beirut", "hezbollah"],
            "Jordan": ["jordan", "jordanian", "amman"],
            "Qatar": ["qatar", "qatari", "doha"],
            "Kuwait": ["kuwait", "kuwaiti"],
            "Oman": ["oman", "omani", "muscat"],
            "Bahrain": ["bahrain", "bahraini", "manama"],
            # Europe
            "Russia": ["russia", "russian", "moscow", "putin", "kremlin"],
            "Ukraine": ["ukraine", "ukrainian", "kyiv", "zelensky", "kiev"],
            "United Kingdom": ["britain", "british", "uk", "london", "england", "united kingdom"],
            "Germany": ["germany", "german", "berlin", "scholz"],
            "France": ["france", "french", "paris", "macron"],
            "Italy": ["italy", "italian", "rome"],
            "Poland": ["poland", "polish", "warsaw"],
            "Spain": ["spain", "spanish", "madrid"],
            "Netherlands": ["netherlands", "dutch", "amsterdam", "hague"],
            "Belgium": ["belgium", "belgian", "brussels"],
            "Greece": ["greece", "greek", "athens"],
            "Serbia": ["serbia", "serbian", "belgrade"],
            "Hungary": ["hungary", "hungarian", "budapest", "orban"],
            "Romania": ["romania", "romanian", "bucharest"],
            "Belarus": ["belarus", "belarusian", "minsk", "lukashenko"],
            "Finland": ["finland", "finnish", "helsinki"],
            "Sweden": ["sweden", "swedish", "stockholm"],
            "Norway": ["norway", "norwegian", "oslo"],
            # Americas
            "USA": ["usa", "united states", "america", "washington", "pentagon", "biden", "u.s.", "american"],
            "Canada": ["canada", "canadian", "ottawa", "trudeau"],
            "Mexico": ["mexico", "mexican", "mexico city"],
            "Brazil": ["brazil", "brazilian", "brasilia", "lula"],
            "Argentina": ["argentina", "argentine", "buenos aires"],
            "Colombia": ["colombia", "colombian", "bogota"],
            "Venezuela": ["venezuela", "venezuelan", "caracas", "maduro"],
            "Cuba": ["cuba", "cuban", "havana"],
            # Africa
            "Egypt": ["egypt", "egyptian", "cairo", "sisi"],
            "South Africa": ["south africa", "south african", "pretoria", "johannesburg"],
            "Nigeria": ["nigeria", "nigerian", "abuja", "lagos"],
            "Kenya": ["kenya", "kenyan", "nairobi"],
            "Ethiopia": ["ethiopia", "ethiopian", "addis ababa"],
            "Sudan": ["sudan", "sudanese", "khartoum"],
            "Libya": ["libya", "libyan", "tripoli"],
            "Morocco": ["morocco", "moroccan", "rabat"],
            "Algeria": ["algeria", "algerian", "algiers"],
            # Central Asia
            "Kazakhstan": ["kazakhstan", "kazakh", "astana", "almaty"],
            "Uzbekistan": ["uzbekistan", "uzbek", "tashkent"],
            "Turkmenistan": ["turkmenistan", "turkmen", "ashgabat"],
            "Tajikistan": ["tajikistan", "tajik", "dushanbe"],
            "Kyrgyzstan": ["kyrgyzstan", "kyrgyz", "bishkek"],
            # Oceania
            "Australia": ["australia", "australian", "canberra", "sydney"],
            "New Zealand": ["new zealand", "kiwi", "wellington", "auckland"],
        }

        # Use word boundary matching for country detection
        for ctry, keywords in country_keywords.items():
            for kw in keywords:
                pattern = r'\b' + re.escape(kw) + r'\b'
                if re.search(pattern, text):
                    country = ctry
                    break
            if country:
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
