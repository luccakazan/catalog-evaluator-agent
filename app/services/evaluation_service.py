import os
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import List, Iterator, Tuple
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
        self._product_fetch_workers = max(1, int(os.getenv('VTEX_FETCH_CONCURRENCY', '8')))

    @dataclass
    class _FetchOutcome:
        index: int
        product_id: str
        product: Product | None = None
        error_result: EvaluationResult | None = None

    def _fetch_single_product(self, index: int, product_id: str) -> "EvaluationService._FetchOutcome":
        """Fetch a single product and build error result on failure."""
        try:
            product = self.vtex_client.get_product(product_id)
            if product and product.description:
                return self._FetchOutcome(index=index, product_id=product_id, product=product)

            logger.warning(
                f"Product {product_id} not found or has no description",
                extra={'product_id': product_id}
            )
            error_result = EvaluationResult(
                product_id=product_id,
                quality_score=0,
                evaluation_timestamp=datetime.now(timezone.utc),
                reason="Product not found in VTEX catalog or has no description",
                raw_response="VTEX_API_ERROR"
            )
            return self._FetchOutcome(index=index, product_id=product_id, error_result=error_result)

        except Exception as exc:
            logger.error(
                f"Failed to fetch product {product_id}: {exc}",
                extra={'product_id': product_id}
            )
            error_result = EvaluationResult(
                product_id=product_id,
                quality_score=0,
                evaluation_timestamp=datetime.now(timezone.utc),
                reason=f"VTEX API error: {str(exc)}",
                raw_response="VTEX_API_ERROR"
            )
            return self._FetchOutcome(index=index, product_id=product_id, error_result=error_result)

    def _fetch_products_concurrently(self, product_ids: List[str]) -> List["EvaluationService._FetchOutcome"]:
        """Fetch VTEX products concurrently to hide network latency."""
        outcomes: List[EvaluationService._FetchOutcome] = []
        with ThreadPoolExecutor(max_workers=self._product_fetch_workers) as executor:
            future_map = {
                executor.submit(self._fetch_single_product, idx, product_id): idx
                for idx, product_id in enumerate(product_ids)
            }
            for future in as_completed(future_map):
                outcome = future.result()
                outcomes.append(outcome)

        return sorted(outcomes, key=lambda item: item.index)

    def evaluate_catalog_batches(
        self,
        product_ids: List[str],
        *,
        batch_size: int | None = None
    ) -> Iterator[Tuple[List[Product], List[EvaluationResult]]]:
        """Yield VTEX products and evaluation results in batches."""
        resolved_batch_size = max(1, batch_size or self.gemini_evaluator.batch_size)

        outcomes = self._fetch_products_concurrently(product_ids)

        valid_products = [outcome.product for outcome in outcomes if outcome.product]
        evaluated_results: List[EvaluationResult] = []
        if valid_products:
            evaluated_results = self.gemini_evaluator.evaluate_products(valid_products)
            if len(evaluated_results) != len(valid_products):
                logger.error(
                    "Mismatch between evaluated results and fetched products",
                    extra={'expected': len(valid_products), 'received': len(evaluated_results)}
                )

        evaluation_iter = iter(evaluated_results)
        batch_products: List[Product] = []
        batch_results: List[EvaluationResult] = []

        for outcome in outcomes:
            if outcome.product:
                product = outcome.product
                try:
                    result = next(evaluation_iter)
                except StopIteration:
                    logger.error(
                        "Ran out of evaluation results while processing products",
                        extra={'product_id': product.product_id}
                    )
                    if batch_products or batch_results:
                        yield batch_products.copy(), batch_results.copy()
                    break
                batch_products.append(product)
                batch_results.append(result)

                if len(batch_products) >= resolved_batch_size:
                    yield batch_products.copy(), batch_results.copy()
                    batch_products.clear()
                    batch_results.clear()
            elif outcome.error_result:
                if batch_products or batch_results:
                    yield batch_products.copy(), batch_results.copy()
                    batch_products.clear()
                    batch_results.clear()

                yield [], [outcome.error_result]

        if batch_products or batch_results:
            yield batch_products.copy(), batch_results.copy()

    def evaluate_catalog(self, product_ids: List[str]) -> tuple[List[Product], List[EvaluationResult]]:
        """Evaluate a list of product IDs and return products and evaluation results."""
        products: List[Product] = []
        evaluation_results: List[EvaluationResult] = []

        for batch_products, batch_results in self.evaluate_catalog_batches(product_ids):
            if batch_products:
                products.extend(batch_products)
            evaluation_results.extend(batch_results)

        if not products:
            logger.info("No products available for AI evaluation")

        return products, evaluation_results