# Catalog Quality Evaluator - Spec Kit Test

This is a quick hobby project to experiment with Spec Kit.

It builds a service that evaluates VTEX product catalog quality by fetching product data via API, analyzing descriptions with Google Gemini LLM, and storing results in CSV and Google Cloud Storage (much cheaper than database!).

## Features

- **CSV Processing**: Read product IDs from CSV files
- **VTEX Integration**: Fetch product details via VTEX Catalog API
- **AI Evaluation**: Analyze product descriptions using Google Gemini
- **Cloud Storage**: Store results cheaply in Google Cloud Storage ($3/month vs $12/month for database)
- **Database Optional**: Cloud SQL PostgreSQL support for complex queries
- **REST API**: FastAPI-based endpoints for web integration
- **Cloud Deployment**: Ready for Google Cloud Run

## Quick Start

### Prerequisites

- Python 3.12+
- Google Cloud SDK
- VTEX API credentials
- Google Gemini API key

### Installation

1. Clone the repository
2. Create virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

Create a `.env` file with your credentials:

```env
# VTEX API
VTEX_APP_KEY=your_app_key
VTEX_APP_TOKEN=your_app_token
VTEX_ACCOUNT_NAME=your_account

# Google Gemini
GOOGLE_API_KEY=your_gemini_key

# Cloud Storage (recommended - $3/month)
GCS_BUCKET_NAME=catalog-evaluator-results

# Database (optional - $12+/month)
DB_INSTANCE_CONNECTION_NAME=project:region:instance
DB_NAME=catalog_evaluator
DB_USER=your_user

# API Security
API_KEY=your-secure-api-key-change-this-in-production
```

**Note**: You only need either Cloud Storage OR Database.

### Usage

#### Command Line

```bash
python -m app.main --input products.csv --output results.csv
```

#### API Server

```bash
uvicorn app.api:app --reload
```

Then upload CSV via POST to `/evaluate`.

## API Documentation

### Authentication
All API endpoints (except `/health`) require API key authentication. Include the API key in the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-secure-api-key" \
  -X POST "http://localhost:8000/evaluate" \
  -F "file=@products.csv"
```

### POST /evaluate
Upload a CSV file with product IDs to start evaluation.

**Authentication**: Required (X-API-Key header)

**Request**: Multipart form with `file` field containing CSV.

**Response**:
```json
{
  "job_id": "uuid",
  "status": "processing",
  "message": "Evaluation started"
}
```

### GET /status/{job_id}
Check evaluation progress.

**Response**:
```json
{
  "job_id": "uuid",
  "status": "processing|completed|failed",
  "progress": {
    "processed": 10,
    "total": 100,
    "errors": 0
  }
}
```

### GET /results/{job_id}
Download evaluation results CSV.

**Authentication**: Required (X-API-Key header)

## Testing

### Test Cloud Storage Integration

```bash
# Test Cloud Storage upload/download
python test_gcs.py
```

### Test Full Pipeline

```bash
# Test with sample data
python -m app.main --input test_products.csv --output test_results.csv

# Check results
head -5 test_results.csv
```

### Test API Endpoints

```bash
# Start API server in one terminal
uvicorn app.api:app --host 0.0.0.0 --port 8000

# In another terminal, test endpoints
# First, test health (no auth required)
curl -X GET "http://localhost:8000/health"

# Upload CSV for evaluation (replace <YOUR_API_KEY_FROM_ENV> with the value from your .env file)
curl -H "X-API-Key: <YOUR_API_KEY_FROM_ENV>" \
  -X POST "http://localhost:8000/evaluate" \
  -F "file=@test_products.csv"

# Check status (no auth required) - replace job-uuid with the actual job_id from the response
curl -X GET "http://localhost:8000/status/job-uuid"

# Download results (replace YOUR_API_KEY and job-uuid)
curl -H "X-API-Key: YOUR_API_KEY" \
  -X GET "http://localhost:8000/results/job-uuid" \
  -o results.csv
```

## Deployment

### Local Development

```bash
# Run API
uvicorn app.api:app --host 0.0.0.0 --port 8000

# Run CLI
python -m app.main --input test.csv --output results.csv
```

### Google Cloud Run

1. Build and push Docker image:
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT/catalog-evaluator
   ```

2. Deploy:
   ```bash
   gcloud run deploy catalog-evaluator \
     --image gcr.io/YOUR_PROJECT/catalog-evaluator \
     --platform managed \
     --allow-unauthenticated \
     --set-env-vars "GOOGLE_API_KEY=KEY,DB_INSTANCE=..."
   ```

### Database Setup

Run the schema migration:

```bash
python app/create_schema.py
```

## Architecture

```
CSV Input → VTEX API → Product Models → Gemini Evaluation → Results → CSV + Database
```

- **app/models/**: Data models (Product, EvaluationResult)
- **app/services/**: Business logic (VTEX client, Gemini evaluator, Database)
- **app/utils/**: Helpers (CSV handler, logging)
- **app/api.py**: FastAPI application
- **app/main.py**: CLI entry point

## Quality Scoring

- 1: Excellent quality
- 2: Good quality
- 3: Average quality
- 4: Poor quality
- 5: Very poor quality

## Performance

- Processes ~1000 products
- Batch size: 5-10 concurrent evaluations
- Built-in retry logic for API failures

## Troubleshooting

- **VTEX API errors**: Check credentials and permissions
- **Gemini quota**: Monitor Google Cloud console
- **Database connection**: Verify Cloud SQL setup
- **Memory issues**: Increase Cloud Run memory for large CSVs

## License

This is a hobby project testing spec kit, nobody should use it really. But feel free