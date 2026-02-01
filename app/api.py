import uuid
import tempfile
import os
from datetime import datetime, timezone
from typing import Dict, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
import pandas as pd
from app.services.vtex_client import VtexClient
from app.services.gemini_evaluator import GeminiEvaluator
from app.services.cloud_storage import CloudStorageService
from app.utils.csv_handler import read_product_ids, write_evaluation_results
from app.models.product import Product
from app.models.evaluation_result import EvaluationResult
from app.utils.logger import get_logger

# Load environment variables
load_dotenv()

logger = get_logger(__name__)

app = FastAPI(title="Catalog Quality Evaluator API", version="1.0.0")

# In-memory job storage (for production, use database or Redis)
jobs: Dict[str, Dict] = {}


@app.get("/health")
async def health_check() -> Dict:
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


@app.post("/evaluate")
async def evaluate_catalog(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
) -> Dict:
    """Start catalog quality evaluation job."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV")

    # Generate job ID
    job_id = str(uuid.uuid4())

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
        content = await file.read()
        temp_file.write(content)
        input_file = temp_file.name

    # Initialize job status
    jobs[job_id] = {
        'status': 'processing',
        'started_at': datetime.now(timezone.utc),
        'input_file': input_file,
        'progress': {'processed': 0, 'total': 0, 'errors': 0}
    }

    # Start background processing
    background_tasks.add_task(process_evaluation_job, job_id)

    logger.info("Started evaluation job", extra={'job_id': job_id})

    return {
        'job_id': job_id,
        'status': 'processing',
        'message': 'Evaluation started'
    }


@app.get("/status/{job_id}")
async def get_job_status(job_id: str) -> Dict:
    """Get evaluation job status."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    return {
        'job_id': job_id,
        'status': job['status'],
        'progress': job.get('progress', {}),
        'started_at': job['started_at'].isoformat(),
        'completed_at': job.get('completed_at', '').isoformat() if 'completed_at' in job else None
    }


@app.get("/results/{job_id}")
async def get_job_results(job_id: str):
    """Download evaluation results CSV."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    if job['status'] != 'completed':
        raise HTTPException(status_code=404, detail="Job not completed")

    results_file = job.get('results_file')
    if not results_file:
        raise HTTPException(status_code=404, detail="Results file not found")

    # Check if results are in Cloud Storage (GCS URL) or local file
    if results_file.startswith('gs://'):
        # Download from Cloud Storage
        try:
            bucket_name = os.getenv('GCS_BUCKET_NAME', 'catalog-evaluator-results')
            filename = f"results_{job_id}.csv"
            
            storage_service = CloudStorageService()
            csv_content = storage_service.download_results_csv(filename)
            
            def iter_content():
                yield csv_content.encode('utf-8')
            
            return StreamingResponse(
                iter_content(),
                media_type='text/csv',
                headers={"Content-Disposition": f"attachment; filename=results_{job_id}.csv"}
            )
        except Exception as e:
            logger.error(f"Failed to download from Cloud Storage: {e}")
            raise HTTPException(status_code=500, detail="Failed to download results")
    else:
        # Local file fallback
        if not os.path.exists(results_file):
            raise HTTPException(status_code=404, detail="Results file not found")

        def iter_file():
            with open(results_file, 'rb') as f:
                yield from f

        return StreamingResponse(
            iter_file(),
            media_type='text/csv',
            headers={"Content-Disposition": f"attachment; filename=results_{job_id}.csv"}
        )


def process_evaluation_job(job_id: str):
    """Background task to process evaluation job."""
    try:
        job = jobs[job_id]
        input_file = job['input_file']

        # Read product IDs
        product_ids = read_product_ids(input_file)
        job['progress']['total'] = len(product_ids)

        # Initialize services
        vtex_client = VtexClient()
        gemini_evaluator = GeminiEvaluator()
        
        # Initialize Cloud Storage (cheaper than database!)
        storage_service = CloudStorageService()
        storage_service.ensure_bucket_exists()
        
        # Optional database service (only if configured)
        db_service = None
        if os.getenv('DB_INSTANCE_CONNECTION_NAME') and os.getenv('DB_INSTANCE_CONNECTION_NAME') != 'your_project:region:instance':
            try:
                from app.services.database import DatabaseService
                db_service = DatabaseService()
            except ImportError as e:
                logger.warning(f"Database dependencies not installed: {e}. Using Cloud Storage only.")
            except Exception as e:
                logger.warning(f"Database initialization failed: {e}. Using Cloud Storage only.")

        # Fetch products and prepare evaluation results
        products = []
        evaluation_results = []
        
        for i, product_id in enumerate(product_ids):
            try:
                product = vtex_client.get_product(product_id)
                if product and product.description:
                    products.append(product)
                else:
                    # Product not found or no description - create error result
                    error_result = EvaluationResult(
                        product_id=product_id,
                        quality_score=0,
                        evaluation_timestamp=datetime.now(timezone.utc),
                        reason="Product not found in VTEX catalog or has no description",
                        raw_response="VTEX_API_ERROR"
                    )
                    evaluation_results.append(error_result)
                    logger.warning(f"Product {product_id} not found or has no description",
                                 extra={'product_id': product_id})
            except Exception as e:
                # API error - create error result
                error_result = EvaluationResult(
                    product_id=product_id,
                    quality_score=0,
                    evaluation_timestamp=datetime.now(timezone.utc),
                    reason=f"VTEX API error: {str(e)}",
                    raw_response="VTEX_API_ERROR"
                )
                evaluation_results.append(error_result)
                logger.error(f"Failed to fetch product {product_id}: {e}",
                           extra={'product_id': product_id})
            
            job['progress']['processed'] = i + 1
            job['progress']['errors'] += 1 if evaluation_results and evaluation_results[-1].quality_score == 0 else 0

        # Evaluate products with Gemini (only successful fetches)
        if products:
            gemini_results = gemini_evaluator.evaluate_products(products)
            evaluation_results.extend(gemini_results)
        else:
            logger.info("No products available for AI evaluation")

        # Store results in database (optional)
        if evaluation_results:
            if db_service:
                try:
                    db_service.store_evaluation_results(products, evaluation_results)
                except Exception as e:
                    logger.warning(f"Database storage failed: {e}. Results stored in Cloud Storage only.")
            
            # Always store results in Cloud Storage (much cheaper!)
            try:
                gcs_filename = f"results_{job_id}.csv"
                gcs_url = storage_service.upload_results_csv(evaluation_results, gcs_filename)
                job['results_file'] = gcs_url
                logger.info(f"Results stored in Cloud Storage: {gcs_url}")
            except Exception as e:
                logger.error(f"Cloud Storage upload failed: {e}")
                # Fallback: store locally
                with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
                    write_evaluation_results(evaluation_results, temp_file.name)
                    job['results_file'] = temp_file.name
                    logger.warning("Using local storage as fallback")
        else:
            logger.warning("No evaluation results to store")

        # Update job status
        job['status'] = 'completed'
        job['completed_at'] = datetime.now(timezone.utc)

        logger.info("Completed evaluation job", extra={'job_id': job_id})

    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}", extra={'job_id': job_id})
        job['status'] = 'failed'
        job['error'] = str(e)
    finally:
        # Cleanup input file
        if os.path.exists(input_file):
            os.unlink(input_file)