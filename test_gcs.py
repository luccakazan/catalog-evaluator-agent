#!/usr/bin/env python3
"""Test Cloud Storage integration."""

import os
from dotenv import load_dotenv
from app.services.cloud_storage import CloudStorageService
from app.models.evaluation_result import EvaluationResult
from datetime import datetime, timezone

load_dotenv()

def test_cloud_storage():
    """Test Cloud Storage upload and download."""
    print("🧪 Testing Cloud Storage Integration...")

    # Create test results
    test_results = [
        EvaluationResult(
            product_id="1",
            quality_score=3,
            evaluation_timestamp=datetime.now(timezone.utc),
            reason="Good quality description",
            raw_response="SCORE: 3\nREASON: Good quality description"
        ),
        EvaluationResult(
            product_id="999",
            quality_score=0,
            evaluation_timestamp=datetime.now(timezone.utc),
            reason="Product not found",
            raw_response="VTEX_API_ERROR"
        )
    ]

    try:
        # Initialize service
        storage_service = CloudStorageService()
        print("✅ Cloud Storage service initialized")

        # Ensure bucket exists
        storage_service.ensure_bucket_exists()
        print("✅ Bucket ready")

        # Upload test file
        filename = "test_results.csv"
        gcs_url = storage_service.upload_results_csv(test_results, filename)
        print(f"✅ Results uploaded to: {gcs_url}")

        # Download and verify
        downloaded_content = storage_service.download_results_csv(filename)
        print("✅ Results downloaded successfully")

        # Check content
        lines = [line for line in downloaded_content.strip().split('\n') if line.strip()]
        if len(lines) >= 3:  # header + at least 2 data rows
            print("✅ CSV format correct")
            print(f"📄 Sample content:\n{lines[0]}")
            if len(lines) > 1:
                print(f"{lines[1][:100]}...")
        else:
            print(f"❌ Unexpected CSV format: {len(lines)} lines")
            print(f"Content: {downloaded_content[:200]}")

        # List files
        files = storage_service.list_result_files()
        print(f"✅ Found {len(files)} files in bucket")

        print("🎉 Cloud Storage integration test completed successfully!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

    return True

if __name__ == "__main__":
    test_cloud_storage()