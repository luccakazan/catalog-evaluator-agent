# Quickstart: Catalog Quality Evaluator

**Date**: 2026-01-31
**Plan**: [specs/001-catalog-quality-evaluator/plan.md](specs/001-catalog-quality-evaluator/plan.md)

## Local Development Setup

### Prerequisites
- Python 3.12+
- Google Cloud SDK (for GCP authentication)
- VTEX API credentials (App Key, App Token)
- Google Gemini API key

### Installation

1. Clone the repository and navigate to the project root
2. Create virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

Create a `.env` file with required environment variables:

```env
# VTEX API Credentials
VTEX_APP_KEY=your_vtex_app_key
VTEX_APP_TOKEN=your_vtex_app_token
VTEX_ACCOUNT_NAME=your_vtex_account

# Google Gemini API
GOOGLE_API_KEY=your_gemini_api_key

# Cloud SQL (for production)
DB_INSTANCE_CONNECTION_NAME=your_project:region:instance
DB_NAME=catalog_evaluator
DB_USER=your_db_user

# Logging
LOG_LEVEL=INFO
```

### Running Locally

1. Prepare a CSV file with product IDs:
   ```csv
   product_id
   12345
   67890
   ```

2. Run the evaluation:
   ```bash
   python app/main.py --input products.csv --output results.csv
   ```

3. Check results in `results.csv`:
   ```csv
   product_id,quality_score,evaluation_timestamp,reason,raw_response
   12345,3,2026-01-31T10:00:00Z,"The description is clear but lacks detail","SCORE: 3\nREASON: The description is clear but lacks detail"
   67890,0,2026-01-31T10:00:01Z,"Product not found in VTEX catalog or has no description","VTEX_API_ERROR"
   ```

## Testing

Run the test suite:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=app tests/
```

## Deployment to GCP

### Prerequisites
- Google Cloud Project with billing enabled
- Cloud SQL PostgreSQL instance created
- Cloud Storage bucket (optional, for result storage)
- Service account with appropriate permissions

### Deploy to Cloud Run

1. Build and push Docker image:
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT/catalog-evaluator
   ```

2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy catalog-evaluator \
     --image gcr.io/YOUR_PROJECT/catalog-evaluator \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars "GOOGLE_API_KEY=YOUR_KEY,DB_INSTANCE_CONNECTION_NAME=YOUR_DB"
   ```

### API Usage

Once deployed, use the API endpoints:

- **Start Evaluation**:
  ```bash
  curl -X POST https://your-service-url/evaluate \
    -F "file=@products.csv"
  ```

- **Check Status**:
  ```bash
  curl https://your-service-url/status/{job_id}
  ```

- **Download Results**:
  ```bash
  curl -o results.csv https://your-service-url/results/{job_id}
  ```

## Troubleshooting

### Common Issues

- **VTEX API Authentication**: Verify App Key and Token are correct and have catalog read permissions
- **Gemini API Quota**: Check Google Cloud console for API limits and usage
- **Cloud SQL Connection**: Ensure service account has Cloud SQL Client role
- **Memory Issues**: For large CSV files (>10k products), consider increasing Cloud Run memory

### Logs

View application logs:
```bash
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=catalog-evaluator"
```

## Performance Notes

- Typical processing time: ~1-2 hours for 1000 products
- Cost estimate: ~$0.50-2.00 per 1000 products (API calls + compute)
- Rate limiting: Built-in exponential backoff handles VTEX API limits</content>
<parameter name="filePath">/Users/lucca.kazan/Documents/study_projects/catalog-evaluator-agent/specs/001-catalog-quality-evaluator/quickstart.md