#!/usr/bin/env python3
"""
Database schema migration script for Cloud SQL setup.
Run this script to create the required tables for the catalog evaluator.
"""

import os
from dotenv import load_dotenv
from app.services.database import DatabaseService
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Schema SQL from data-model.md
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(255) PRIMARY KEY,
    description TEXT,
    name VARCHAR(255),
    category VARCHAR(255),
    brand VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS evaluation_results (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(255) NOT NULL REFERENCES products(product_id),
    quality_score INTEGER NOT NULL CHECK (quality_score >= 0 AND quality_score <= 5),
    evaluation_timestamp TIMESTAMP NOT NULL,
    reason TEXT,
    raw_response TEXT,
    UNIQUE(product_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_evaluation_results_product_id ON evaluation_results(product_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_results_timestamp ON evaluation_results(evaluation_timestamp);
"""


def main():
    """Create database schema."""
    load_dotenv()

    logger.info("Starting database schema migration")

    try:
        db_service = DatabaseService()

        # Test connection first
        if not db_service.test_connection():
            logger.error("Database connection failed")
            return

        # Execute schema creation
        engine = db_service.get_engine()

        with engine.begin() as conn:
            # Split SQL into individual statements
            statements = [stmt.strip() for stmt in SCHEMA_SQL.split(';') if stmt.strip()]

            for statement in statements:
                if statement:
                    logger.info(f"Executing: {statement[:50]}...")
                    conn.execute(statement)

        logger.info("Database schema migration completed successfully")

    except Exception as e:
        logger.error(f"Schema migration failed: {e}")
        raise
    finally:
        db_service.close()


if __name__ == "__main__":
    main()