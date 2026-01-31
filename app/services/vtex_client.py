import os
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import Optional, Dict, Any
from app.models.product import Product
from app.utils.logger import get_logger

logger = get_logger(__name__)


class VtexClient:
    """Client for interacting with VTEX Catalog API."""

    def __init__(self):
        self.app_key = os.getenv('VTEX_APP_KEY')
        self.app_token = os.getenv('VTEX_APP_TOKEN')
        self.account_name = os.getenv('VTEX_ACCOUNT_NAME')

        if not all([self.app_key, self.app_token, self.account_name]):
            raise ValueError("VTEX credentials not configured")

        self.base_url = f"https://{self.account_name}.vtexcommercestable.com.br"
        self.session = requests.Session()
        self.session.headers.update({
            'X-VTEX-API-AppKey': self.app_key,
            'X-VTEX-API-AppToken': self.app_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.RequestException, requests.HTTPError))
    )
    def _make_request(self, endpoint: str) -> Dict[str, Any]:
        """Make authenticated request to VTEX API with retry logic."""
        url = f"{self.base_url}{endpoint}"
        logger.info(f"Making request to {url}")

        response = self.session.get(url)
        response.raise_for_status()

        return response.json()

    def get_product(self, product_id: str) -> Optional[Product]:
        """Fetch product data from VTEX API."""
        try:
            # VTEX API endpoint for product details
            endpoint = f"/api/catalog/pvt/product/{product_id}"
            data = self._make_request(endpoint)

            product = Product(
                product_id=product_id,
                description=data.get('Description'),
                name=data.get('Name'),
                category=data.get('CategoryName'),
                brand=data.get('BrandName')
            )

            logger.info(f"Successfully fetched product {product_id}", extra={'product_id': product_id})
            return product

        except requests.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Product {product_id} not found", extra={'product_id': product_id})
                return None
            else:
                logger.error(f"HTTP error fetching product {product_id}: {e}", extra={'product_id': product_id})
                raise
        except Exception as e:
            logger.error(f"Error fetching product {product_id}: {e}", extra={'product_id': product_id})
            raise