import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional
from datetime import datetime, timezone
import google.genai as genai
from app.models.product import Product
from app.models.evaluation_result import EvaluationResult
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GeminiEvaluator:
    """Service for evaluating product descriptions using Google Gemini."""

    def __init__(self):
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not set")

        self.client = genai.Client(api_key=api_key)
        self.model = "models/gemini-flash-latest"  # Use a stable available model
        
        # Try to list available models for debugging
        try:
            models = self.client.models.list()
            logger.info(f"Available Gemini models: {[m.name for m in models if 'gemini' in m.name.lower()]}")
        except Exception as e:
            logger.warning(f"Could not list models: {e}")

        # Batch size for concurrent processing
        self.batch_size = 5

    def _create_evaluation_prompt(self, product: Product) -> str:
        """Create prompt for evaluating product description quality."""
        return f"""
Evaluate the quality of this product description on a scale of 1-5, where:
1 = Excellent quality (clear, detailed, engaging, error-free)
2 = Good quality (mostly clear, some details, minor issues)
3 = Average quality (basic information, some clarity issues)
4 = Poor quality (unclear, missing key info, noticeable errors)
5 = Very poor quality (confusing, incomplete, major errors)

Product Name: {product.name or 'N/A'}
Product Description: {product.description or 'No description available'}

Provide your response in this exact format:
SCORE: [1-5]
REASON: [brief 150 characters explanation in English]

Consider:
- Clarity and comprehensibility
- Completeness of information
- Grammar and spelling
- Engagement and appeal
- Accuracy and helpfulness

Response:"""

    async def _evaluate_single_product(self, product: Product) -> EvaluationResult:
        """Evaluate a single product description."""
        try:
            prompt = self._create_evaluation_prompt(product)

            # Run in thread pool since google-genai is synchronous
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                response = await loop.run_in_executor(
                    executor, 
                    lambda: self.client.models.generate_content(
                        model=self.model,
                        contents=prompt
                    )
                )

            # Extract score and reason from response
            if hasattr(response, 'text'):
                raw_response = response.text.strip()
            else:
                raw_response = str(response)
            
            # Parse structured response
            score = None
            reason = None
            
            lines = raw_response.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('SCORE:'):
                    try:
                        score = int(line.split(':', 1)[1].strip())
                    except (ValueError, IndexError):
                        pass
                elif line.startswith('REASON:'):
                    reason = line.split(':', 1)[1].strip()
            
            # Fallback parsing if structured format not followed
            if score is None:
                # Try to find a number 1-5 in the response
                import re
                numbers = re.findall(r'\b([1-5])\b', raw_response)
                if numbers:
                    score = int(numbers[0])
                else:
                    score = 5  # Default to poor quality
            
            if reason is None:
                reason = "Evaluation completed"  # Default reason
            
            if not (1 <= score <= 5):
                score = 5
                reason = "Invalid score received, defaulted to poor quality"

            result = EvaluationResult(
                product_id=product.product_id,
                quality_score=score,
                evaluation_timestamp=datetime.utcnow(),
                reason=reason,
                raw_response=raw_response
            )

            logger.info(f"Evaluated product {product.product_id} with score {score}",
                       extra={'product_id': product.product_id})
            return result

        except Exception as e:
            logger.error(f"Error evaluating product {product.product_id}: {e}",
                        extra={'product_id': product.product_id})
            # Return error result with score 0
            return EvaluationResult(
                product_id=product.product_id,
                quality_score=0,
                evaluation_timestamp=datetime.now(timezone.utc),
                reason=f"Evaluation failed: {str(e)}",
                raw_response=str(e)
            )

    async def evaluate_batch(self, products: List[Product]) -> List[EvaluationResult]:
        """Evaluate a batch of products concurrently."""
        logger.info(f"Starting evaluation of {len(products)} products")

        # Process in batches to avoid overwhelming the API
        results = []
        for i in range(0, len(products), self.batch_size):
            batch = products[i:i + self.batch_size]
            logger.info(f"Processing batch {i//self.batch_size + 1} with {len(batch)} products")

            # Evaluate batch concurrently
            batch_results = await asyncio.gather(
                *[self._evaluate_single_product(product) for product in batch]
            )
            results.extend(batch_results)

        logger.info(f"Completed evaluation of {len(products)} products")
        return results

    def evaluate_products(self, products: List[Product]) -> List[EvaluationResult]:
        """Synchronous wrapper for batch evaluation."""
        return asyncio.run(self.evaluate_batch(products))