import os
from google.cloud.sql.connector import Connector
import pg8000
from typing import Optional, List
import sqlalchemy
from sqlalchemy import create_engine, text, insert, select
from sqlalchemy.exc import IntegrityError
from app.models.product import Product
from app.models.evaluation_result import EvaluationResult
from app.utils.logger import get_logger

logger = get_logger(__name__)

logger = get_logger(__name__)


class DatabaseService:
    """Service for managing Cloud SQL PostgreSQL connections and operations."""

    def __init__(self):
        self.connector = Connector()
        self.engine: Optional[sqlalchemy.engine.Engine] = None

    def get_connection(self):
        """Get a database connection using Cloud SQL connector."""
        instance_connection_name = os.getenv('DB_INSTANCE_CONNECTION_NAME')
        db_user = os.getenv('DB_USER')
        db_name = os.getenv('DB_NAME')

        if not all([instance_connection_name, db_user, db_name]):
            raise ValueError("Database environment variables not set")

        def getconn() -> pg8000.dbapi.Connection:
            conn = self.connector.connect(
                instance_connection_name,
                "pg8000",
                user=db_user,
                db=db_name,
            )
            return conn

        return getconn()

    def get_engine(self) -> sqlalchemy.engine.Engine:
        """Get SQLAlchemy engine for the database."""
        if self.engine is None:
            instance_connection_name = os.getenv('DB_INSTANCE_CONNECTION_NAME')
            db_user = os.getenv('DB_USER')
            db_name = os.getenv('DB_NAME')

            if not all([instance_connection_name, db_user, db_name]):
                raise ValueError("Database environment variables not set")

            # Create SQLAlchemy engine
            self.engine = create_engine(
                f"postgresql+pg8000://",
                creator=self.get_connection,
                pool_pre_ping=True,
            )

        return self.engine

    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.get_engine().connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False

    def close(self):
        """Close the connector."""
        if self.connector:
            self.connector.close()
            logger.info("Database connector closed")

    def store_evaluation_results(self, products: List[Product], results: List[EvaluationResult]) -> None:
        """Store products and evaluation results in database."""
        try:
            engine = self.get_engine()

            with engine.begin() as conn:
                # Store products first (ignore if already exists)
                for product in products:
                    try:
                        conn.execute(
                            text("""
                                INSERT INTO products (product_id, description, name, category, brand)
                                VALUES (:product_id, :description, :name, :category, :brand)
                                ON CONFLICT (product_id) DO NOTHING
                            """),
                            {
                                'product_id': product.product_id,
                                'description': product.description,
                                'name': product.name,
                                'category': product.category,
                                'brand': product.brand
                            }
                        )
                    except Exception as e:
                        logger.warning(f"Failed to store product {product.product_id}: {e}")

                # Store evaluation results
                for result in results:
                    try:
                        conn.execute(
                            text("""
                                INSERT INTO evaluation_results (product_id, quality_score, evaluation_timestamp, reason, raw_response)
                                VALUES (:product_id, :quality_score, :evaluation_timestamp, :reason, :raw_response)
                            """),
                            {
                                'product_id': result.product_id,
                                'quality_score': result.quality_score,
                                'evaluation_timestamp': result.evaluation_timestamp,
                                'reason': result.reason,
                                'raw_response': result.raw_response
                            }
                        )
                        logger.info(f"Stored evaluation result for product {result.product_id}",
                                  extra={'product_id': result.product_id})
                    except IntegrityError:
                        logger.warning(f"Evaluation result already exists for product {result.product_id}",
                                     extra={'product_id': result.product_id})
                    except Exception as e:
                        logger.error(f"Failed to store evaluation result for product {result.product_id}: {e}")

            logger.info(f"Stored {len(products)} products and {len(results)} evaluation results")

        except Exception as e:
            logger.error(f"Failed to store evaluation results: {e}")
            raise

    def get_evaluation_results(self, limit: int = 100) -> List[EvaluationResult]:
        """Retrieve recent evaluation results from database."""
        try:
            engine = self.get_engine()

            with engine.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT product_id, quality_score, evaluation_timestamp, reason, raw_response
                        FROM evaluation_results
                        ORDER BY evaluation_timestamp DESC
                        LIMIT :limit
                    """),
                    {'limit': limit}
                )

                evaluation_results = []
                for row in result:
                    evaluation_results.append(EvaluationResult(
                        product_id=row[0],
                        quality_score=row[1],
                        evaluation_timestamp=row[2],
                        reason=row[3],
                        raw_response=row[4]
                    ))

            logger.info(f"Retrieved {len(evaluation_results)} evaluation results")
            return evaluation_results

        except Exception as e:
            logger.error(f"Failed to retrieve evaluation results: {e}")
            raise