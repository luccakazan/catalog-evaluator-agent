import pandas as pd
from typing import List
from app.models.product import Product
from app.models.evaluation_result import EvaluationResult
from app.utils.logger import get_logger

logger = get_logger(__name__)


def read_product_ids(csv_path: str) -> List[str]:
    """Read product IDs from CSV file.

    Expects a CSV with a 'product_id' column.
    """
    try:
        df = pd.read_csv(csv_path)
        if 'product_id' not in df.columns:
            raise ValueError("CSV must contain 'product_id' column")

        product_ids = df['product_id'].astype(str).tolist()
        logger.info(f"Read {len(product_ids)} product IDs from {csv_path}")
        return product_ids

    except Exception as e:
        logger.error(f"Failed to read CSV {csv_path}: {e}")
        raise


def write_evaluation_results(results: List[EvaluationResult], csv_path: str) -> None:
    """Write evaluation results to CSV file."""
    try:
        data = []
        for result in results:
            # Clean reason and raw_response to remove newlines and extra spaces
            clean_reason = (result.reason or '').replace('\n', ' ').replace('\r', ' ').strip()
            clean_raw_response = (result.raw_response or '').replace('\n', ' ').replace('\r', ' ').strip()
            
            data.append({
                'product_id': result.product_id,
                'quality_score': result.quality_score,
                'evaluation_timestamp': result.evaluation_timestamp.isoformat(),
                'reason': clean_reason,
                'raw_response': clean_raw_response
            })

        df = pd.DataFrame(data)
        df.to_csv(csv_path, index=False)
        logger.info(f"Wrote {len(results)} evaluation results to {csv_path}")

    except Exception as e:
        logger.error(f"Failed to write CSV {csv_path}: {e}")
        raise