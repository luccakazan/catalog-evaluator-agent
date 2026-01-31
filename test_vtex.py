#!/usr/bin/env python3
"""
Test script for VTEX API integration.
Fetches a single product to verify API credentials and connection.
"""

import os
from dotenv import load_dotenv
from app.services.vtex_client import VtexClient
from app.utils.logger import get_logger

logger = get_logger(__name__)


def test_vtex_api(product_id: str = "12345"):
    """Test VTEX API by fetching a product."""
    load_dotenv()

    logger.info("Testing VTEX API connection", extra={'product_id': product_id})

    try:
        client = VtexClient()
        product = client.get_product(product_id)

        if product:
            print("✅ VTEX API test successful!")
            print(f"Product ID: {product.product_id}")
            print(f"Name: {product.name}")
            print(f"Description: {product.description[:100] if product.description else 'No description'}...")
            print(f"Category: {product.category}")
            print(f"Brand: {product.brand}")
        else:
            print("❌ Product not found or no description")
            print("This might be expected if the product ID doesn't exist in your catalog")

    except Exception as e:
        print(f"❌ VTEX API test failed: {e}")
        print("Please check your VTEX credentials in .env file")
        return False

    return True


if __name__ == "__main__":
    import sys

    product_id = sys.argv[1] if len(sys.argv) > 1 else "12345"
    test_vtex_api(product_id)