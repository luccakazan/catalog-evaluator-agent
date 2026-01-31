import argparse
import os
from datetime import datetime
from dotenv import load_dotenv
from typing import List
from app.services.vtex_client import VtexClient
from app.services.gemini_evaluator import GeminiEvaluator
from app.services.database import DatabaseService
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

        # 2. Initialize services
        vtex_client = VtexClient()
        gemini_evaluator = GeminiEvaluator()
        
        # Database service is optional
        db_service = None
        db_instance = os.getenv('DB_INSTANCE_CONNECTION_NAME')
        db_user = os.getenv('DB_USER')
        if db_instance and db_user and db_instance != 'your_project:region:instance':
            try:
                db_service = DatabaseService()
            except Exception as e:
                logger.warning(f"Database initialization failed: {e}. Results will only be saved to CSV.")
        else:
            logger.info("Database not configured. Results will only be saved to CSV.")

        # 3. Fetch products from VTEX and prepare evaluation results
        products = []
        evaluation_results = []
        
        for product_id in product_ids:
            try:
                product = vtex_client.get_product(product_id)
                if product and product.description:
                    products.append(product)
                else:
                    # Product not found or no description - create error result
                    error_result = EvaluationResult(
                        product_id=product_id,
                        quality_score=0,  # Special code for not processed
                        evaluation_timestamp=datetime.utcnow(),
                        reason="Product not found in VTEX catalog or has no description",
                        raw_response="VTEX_API_ERROR"
                    )
                    evaluation_results.append(error_result)
                    logger.warning(f"Product {product_id} not found or has no description",
                                 extra={'product_id': product_id})
            except Exception as e:
                # API error - create error result
                error_result = EvaluationResult(
                    product_id=product_id,
                    quality_score=0,  # Special code for API error
                    evaluation_timestamp=datetime.utcnow(),
                    reason=f"VTEX API error: {str(e)}",
                    raw_response="VTEX_API_ERROR"
                )
                evaluation_results.append(error_result)
                logger.error(f"Failed to fetch product {product_id}: {e}",
                           extra={'product_id': product_id})

        if not products:
            logger.error("No products with descriptions to evaluate")
            return

        # 4. Evaluate products with Gemini (only successful fetches)
        if products:
            gemini_results = gemini_evaluator.evaluate_products(products)
            evaluation_results.extend(gemini_results)
        else:
            logger.info("No products available for AI evaluation")

        # 5. Store results in database (optional)
        if db_service:
            db_service.store_evaluation_results(products, evaluation_results)

        # 6. Write results to CSV
        write_evaluation_results(evaluation_results, args.output)

        logger.info("Catalog quality evaluation completed successfully",
                   extra={'total_products': len(product_ids), 'evaluated_products': len(products)})

    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        raise


if __name__ == "__main__":
    main()
