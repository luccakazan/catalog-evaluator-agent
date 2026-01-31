from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class EvaluationResult:
    """Represents the quality evaluation result for a product description."""
    product_id: str
    quality_score: int
    evaluation_timestamp: datetime
    reason: Optional[str] = None
    raw_response: Optional[str] = None

    def __post_init__(self):
        if not isinstance(self.quality_score, int) or not (0 <= self.quality_score <= 5):
            raise ValueError("quality_score must be an integer between 0 and 5")
        if not self.product_id:
            raise ValueError("product_id must be non-empty")