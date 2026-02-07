import os
import csv
import pandas as pd
from typing import List
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


def write_evaluation_results(
    results: List[EvaluationResult],
    csv_path: str,
    *,
    mode: str = 'w',
    write_header: bool = True
) -> None:
    """Write evaluation results to CSV file."""
    if mode not in ('w', 'a'):
        raise ValueError("mode must be 'w' or 'a'")

    try:
        header_needed = write_header

        if mode == 'a' and write_header:
            header_needed = not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0

        with open(csv_path, mode, newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)

            if header_needed:
                writer.writerow(['product_id', 'quality_score', 'evaluation_timestamp', 'reason', 'raw_response'])

            for result in results:
                clean_reason = (result.reason or '').replace('\n', ' ').replace('\r', ' ').strip()
                clean_raw_response = (result.raw_response or '').replace('\n', ' ').replace('\r', ' ').strip()

                writer.writerow([
                    result.product_id,
                    result.quality_score,
                    result.evaluation_timestamp.isoformat(),
                    clean_reason,
                    clean_raw_response
                ])

        logger.info(f"Wrote {len(results)} evaluation results to {csv_path}")

    except Exception as e:
        logger.error(f"Failed to write CSV {csv_path}: {e}")
        raise