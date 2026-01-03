"""
Additional News Sources Configuration

To add these sources, call the API endpoint:
POST /api/sources/ with the source data

Or run: python -m app.services.additional_sources
"""

ADDITIONAL_RSS_SOURCES = [
    # === Indian Sources ===
    {
        "name": "IDSA - Institute for Defence Studies",
        "url": "https://www.idsa.in",
        "feed_url": "https://www.idsa.in/rss/idsa-comments.xml",
        "source_type": "rss",
        "category": "think_tank",
        "country": "India",
        "reliability_score": 9,
        "description": "Premier Indian defence think tank"
    },
    {
        "name": "ORF - Observer Research Foundation",
        "url": "https://www.orfonline.org",
        "feed_url": "https://www.orfonline.org/feed/",
        "source_type": "rss",
        "category": "think_tank",
        "country": "India",
        "reliability_score": 8,
        "description": "Indian policy research think tank"
    },
    {
        "name": "Indian Express - Defence",
        "url": "https://indianexpress.com",
        "feed_url": "https://indianexpress.com/section/india/feed/",
        "source_type": "rss",
        "category": "news_agency",
        "country": "India",
        "reliability_score": 8
    },
    {
        "name": "Hindustan Times - World",
        "url": "https://www.hindustantimes.com",
        "feed_url": "https://www.hindustantimes.com/feeds/rss/world-news/rssfeed.xml",
        "source_type": "rss",
        "category": "news_agency",
        "country": "India",
        "reliability_score": 7
    },

    # === International Think Tanks ===
    {
        "name": "Brookings Institution",
        "url": "https://www.brookings.edu",
        "feed_url": "https://www.brookings.edu/feed/",
        "source_type": "rss",
        "category": "think_tank",
        "country": "USA",
        "reliability_score": 9
    },
    {
        "name": "RAND Corporation",
        "url": "https://www.rand.org",
        "feed_url": "https://www.rand.org/feeds/content.xml",
        "source_type": "rss",
        "category": "think_tank",
        "country": "USA",
        "reliability_score": 9
    },
    {
        "name": "Carnegie Endowment",
        "url": "https://carnegieendowment.org",
        "feed_url": "https://carnegieendowment.org/rss/feeds/articles.xml",
        "source_type": "rss",
        "category": "think_tank",
        "country": "USA",
        "reliability_score": 9
    },
    {
        "name": "IISS - International Institute for Strategic Studies",
        "url": "https://www.iiss.org",
        "feed_url": "https://www.iiss.org/rss",
        "source_type": "rss",
        "category": "think_tank",
        "country": "UK",
        "reliability_score": 9
    },
    {
        "name": "Chatham House",
        "url": "https://www.chathamhouse.org",
        "feed_url": "https://www.chathamhouse.org/rss.xml",
        "source_type": "rss",
        "category": "think_tank",
        "country": "UK",
        "reliability_score": 9
    },

    # === Defence Publications ===
    {
        "name": "Jane's Defence",
        "url": "https://www.janes.com",
        "feed_url": "https://www.janes.com/feeds/news",
        "source_type": "rss",
        "category": "military",
        "country": "UK",
        "reliability_score": 9
    },
    {
        "name": "Military Times",
        "url": "https://www.militarytimes.com",
        "feed_url": "https://www.militarytimes.com/arc/outboundfeeds/rss/?outputType=xml",
        "source_type": "rss",
        "category": "military",
        "country": "USA",
        "reliability_score": 8
    },
    {
        "name": "War on the Rocks",
        "url": "https://warontherocks.com",
        "feed_url": "https://warontherocks.com/feed/",
        "source_type": "rss",
        "category": "think_tank",
        "country": "USA",
        "reliability_score": 8
    },

    # === Regional News ===
    {
        "name": "Nikkei Asia",
        "url": "https://asia.nikkei.com",
        "feed_url": "https://asia.nikkei.com/rss/feed/nar",
        "source_type": "rss",
        "category": "news_agency",
        "country": "Japan",
        "reliability_score": 8
    },
    {
        "name": "Channel News Asia",
        "url": "https://www.channelnewsasia.com",
        "feed_url": "https://www.channelnewsasia.com/rssfeeds/8395986",
        "source_type": "rss",
        "category": "news_agency",
        "country": "Singapore",
        "reliability_score": 8
    },
    {
        "name": "Dawn - Pakistan",
        "url": "https://www.dawn.com",
        "feed_url": "https://www.dawn.com/feeds/home",
        "source_type": "rss",
        "category": "news_agency",
        "country": "Pakistan",
        "reliability_score": 7
    },
    {
        "name": "Global Times - China",
        "url": "https://www.globaltimes.cn",
        "feed_url": "https://www.globaltimes.cn/rss/outbrain.xml",
        "source_type": "rss",
        "category": "news_agency",
        "country": "China",
        "reliability_score": 5,
        "bias_rating": "state-affiliated"
    },

    # === Wire Services ===
    {
        "name": "Associated Press",
        "url": "https://apnews.com",
        "feed_url": "https://rsshub.app/apnews/topics/apf-topnews",
        "source_type": "rss",
        "category": "news_agency",
        "country": "USA",
        "reliability_score": 9
    },
    {
        "name": "AFP - Agence France-Presse",
        "url": "https://www.afp.com",
        "feed_url": "https://www.afp.com/en/feed",
        "source_type": "rss",
        "category": "news_agency",
        "country": "France",
        "reliability_score": 9
    },

    # === Government Sources ===
    {
        "name": "US State Department",
        "url": "https://www.state.gov",
        "feed_url": "https://www.state.gov/rss-feed/press-releases/feed/",
        "source_type": "rss",
        "category": "government",
        "country": "USA",
        "reliability_score": 8
    },
    {
        "name": "UK Foreign Office",
        "url": "https://www.gov.uk/government/organisations/foreign-commonwealth-development-office",
        "feed_url": "https://www.gov.uk/government/organisations/foreign-commonwealth-development-office.atom",
        "source_type": "rss",
        "category": "government",
        "country": "UK",
        "reliability_score": 8
    },
    {
        "name": "MEA India",
        "url": "https://www.mea.gov.in",
        "feed_url": "https://www.mea.gov.in/rss-feeds.htm",
        "source_type": "rss",
        "category": "government",
        "country": "India",
        "reliability_score": 9
    },
]


def seed_additional_sources(db):
    """Add additional sources to database"""
    from app.models.source import Source, SourceType, SourceCategory

    added = 0
    for source_data in ADDITIONAL_RSS_SOURCES:
        existing = db.query(Source).filter(Source.name == source_data["name"]).first()
        if not existing:
            source = Source(
                name=source_data["name"],
                url=source_data["url"],
                feed_url=source_data.get("feed_url"),
                source_type=SourceType(source_data.get("source_type", "rss")),
                category=SourceCategory(source_data.get("category", "news_agency")),
                country=source_data.get("country"),
                reliability_score=source_data.get("reliability_score", 5),
                bias_rating=source_data.get("bias_rating"),
                description=source_data.get("description"),
                is_active=True
            )
            db.add(source)
            added += 1

    db.commit()
    return added


if __name__ == "__main__":
    from app.database import SessionLocal
    db = SessionLocal()
    count = seed_additional_sources(db)
    print(f"Added {count} new sources")
    db.close()
