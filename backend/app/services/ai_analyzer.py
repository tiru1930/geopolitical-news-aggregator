import json
import logging
from typing import Dict, Any, Optional
from groq import Groq
import httpx
from app.config import settings

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """
    AI service for generating strategic analysis of news articles.
    Supports Groq API (free tier) with easy switch to Ollama for local deployment.
    """

    def __init__(self):
        self.provider = settings.llm_provider
        self.model = settings.llm_model

        if self.provider == "groq":
            self.client = Groq(api_key=settings.groq_api_key)
        elif self.provider == "ollama":
            self.ollama_url = settings.ollama_base_url

    def _call_groq(self, prompt: str, system_prompt: str) -> str:
        """Call Groq API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise

    def _call_ollama(self, prompt: str, system_prompt: str) -> str:
        """Call local Ollama instance"""
        try:
            response = httpx.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"{system_prompt}\n\n{prompt}",
                    "stream": False
                },
                timeout=120.0
            )
            return response.json()["response"]
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            raise

    def _call_llm(self, prompt: str, system_prompt: str) -> str:
        """Call the configured LLM provider"""
        if self.provider == "groq":
            return self._call_groq(prompt, system_prompt)
        elif self.provider == "ollama":
            return self._call_ollama(prompt, system_prompt)
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")

    def generate_bullet_summary(self, title: str, content: str) -> str:
        """
        Generate a concise 5-line bullet point summary of the news article.

        Returns:
            String with bullet points separated by newlines
        """
        system_prompt = """You are a news summarizer. Create concise, factual bullet point summaries.
Keep each bullet point brief (max 15 words). Focus on key facts only."""

        prompt = f"""Summarize this news article in exactly 5 bullet points.

Title: {title}

Content: {content[:2500]}

Rules:
- Exactly 5 bullet points
- Each bullet starts with "• "
- Max 15 words per bullet
- Focus on: Who, What, Where, When, Why/Impact
- Be factual, no opinions
- No attribution needed

Example format:
• First key point about the news
• Second important fact
• Third relevant detail
• Fourth significant point
• Fifth takeaway or impact

Respond with ONLY the 5 bullet points, nothing else:"""

        try:
            response = self._call_llm(prompt, system_prompt)

            # Clean up response
            lines = response.strip().split('\n')
            bullets = []
            for line in lines:
                line = line.strip()
                if line:
                    # Ensure bullet format
                    if not line.startswith('•'):
                        line = '• ' + line.lstrip('- *>')
                    bullets.append(line)

            # Take only first 5 bullets
            bullets = bullets[:5]

            return '\n'.join(bullets) if bullets else ""
        except Exception as e:
            logger.error(f"Error generating bullet summary: {e}")
            return ""

    def generate_strategic_summary(self, title: str, content: str) -> Dict[str, str]:
        """
        Generate a structured strategic summary for a news article.

        Returns:
            Dict with keys: bullets, what_happened, why_matters, india_implications, future_developments
        """
        # First generate bullet summary
        bullets = self.generate_bullet_summary(title, content)

        system_prompt = """You are a strategic analyst specializing in geopolitical and defense affairs.
Your task is to analyze news articles and provide concise, professional summaries suitable for
defense analysts, military officers, and policy researchers.

Focus on:
- Factual accuracy
- Strategic implications
- Relevance to India's security environment
- Professional, briefing-style language

Always respond in valid JSON format."""

        prompt = f"""Analyze this news article and provide a structured strategic summary.

Title: {title}

Content: {content[:3000]}

Respond with a JSON object containing exactly these four keys:
{{
    "what_happened": "A concise 2-3 sentence factual summary of the event",
    "why_matters": "Strategic context and significance (2-3 sentences)",
    "india_implications": "Specific implications for India's security, diplomacy, or interests (2-3 sentences)",
    "future_developments": "Likely next steps or developments to watch (2-3 sentences)"
}}

If the article has no relevance to India, still provide analysis but note limited direct implications."""

        try:
            response = self._call_llm(prompt, system_prompt)

            # Parse JSON response
            # Try to extract JSON from response
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]

            result = json.loads(response.strip())

            return {
                "bullets": bullets,
                "what_happened": result.get("what_happened", ""),
                "why_matters": result.get("why_matters", ""),
                "india_implications": result.get("india_implications", ""),
                "future_developments": result.get("future_developments", "")
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            # Return empty summary on parse error
            return {
                "bullets": bullets,
                "what_happened": "",
                "why_matters": "",
                "india_implications": "",
                "future_developments": ""
            }
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            raise

    def extract_entities(self, title: str, content: str) -> list:
        """
        Extract named entities from the article.

        Returns:
            List of dicts with 'type' and 'name' keys
        """
        system_prompt = """You are an entity extraction specialist for geopolitical news.
Extract key entities and respond only with valid JSON."""

        prompt = f"""Extract key entities from this news article.

Title: {title}
Content: {content[:2000]}

Respond with a JSON array of entities:
[
    {{"type": "country", "name": "China"}},
    {{"type": "leader", "name": "Xi Jinping"}},
    {{"type": "organization", "name": "NATO"}},
    {{"type": "military", "name": "PLA Navy"}},
    {{"type": "location", "name": "South China Sea"}},
    {{"type": "weapon", "name": "Type 055 Destroyer"}}
]

Only include significant entities. Types: country, leader, organization, military, location, weapon, event"""

        try:
            response = self._call_llm(prompt, system_prompt)

            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]

            entities = json.loads(response.strip())
            return entities if isinstance(entities, list) else []
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return []

    # Valid values for classification
    VALID_REGIONS = ["South Asia", "East Asia", "Indo-Pacific", "Middle East", "Europe", "Africa", "Americas", "Central Asia", "Global"]
    VALID_THEMES = ["Great Power Competition", "Border Security", "Maritime Security", "Defense Technology", "Nuclear Affairs", "Terrorism", "Cyber Security", "Space", "Economic Security", "Diplomacy", "Internal Security", "General Security"]
    VALID_DOMAINS = ["land", "maritime", "air", "cyber", "space", "nuclear", "diplomatic", "economic", "multi-domain"]

    def _validate_and_normalize(self, value: str, valid_list: list, default: str) -> str:
        """Validate and normalize a classification value"""
        if not value or not isinstance(value, str):
            return default
        value = value.strip()
        # Exact match
        if value in valid_list:
            return value
        # Case-insensitive match
        for valid in valid_list:
            if value.lower() == valid.lower():
                return valid
        # Partial match
        for valid in valid_list:
            if value.lower() in valid.lower() or valid.lower() in value.lower():
                return valid
        return default

    def _normalize_country(self, country: str) -> str:
        """Normalize country names to standard format"""
        if not country or not isinstance(country, str):
            return ""
        country = country.strip()
        # Common normalizations
        normalizations = {
            "us": "USA", "u.s.": "USA", "u.s.a.": "USA", "united states": "USA", "america": "USA",
            "uk": "United Kingdom", "u.k.": "United Kingdom", "britain": "United Kingdom", "great britain": "United Kingdom",
            "prc": "China", "people's republic of china": "China",
            "rok": "South Korea", "republic of korea": "South Korea",
            "dprk": "North Korea", "democratic people's republic of korea": "North Korea",
            "uae": "UAE", "united arab emirates": "UAE",
            "ksa": "Saudi Arabia", "kingdom of saudi arabia": "Saudi Arabia",
        }
        lower = country.lower()
        if lower in normalizations:
            return normalizations[lower]
        return country

    def classify_article(self, title: str, content: str) -> Dict[str, str]:
        """
        Classify article by region, theme, and domain.

        Returns:
            Dict with keys: region, country, theme, domain
        """
        system_prompt = """You are a geopolitical classification specialist.
Classify news articles into predefined categories. Respond only with valid JSON.
IMPORTANT: You MUST choose values from the exact lists provided. Do not make up new categories."""

        prompt = f"""Classify this news article.

Title: {title}
Content: {content[:2000]}

Respond with a JSON object. You MUST use these exact values:

{{
    "region": "MUST be one of: South Asia, East Asia, Indo-Pacific, Middle East, Europe, Africa, Americas, Central Asia, Global",
    "country": "The PRIMARY country this article is about. Use standard names: India, China, Pakistan, USA, Russia, Ukraine, Israel, Iran, etc. If multiple countries, pick the main one.",
    "theme": "MUST be one of: Great Power Competition, Border Security, Maritime Security, Defense Technology, Nuclear Affairs, Terrorism, Cyber Security, Space, Economic Security, Diplomacy, Internal Security",
    "domain": "MUST be one of: land, maritime, air, cyber, space, nuclear, diplomatic, economic, multi-domain"
}}

If unsure about country, analyze which country is the PRIMARY subject of the article."""

        try:
            response = self._call_llm(prompt, system_prompt)

            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]

            result = json.loads(response.strip())

            # Validate and normalize all fields
            region = self._validate_and_normalize(result.get("region", ""), self.VALID_REGIONS, "Global")
            country = self._normalize_country(result.get("country", ""))
            theme = self._validate_and_normalize(result.get("theme", ""), self.VALID_THEMES, "General Security")
            domain = self._validate_and_normalize(result.get("domain", ""), self.VALID_DOMAINS, "multi-domain")

            return {
                "region": region,
                "country": country,
                "theme": theme,
                "domain": domain
            }
        except Exception as e:
            logger.error(f"Error classifying article: {e}")
            return {
                "region": "Global",
                "country": "",
                "theme": "General Security",
                "domain": "multi-domain"
            }

    def analyze_article(self, title: str, content: str) -> Dict[str, Any]:
        """
        Full analysis of an article: summary, entities, and classification.
        """
        summary = self.generate_strategic_summary(title, content)
        entities = self.extract_entities(title, content)
        classification = self.classify_article(title, content)

        return {
            "summary": summary,
            "entities": entities,
            "classification": classification
        }


# Singleton instance
_analyzer: Optional[AIAnalyzer] = None


def get_ai_analyzer() -> AIAnalyzer:
    """Get or create AI analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = AIAnalyzer()
    return _analyzer
