import argparse
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from typing import List
from app.services.evaluation_service import EvaluationService
from app.services.cloud_storage import CloudStorageService
from app.utils.csv_handler import read_product_ids, write_evaluation_results
from app.models.product import Product
from app.models.evaluation_result import EvaluationResult
from app.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    # Load environment variables
    load_dotenv()

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Evaluate VTEX product catalog quality')
    parser.add_argument('--input', '-i', required=True, help='Input CSV file with product_ids')
    parser.add_argument('--output', '-o', required=True, help='Output CSV file for results')
    args = parser.parse_args()

    logger.info("Starting catalog quality evaluation", extra={'input_file': args.input, 'output_file': args.output})

    try:
        # 1. Read product IDs from CSV
        product_ids = read_product_ids(args.input)
        if not product_ids:
            logger.error("No product IDs found in input file")
            return

        # 2. Initialize evaluation service
        evaluation_service = EvaluationService()

        # 3. Evaluate catalog in batches and persist results incrementally
        products: List[Product] = []
        evaluation_results: List[EvaluationResult] = []
        write_evaluation_results([], args.output, mode='w', write_header=True)

        for batch_products, batch_results in evaluation_service.evaluate_catalog_batches(product_ids):
            if batch_products:
                products.extend(batch_products)
            if batch_results:
                evaluation_results.extend(batch_results)
                write_evaluation_results(batch_results, args.output, mode='a', write_header=False)

        if not evaluation_results:
            logger.error("No evaluation results generated")
            return

        # 4. Initialize Cloud Storage service (optional, cheaper alternative)
        storage_service = None
        if os.getenv('GCS_BUCKET_NAME'):
            try:
                storage_service = CloudStorageService()
                storage_service.ensure_bucket_exists()
                logger.info("Cloud Storage initialized for result storage")
            except Exception as e:
                logger.warning(f"Cloud Storage initialization failed: {e}")
        
        # 5. Initialize Database service (optional)
        db_service = None
        db_instance = os.getenv('DB_INSTANCE_CONNECTION_NAME')
        db_user = os.getenv('DB_USER')
        if db_instance and db_user and db_instance != 'your_project:region:instance':
            try:
                from app.services.database import DatabaseService
                db_service = DatabaseService()
            except ImportError as e:
                logger.warning(f"Database dependencies not installed: {e}. Using Cloud Storage only.")
            except Exception as e:
                logger.warning(f"Database initialization failed: {e}. Results will only be saved to CSV/Cloud Storage.")
        else:
            logger.info("Database not configured. Results will be saved to CSV/Cloud Storage.")

        # 6. Store results in database (optional)
        if db_service:
            try:
                db_service.store_evaluation_results(products, evaluation_results)
            except Exception as e:
                logger.warning(f"Database storage failed: {e}")

        # 7. Store results in Cloud Storage (optional, cheaper alternative)
        if storage_service:
            try:
                filename = os.path.basename(args.output)
                gcs_url = storage_service.upload_results_csv(evaluation_results, filename)
                logger.info(f"Results uploaded to Cloud Storage: {gcs_url}")
            except Exception as e:
                logger.warning(f"Cloud Storage upload failed: {e}")

        logger.info(
            "Catalog quality evaluation completed successfully",
            extra={'total_products': len(product_ids), 'total_results': len(evaluation_results)}
        )

    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        raise


if __name__ == "__main__":
    main()
