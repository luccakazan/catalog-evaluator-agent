import os
from datetime import datetime, timezone
from typing import List
from app.services.vtex_client import VtexClient
from app.services.gemini_evaluator import GeminiEvaluator
from app.models.product import Product
from app.models.evaluation_result import EvaluationResult
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EvaluationService:
    """Service for evaluating product catalog quality."""

    def __init__(self):
        self.vtex_client = VtexClient()
        self.gemini_evaluator = GeminiEvaluator()

    def evaluate_catalog(self, product_ids: List[str]) -> tuple[List[Product], List[EvaluationResult]]:
        """Evaluate a list of product IDs and return products and evaluation results."""
        evaluation_results = []
        products = []

        for product_id in product_ids:
            try:
                product = self.vtex_client.get_product(product_id)
                if product and product.description:
                    products.append(product)
                else:
                    # Product not found or no description - create error result
                    error_result = EvaluationResult(
                        product_id=product_id,
                        quality_score=0,
                        evaluation_timestamp=datetime.now(timezone.utc),
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
                    quality_score=0,
                    evaluation_timestamp=datetime.now(timezone.utc),
                    reason=f"VTEX API error: {str(e)}",
                    raw_response="VTEX_API_ERROR"
                )
                evaluation_results.append(error_result)
                logger.error(f"Failed to fetch product {product_id}: {e}",
                           extra={'product_id': product_id})

        # Evaluate products with Gemini (only successful fetches)
        if products:
            gemini_results = self.gemini_evaluator.evaluate_products(products)
            evaluation_results.extend(gemini_results)
        else:
            logger.info("No products available for AI evaluation")

        return products, evaluation_results