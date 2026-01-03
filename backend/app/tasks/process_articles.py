import logging
from datetime import datetime, timedelta
from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.article import Article, RelevanceLevel
from app.services.ai_analyzer import get_ai_analyzer
from app.services.relevance_scorer import get_relevance_scorer
from app.services.llm_scorer import get_llm_scorer
from app.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.tasks.process_articles.process_pending_articles")
def process_pending_articles(self, batch_size: int = 10):
    """
    Process unprocessed articles: use LLM for intelligent relevance scoring and categorization.
    Runs every 5 minutes.
    """
    db = SessionLocal()
    try:
        # Get unprocessed articles
        articles = db.query(Article).filter(
            Article.is_processed == 0
        ).order_by(Article.created_at.desc()).limit(batch_size).all()

        if not articles:
            logger.info("No pending articles to process")
            return {"status": "success", "processed": 0}

        # Use LLM scorer for intelligent relevance assessment
        llm_scorer = get_llm_scorer() if settings.groq_api_key else None
        keyword_scorer = get_relevance_scorer()  # Fallback

        processed_count = 0
        llm_scored_count = 0
        ai_summarized_count = 0

        for article in articles:
            try:
                content = article.original_content or ""

                # Try LLM-based scoring first (more accurate)
                if llm_scorer and settings.groq_api_key:
                    try:
                        llm_result = llm_scorer.score_article(article.title, content)

                        # Update relevance from LLM
                        article.relevance_score = llm_result["relevance_score"]
                        article.relevance_level = RelevanceLevel(llm_result["relevance_level"])

                        # Update classification from LLM
                        classification = llm_result.get("classification", {})
                        article.region = classification.get("region", "Global")
                        article.country = classification.get("country", "")
                        article.theme = classification.get("theme", "General Security")
                        article.domain = classification.get("domain", "multi-domain")

                        # Calculate component scores using keywords (for display)
                        keyword_scores = keyword_scorer.calculate_scores(article.title, content)
                        article.geo_score = keyword_scores["geo_score"]
                        article.military_score = keyword_scores["military_score"]
                        article.diplomatic_score = keyword_scores["diplomatic_score"]
                        article.economic_score = keyword_scores["economic_score"]

                        llm_scored_count += 1
                        logger.debug(f"LLM scored article {article.id}: {llm_result['relevance_level']} ({llm_result['relevance_score']})")

                    except Exception as e:
                        logger.warning(f"LLM scoring failed for article {article.id}, using keywords: {e}")
                        # Fall back to keyword scoring
                        scores = keyword_scorer.calculate_scores(article.title, content)
                        article.geo_score = scores["geo_score"]
                        article.military_score = scores["military_score"]
                        article.diplomatic_score = scores["diplomatic_score"]
                        article.economic_score = scores["economic_score"]
                        article.relevance_score = scores["relevance_score"]
                        article.relevance_level = RelevanceLevel(scores["relevance_level"])

                        classification = keyword_scorer.extract_region_theme(article.title, content)
                        article.region = classification.get("region")
                        article.country = classification.get("country")
                        article.theme = classification.get("theme")
                        article.domain = classification.get("domain")
                else:
                    # No LLM available, use keyword scoring
                    scores = keyword_scorer.calculate_scores(article.title, content)
                    article.geo_score = scores["geo_score"]
                    article.military_score = scores["military_score"]
                    article.diplomatic_score = scores["diplomatic_score"]
                    article.economic_score = scores["economic_score"]
                    article.relevance_score = scores["relevance_score"]
                    article.relevance_level = RelevanceLevel(scores["relevance_level"])

                    classification = keyword_scorer.extract_region_theme(article.title, content)
                    article.region = classification.get("region")
                    article.country = classification.get("country")
                    article.theme = classification.get("theme")
                    article.domain = classification.get("domain")

                # Generate AI summaries for HIGH relevance articles
                if article.relevance_level == RelevanceLevel.HIGH and settings.groq_api_key:
                    try:
                        analyzer = get_ai_analyzer()
                        analysis = analyzer.analyze_article(article.title, content)

                        # Update summaries
                        summary = analysis.get("summary", {})
                        article.summary_what_happened = summary.get("what_happened", "")
                        article.summary_why_matters = summary.get("why_matters", "")
                        article.summary_india_implications = summary.get("india_implications", "")
                        article.summary_future_developments = summary.get("future_developments", "")

                        # Update entities
                        article.entities = analysis.get("entities", [])

                        ai_summarized_count += 1

                    except Exception as e:
                        logger.warning(f"AI summary failed for article {article.id}: {e}")

                article.is_processed = 1
                processed_count += 1

            except Exception as e:
                logger.error(f"Error processing article {article.id}: {e}")
                article.is_processed = 2  # Mark as failed
                article.processing_error = str(e)[:500]

        db.commit()

        logger.info(f"Processed {processed_count} articles: {llm_scored_count} LLM-scored, {ai_summarized_count} AI-summarized")

        return {
            "status": "success",
            "processed": processed_count,
            "llm_scored": llm_scored_count,
            "ai_summarized": ai_summarized_count
        }

    except Exception as e:
        logger.error(f"Error in process_pending_articles: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        db.close()


@celery_app.task(bind=True, name="app.tasks.process_articles.process_single_article")
def process_single_article(self, article_id: int):
    """
    Process a single article on demand.
    """
    db = SessionLocal()
    try:
        article = db.query(Article).filter(Article.id == article_id).first()

        if not article:
            return {"status": "error", "error": "Article not found"}

        scorer = get_relevance_scorer()
        analyzer = get_ai_analyzer()

        # Calculate relevance scores
        scores = scorer.calculate_scores(
            article.title,
            article.original_content or ""
        )

        article.geo_score = scores["geo_score"]
        article.military_score = scores["military_score"]
        article.diplomatic_score = scores["diplomatic_score"]
        article.economic_score = scores["economic_score"]
        article.relevance_score = scores["relevance_score"]
        article.relevance_level = RelevanceLevel(scores["relevance_level"])

        # AI analysis
        if settings.groq_api_key:
            analysis = analyzer.analyze_article(
                article.title,
                article.original_content or ""
            )

            summary = analysis.get("summary", {})
            article.summary_what_happened = summary.get("what_happened", "")
            article.summary_why_matters = summary.get("why_matters", "")
            article.summary_india_implications = summary.get("india_implications", "")
            article.summary_future_developments = summary.get("future_developments", "")

            classification = analysis.get("classification", {})
            article.region = classification.get("region")
            article.country = classification.get("country")
            article.theme = classification.get("theme")
            article.domain = classification.get("domain")

            article.entities = analysis.get("entities", [])

        article.is_processed = 1
        db.commit()

        return {
            "status": "success",
            "article_id": article_id,
            "relevance_score": article.relevance_score,
            "relevance_level": article.relevance_level.value
        }

    except Exception as e:
        logger.error(f"Error processing article {article_id}: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        db.close()


@celery_app.task(name="app.tasks.process_articles.cleanup_old_articles")
def cleanup_old_articles(days: int = 90):
    """
    Remove articles older than specified days.
    Runs weekly.
    """
    db = SessionLocal()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        deleted = db.query(Article).filter(
            Article.created_at < cutoff_date
        ).delete()

        db.commit()

        logger.info(f"Cleaned up {deleted} old articles")

        return {
            "status": "success",
            "deleted": deleted,
            "cutoff_date": cutoff_date.isoformat()
        }

    except Exception as e:
        logger.error(f"Error cleaning up articles: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        db.close()


@celery_app.task(name="app.tasks.process_articles.reprocess_all")
def reprocess_all_articles():
    """
    Reprocess all articles (admin task).
    Use with caution - this can be expensive on API calls.
    """
    db = SessionLocal()
    try:
        # Reset all articles to unprocessed
        updated = db.query(Article).update({Article.is_processed: 0})
        db.commit()

        logger.info(f"Marked {updated} articles for reprocessing")

        return {
            "status": "success",
            "articles_marked": updated,
            "message": "Articles will be reprocessed by the periodic task"
        }

    except Exception as e:
        logger.error(f"Error in reprocess_all: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        db.close()
