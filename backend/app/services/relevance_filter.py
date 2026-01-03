"""
Pre-fetch Relevance Filter

Filters articles BEFORE saving to database.
Only keeps articles related to:
- Defence / Military
- Security / Intelligence
- Terrorism / Extremism
- Geopolitics / Strategic Affairs
- Border issues / Territorial disputes

Discards:
- Sports, Entertainment, Lifestyle
- General Finance / Business (unless defence deals)
- Celebrity news, Weather, etc.
"""

import re
from typing import Tuple

# Keywords that MUST be present (at least one) - case insensitive
INCLUDE_KEYWORDS = [
    # Military & Defence
    r'\bmilitary\b', r'\bdefence\b', r'\bdefense\b', r'\barmy\b', r'\bnavy\b',
    r'\bair\s*force\b', r'\bairforce\b', r'\bmarines\b', r'\btroops\b',
    r'\bsoldier', r'\bwarship', r'\bsubmarine', r'\baircraft\s*carrier',
    r'\bfighter\s*jet', r'\bdrone', r'\bUAV\b', r'\bmissile', r'\brocket',
    r'\bartillery\b', r'\btank\b', r'\bammunition\b', r'\bweapon',
    r'\bnuclear\b', r'\bballistic\b', r'\bhypersonic\b', r'\bcruise\s*missile',
    r'\bICBM\b', r'\bwarhead\b', r'\batomic\b',

    # Security & Intelligence
    r'\bsecurity\b', r'\bintelligence\b', r'\bespionage\b', r'\bspy\b',
    r'\bcyber\s*attack', r'\bcyber\s*security', r'\bhacking\b', r'\bhacker',
    r'\bsurveillance\b', r'\bcovert\b', r'\bsecret\s*service',
    r'\bCIA\b', r'\bFBI\b', r'\bMI6\b', r'\bMossad\b', r'\bISI\b', r'\bRAW\b',
    r'\bNSA\b', r'\bFSB\b', r'\bSVR\b',

    # Terrorism & Extremism
    r'\bterror', r'\bterrorist', r'\bjihad', r'\bextremis', r'\bradical',
    r'\bISIS\b', r'\bISIL\b', r'\bIslamic\s*State\b', r'\bAl[\s\-]?Qaeda',
    r'\bTaliban\b', r'\bBoko\s*Haram\b', r'\bHezbollah\b', r'\bHamas\b',
    r'\bLashkar', r'\bJaish', r'\bHizbul\b', r'\bmilitant', r'\binsurgent',
    r'\bbombing\b', r'\bexplosion\b', r'\bsuicide\s*attack', r'\bIED\b',
    r'\bhostage\b', r'\bkidnap', r'\babduct',

    # Geopolitics & Strategy
    r'\bgeopolitic', r'\bstrateg', r'\bdiplomat', r'\bforeign\s*policy',
    r'\bsanction', r'\bembargo\b', r'\btreaty\b', r'\balliance\b',
    r'\bNATO\b', r'\bQUAD\b', r'\bASEAN\b', r'\bSCO\b', r'\bBRICS\b',
    r'\bUN\s*Security\s*Council', r'\bUnited\s*Nations\b',
    r'\bbilateral\b', r'\bmultilateral\b', r'\bsummit\b',

    # Border & Territory
    r'\bborder\b', r'\bterritorial\b', r'\bsovereignty\b', r'\bannex',
    r'\boccup', r'\binvasion\b', r'\binvade', r'\bLAC\b', r'\bLOC\b',
    r'\bdisputed\b', r'\bceasefire\b', r'\bstandoff\b', r'\bskirmish',
    r'\bincursion\b', r'\binfiltrat', r'\bcross[\s\-]?border',

    # Conflict & War
    r'\bwar\b', r'\bwarfare\b', r'\bconflict\b', r'\bcombat\b',
    r'\bbattle\b', r'\bclash', r'\bfighting\b', r'\bhostilities\b',
    r'\boffensive\b', r'\bdefensive\b', r'\baisstrike', r'\bair\s*strike',
    r'\bground\s*operation', r'\bmilitary\s*operation',

    # Countries of Strategic Interest
    r'\bIndia\b.*(?:China|Pakistan|military|border|defence)',
    r'\bChina\b.*(?:military|Taiwan|India|South\s*China\s*Sea)',
    r'\bPakistan\b.*(?:India|terror|military|nuclear)',
    r'\bRussia\b.*(?:Ukraine|NATO|military|nuclear)',
    r'\bUkraine\b', r'\bTaiwan\b', r'\bNorth\s*Korea\b', r'\bIran\b.*(?:nuclear|military)',
    r'\bSouth\s*China\s*Sea\b', r'\bIndo[\s\-]?Pacific\b',
    r'\bMiddle\s*East\b.*(?:conflict|military|Iran|Israel)',
    r'\bIsrael\b.*(?:Hamas|Gaza|military|Iran|Hezbollah)',
    r'\bGaza\b', r'\bWest\s*Bank\b',

    # Defence Industry & Deals
    r'\bdefence\s*deal', r'\bdefense\s*deal', r'\barms\s*deal',
    r'\bweapons\s*sale', r'\bmilitary\s*aid', r'\bdefence\s*contract',
    r'\bLockheed', r'\bBoeing\b.*(?:military|defence|fighter)',
    r'\bRaytheon\b', r'\bNorthrop\b', r'\bBAE\s*Systems',
    r'\bRafale\b', r'\bS[\s\-]?400\b', r'\bF[\s\-]?35\b', r'\bF[\s\-]?16\b',

    # Leaders in strategic context
    r'\bPutin\b', r'\bXi\s*Jinping\b', r'\bZelensky\b', r'\bKim\s*Jong',
    r'\bNetanyahu\b', r'\bKhamenei\b',
]

# Keywords that should EXCLUDE articles (unless override by strong include)
EXCLUDE_KEYWORDS = [
    # Sports
    r'\bcricket\b', r'\bfootball\b', r'\bsoccer\b', r'\btennis\b',
    r'\bolympic', r'\bworld\s*cup\b', r'\bIPL\b', r'\bpremier\s*league',
    r'\bchampionship\b', r'\btournament\b', r'\bmatch\b.*(?:score|win|lose)',
    r'\bgoal\b.*(?:scored|match)', r'\bwicket', r'\brun\s*chase',

    # Entertainment
    r'\bbollywood\b', r'\bhollywood\b', r'\bmovie\b', r'\bfilm\b.*(?:release|review)',
    r'\bactor\b', r'\bactress\b', r'\bcelebrit', r'\bsinger\b',
    r'\balbum\b', r'\bconcert\b', r'\bmusic\b.*(?:release|chart)',
    r'\bNetflix\b', r'\bstreaming\b',

    # Lifestyle
    r'\brecipe\b', r'\bcooking\b', r'\bfashion\b', r'\bbeauty\b',
    r'\bwedding\b', r'\bparty\b', r'\bhoroscope\b', r'\bzodiac\b',
    r'\bweight\s*loss', r'\bdiet\b', r'\bfitness\b',

    # General Business (not defence)
    r'\bstock\s*market\b', r'\bsensex\b', r'\bnifty\b', r'\bshare\s*price',
    r'\bIPO\b', r'\bquarterly\s*results', r'\bearnings\b',
    r'\breal\s*estate\b', r'\bproperty\b.*(?:price|buy|sell)',

    # Weather & Misc
    r'\bweather\b', r'\bforecast\b', r'\brain\b.*(?:expected|heavy)',
    r'\btemperature\b', r'\bheatwave\b',
]

# Strong include keywords that override exclusions
STRONG_INCLUDE = [
    r'\bterror', r'\bmilitary\b', r'\bnuclear\b', r'\bmissile\b',
    r'\bwar\b', r'\binvasion\b', r'\battack\b.*(?:terror|military|drone)',
    r'\bdefence\b', r'\bdefense\b', r'\barmy\b', r'\bnavy\b',
]


def is_relevant_article(title: str, content: str = None) -> Tuple[bool, str]:
    """
    Check if an article is relevant to strategic/defence topics.

    Returns:
        (is_relevant, reason)
    """
    text = (title or "") + " " + (content or "")
    text_lower = text.lower()

    # Check for strong include first
    for pattern in STRONG_INCLUDE:
        if re.search(pattern, text_lower):
            return True, "Strong match: strategic/defence content"

    # Check for exclusions
    for pattern in EXCLUDE_KEYWORDS:
        if re.search(pattern, text_lower):
            # Check if there's a strong include that overrides
            has_override = any(re.search(p, text_lower) for p in STRONG_INCLUDE)
            if not has_override:
                return False, f"Excluded: matches non-strategic pattern"

    # Check for include keywords
    for pattern in INCLUDE_KEYWORDS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True, "Matches strategic keywords"

    # Default: not relevant enough
    return False, "No strategic keywords found"


def filter_articles(articles: list, title_key: str = "title", content_key: str = "content") -> list:
    """
    Filter a list of article dicts, keeping only relevant ones.

    Args:
        articles: List of article dicts
        title_key: Key for title in dict
        content_key: Key for content in dict

    Returns:
        Filtered list of relevant articles
    """
    relevant = []
    for article in articles:
        title = article.get(title_key, "")
        content = article.get(content_key, "") or article.get("description", "")

        is_relevant, reason = is_relevant_article(title, content)
        if is_relevant:
            relevant.append(article)

    return relevant
