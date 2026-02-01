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

## Cost Comparison

| Storage Method | Monthly Cost | Use Case |
|----------------|-------------|----------|
| **Cloud Storage** | $3/month | ✅ Recommended - File storage, batch processing |
| **Cloud SQL** | $12+/month | Complex queries, real-time data |
| **Local CSV** | $0 | Development only |

**💡 Pro Tip**: Use Cloud Storage! It's 75% cheaper and perfect for your use case.

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
```

**Note**: You only need either Cloud Storage OR Database. Cloud Storage is much cheaper!

### Usage

#### Command Line

```bash
python app/main.py --input products.csv --output results.csv
```

#### API Server

```bash
uvicorn app.api:app --reload
```

Then upload CSV via POST to `/evaluate`.

## API Documentation

### POST /evaluate
Upload a CSV file with product IDs to start evaluation.

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

## Testing

### Test Cloud Storage Integration

```bash
# Test Cloud Storage upload/download
python test_gcs.py
```

### Test Full Pipeline

```bash
# Test with sample data
python app/main.py --input test_products.csv --output test_results.csv

# Check results
head -5 test_results.csv
```

### Test API Endpoints

```bash
# Start API server
uvicorn app.api:app --host 0.0.0.0 --port 8000

# In another terminal, test endpoints
curl -X POST "http://localhost:8000/evaluate" \
  -F "file=@test_products.csv"

# Check status and download results
```

## Deployment

### Local Development

```bash
# Run API
uvicorn app.api:app --host 0.0.0.0 --port 8000

# Run CLI
python app/main.py --input test.csv --output results.csv
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

- Processes ~1000 products in 1-2 hours
- Batch size: 5-10 concurrent evaluations
- Built-in retry logic for API failures

## Troubleshooting

- **VTEX API errors**: Check credentials and permissions
- **Gemini quota**: Monitor Google Cloud console
- **Database connection**: Verify Cloud SQL setup
- **Memory issues**: Increase Cloud Run memory for large CSVs

## License

This was a hobby project testing spec kit, nobody should use it really. But feel free