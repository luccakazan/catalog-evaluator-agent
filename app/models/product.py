from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Product:
    """Represents a VTEX product fetched from the catalog API."""
    product_id: str
    description: Optional[str] = None
    name: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None

    def __post_init__(self):
        if not self.product_id:
            raise ValueError("product_id must be non-empty")
        if self.product_id and not isinstance(self.product_id, str):
            raise ValueError("product_id must be a string")