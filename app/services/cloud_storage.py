import os
from google.cloud import storage
from typing import List
from app.models.evaluation_result import EvaluationResult
from app.utils.logger import get_logger

logger = get_logger(__name__)


class CloudStorageService:
    """Service for storing evaluation results in Google Cloud Storage."""

    def __init__(self):
        self.bucket_name = os.getenv('GCS_BUCKET_NAME', 'catalog-evaluator-results')
        self.client = storage.Client()
        self.bucket = self.client.bucket(self.bucket_name)

    def ensure_bucket_exists(self):
        """Create bucket if it doesn't exist."""
        if not self.bucket.exists():
            self.bucket.create(location='us-central1')  # or your preferred region
            logger.info(f"Created bucket {self.bucket_name}")
        else:
            logger.info(f"Bucket {self.bucket_name} already exists")

    def upload_results_csv(self, results: List[EvaluationResult], filename: str) -> str:
        """Upload evaluation results as CSV to Cloud Storage."""
        try:
            # Convert results to CSV format
            csv_content = "product_id,quality_score,evaluation_timestamp,reason,raw_response\n"
            for result in results:
                # Clean reason and raw_response to remove newlines and extra spaces
                clean_reason = (result.reason or '').replace('\n', ' ').replace('\r', ' ').strip()
                clean_raw_response = (result.raw_response or '').replace('\n', ' ').replace('\r', ' ').strip()
                
                csv_content += f"{result.product_id},{result.quality_score},{result.evaluation_timestamp.isoformat()},{clean_reason},{clean_raw_response}\n"

            # Upload to GCS
            blob = self.bucket.blob(filename)
            blob.upload_from_string(csv_content, content_type='text/csv')

            gcs_url = f"gs://{self.bucket_name}/{filename}"
            logger.info(f"Uploaded results to {gcs_url}")
            return gcs_url

        except Exception as e:
            logger.error(f"Failed to upload results to GCS: {e}")
            raise

    def download_results_csv(self, filename: str) -> str:
        """Download evaluation results CSV from Cloud Storage."""
        try:
            blob = self.bucket.blob(filename)
            csv_content = blob.download_as_text()
            logger.info(f"Downloaded results from gs://{self.bucket_name}/{filename}")
            return csv_content

        except Exception as e:
            logger.error(f"Failed to download results from GCS: {e}")
            raise

    def list_result_files(self, prefix: str = "results_", limit: int = 10) -> List[str]:
        """List available result files."""
        try:
            blobs = list(self.bucket.list_blobs(prefix=prefix))
            files = [blob.name for blob in blobs[:limit]]
            logger.info(f"Found {len(files)} result files")
            return files

        except Exception as e:
            logger.error(f"Failed to list result files: {e}")
            raise