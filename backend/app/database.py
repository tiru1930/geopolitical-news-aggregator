from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import logging

logger = logging.getLogger(__name__)

engine = create_engine(
    settings.get_database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_migrations():
    """Run database migrations for new columns"""
    migrations = [
        # Add is_priority column to articles table
        {
            "check": "SELECT column_name FROM information_schema.columns WHERE table_name='articles' AND column_name='is_priority'",
            "migrate": "ALTER TABLE articles ADD COLUMN is_priority BOOLEAN DEFAULT FALSE",
            "description": "Add is_priority column to articles"
        },
        # Add summary_bullets column to articles table
        {
            "check": "SELECT column_name FROM information_schema.columns WHERE table_name='articles' AND column_name='summary_bullets'",
            "migrate": "ALTER TABLE articles ADD COLUMN summary_bullets TEXT",
            "description": "Add summary_bullets column to articles"
        },
    ]

    with engine.connect() as conn:
        for migration in migrations:
            try:
                # Check if migration is needed
                result = conn.execute(text(migration["check"]))
                if result.fetchone() is None:
                    # Run migration
                    conn.execute(text(migration["migrate"]))
                    conn.commit()
                    logger.info(f"Migration completed: {migration['description']}")
                else:
                    logger.debug(f"Migration not needed: {migration['description']}")
            except Exception as e:
                logger.error(f"Migration failed: {migration['description']} - {e}")


def init_db():
    """Initialize database tables"""
    from app.models import article, source, alert, user  # noqa
    Base.metadata.create_all(bind=engine)
    # Run migrations for new columns
    run_migrations()
