"""
LLM-based Relevance Scoring

Uses Groq API to intelligently score and categorize news articles
for strategic/geopolitical relevance. Much more accurate than keyword matching.
"""

import json
import logging
import time
from typing import Dict, Optional
from groq import Groq
from app.config import settings

logger = logging.getLogger(__name__)

# Rate limiting
_last_call_time = 0
_min_call_interval = 0.5  # Min 500ms between calls to avoid rate limits

# Priority countries - any news involving these should be HIGH relevance
PRIORITY_COUNTRIES = [
    "Pakistan", "China", "Bangladesh", "Nepal", "Sri Lanka",
    "Myanmar", "Afghanistan", "Maldives", "Bhutan"
]

# Strategic topics that should be HIGH relevance
STRATEGIC_TOPICS = [
    "military", "defence", "defense", "army", "navy", "air force",
    "border", "territorial", "sovereignty", "war", "conflict",
    "nuclear", "missile", "weapons", "ammunition", "arms deal",
    "terrorism", "insurgency", "militant", "extremist",
    "diplomatic", "bilateral", "treaty", "agreement", "summit",
    "sanctions", "trade war", "strategic partnership",
    "intelligence", "espionage", "cyber attack",
    "maritime", "south china sea", "indian ocean"
]

SCORING_PROMPT = """You are a strategic intelligence analyst specializing in India's national security and geopolitical interests.

Analyze this news article and provide a JSON response with the following:

1. **relevance_score** (0.0 to 1.0): How strategically important is this for India?
   - 0.8-1.0: Critical - Direct threat/opportunity for India, involving neighbors (Pakistan, China, Bangladesh), military action, border issues
   - 0.6-0.8: High - Regional security, defense deals, diplomatic developments with strategic partners
   - 0.4-0.6: Medium - Indirect implications, global security trends affecting India
   - 0.2-0.4: Low - Minor relevance, distant events with limited impact
   - 0.0-0.2: Minimal - No strategic relevance

2. **relevance_level**: "high" (>=0.5), "medium" (0.25-0.5), or "low" (<0.25)

3. **priority_reason**: Brief explanation of why this matters (or doesn't) for India

4. **classification**:
   - region: Geographic region (South Asia, East Asia, Indo-Pacific, Middle East, Europe, Central Asia, Africa, Americas, Global)
   - country: Primary country involved
   - theme: Main theme (Border Security, Maritime Security, Defense Technology, Nuclear Affairs, Terrorism, Cyber Security, Diplomacy, Economic Security, Great Power Competition, Regional Stability)
   - domain: Domain (land, maritime, air, cyber, space, nuclear, diplomatic, economic, multi-domain)

5. **involves_priority_country**: true/false - Does this involve Pakistan, China, Bangladesh, Nepal, Sri Lanka, Myanmar, Afghanistan, or Maldives?

6. **is_india_relevant**: true/false - Does this have any relevance to India's interests?

IMPORTANT RULES:
- Any military/defense news involving Pakistan, China, or Bangladesh = HIGH relevance (0.7+)
- Any border/territorial issues with neighbors = HIGH relevance (0.8+)
- Terror attacks in South Asia = HIGH relevance (0.7+)
- Arms deals, military exercises with/near India = HIGH relevance (0.6+)
- US-China, US-Russia tensions affecting Indo-Pacific = MEDIUM-HIGH (0.5+)
- Sports, entertainment, business (non-strategic) = LOW (0.1-0.2)

Article Title: {title}

Article Content: {content}

Respond ONLY with valid JSON, no other text:
"""


class LLMScorer:
    """
    LLM-based strategic relevance scorer using Groq API.
    Falls back to keyword-based scoring if LLM fails.
    """

    def __init__(self):
        self.client = None
        self.model = settings.llm_model
        if settings.groq_api_key:
            self.client = Groq(api_key=settings.groq_api_key)

    def _quick_priority_check(self, text: str) -> bool:
        """Quick check if text mentions priority countries"""
        text_lower = text.lower()
        for country in PRIORITY_COUNTRIES:
            if country.lower() in text_lower:
                return True
        return False

    def _quick_strategic_check(self, text: str) -> bool:
        """Quick check if text mentions strategic topics"""
        text_lower = text.lower()
        for topic in STRATEGIC_TOPICS:
            if topic in text_lower:
                return True
        return False

    def score_article(self, title: str, content: str = "") -> Dict:
        """
        Score an article using LLM for intelligent relevance assessment.

        Returns:
            Dict with relevance_score, relevance_level, classification, etc.
        """
        full_text = f"{title} {content or ''}"

        # Quick checks for priority content
        has_priority_country = self._quick_priority_check(full_text)
        has_strategic_topic = self._quick_strategic_check(full_text)

        # Default response (fallback)
        default_response = {
            "relevance_score": 0.3 if has_priority_country else 0.1,
            "relevance_level": "medium" if has_priority_country else "low",
            "priority_reason": "Keyword-based fallback scoring",
            "classification": {
                "region": "Global",
                "country": "",
                "theme": "General Security",
                "domain": "multi-domain"
            },
            "involves_priority_country": has_priority_country,
            "is_india_relevant": has_priority_country or has_strategic_topic
        }

        if not self.client:
            logger.warning("Groq client not initialized, using fallback scoring")
            return default_response

        try:
            # Rate limiting
            global _last_call_time
            elapsed = time.time() - _last_call_time
            if elapsed < _min_call_interval:
                time.sleep(_min_call_interval - elapsed)
            _last_call_time = time.time()
            # Truncate content to avoid token limits
            truncated_content = content[:3000] if content else ""

            prompt = SCORING_PROMPT.format(
                title=title,
                content=truncated_content or "(No content available, score based on title)"
            )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a strategic intelligence analyst. Respond only with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent scoring
                max_tokens=500
            )

            result_text = response.choices[0].message.content.strip()

            # Parse JSON response
            # Handle potential markdown code blocks
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]

            result = json.loads(result_text)

            # Validate and normalize response
            relevance_score = float(result.get("relevance_score", 0.3))
            relevance_score = max(0.0, min(1.0, relevance_score))

            # Boost score if priority country is involved but LLM scored low
            if has_priority_country and relevance_score < 0.5:
                relevance_score = max(relevance_score, 0.5)
                result["priority_reason"] = f"Boosted: involves priority country. {result.get('priority_reason', '')}"

            # Determine level from score
            if relevance_score >= 0.5:
                relevance_level = "high"
            elif relevance_score >= 0.25:
                relevance_level = "medium"
            else:
                relevance_level = "low"

            return {
                "relevance_score": round(relevance_score, 3),
                "relevance_level": relevance_level,
                "priority_reason": result.get("priority_reason", ""),
                "classification": result.get("classification", default_response["classification"]),
                "involves_priority_country": result.get("involves_priority_country", has_priority_country),
                "is_india_relevant": result.get("is_india_relevant", True)
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            return default_response
        except Exception as e:
            logger.error(f"LLM scoring failed: {e}")
            return default_response

    def batch_score(self, articles: list) -> list:
        """Score multiple articles (for batch processing)"""
        results = []
        for article in articles:
            title = article.get("title", "")
            content = article.get("content", "")
            result = self.score_article(title, content)
            result["article_id"] = article.get("id")
            results.append(result)
        return results


# Singleton instance
_llm_scorer: LLMScorer = None


def get_llm_scorer() -> LLMScorer:
    """Get or create LLM scorer instance"""
    global _llm_scorer
    if _llm_scorer is None:
        _llm_scorer = LLMScorer()
    return _llm_scorer
