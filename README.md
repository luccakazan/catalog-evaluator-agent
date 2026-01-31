# Catalog Quality Evaluator - Spec Kit Test

This is a quick hobby project to experiment with Spec Kit.

It builds a service that evaluates VTEX product catalog quality by fetching product data via API, analyzing descriptions with Google Gemini LLM, and storing results in CSV and Cloud SQL PostgreSQL.

## Features

- **CSV Processing**: Read product IDs from CSV files
- **VTEX Integration**: Fetch product details via VTEX Catalog API
- **AI Evaluation**: Analyze product descriptions using Google Gemini
- **Database Storage**: Persist results in Cloud SQL PostgreSQL
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

# Database (optional)
DB_INSTANCE_CONNECTION_NAME=project:region:instance
DB_NAME=catalog_evaluator
DB_USER=your_user
```

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