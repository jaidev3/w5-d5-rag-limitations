"""Database initialization script."""

import logging
from sqlalchemy import create_engine
from .database import Base, engine
from . import models  # Import all models
from ..config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_tables():
    """Create all database tables."""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully!")
        
        # Log table count
        table_count = len(Base.metadata.tables)
        logger.info(f"Total tables created: {table_count}")
        
        # Log table names
        table_names = list(Base.metadata.tables.keys())
        logger.info(f"Tables: {', '.join(table_names)}")
        
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def drop_tables():
    """Drop all database tables."""
    try:
        logger.info("Dropping database tables...")
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully!")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise


def recreate_tables():
    """Drop and recreate all database tables."""
    try:
        logger.info("Recreating database tables...")
        drop_tables()
        create_tables()
        logger.info("Database tables recreated successfully!")
    except Exception as e:
        logger.error(f"Error recreating database tables: {e}")
        raise


if __name__ == "__main__":
    create_tables() 