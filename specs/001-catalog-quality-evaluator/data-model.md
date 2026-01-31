# Data Model: Catalog Quality Evaluator

**Date**: 2026-01-31
**Plan**: [specs/001-catalog-quality-evaluator/plan.md](specs/001-catalog-quality-evaluator/plan.md)

## Entities

### Product
Represents a VTEX product fetched from the catalog API.

**Fields**:
- `product_id` (string, required): Unique VTEX product identifier
- `description` (string, optional): Product description text for evaluation
- `name` (string, optional): Product name
- `category` (string, optional): Product category
- `brand` (string, optional): Product brand

**Validation Rules**:
- `product_id` must be non-empty string
- `description` must be string if present (can be empty for evaluation as poor quality)

**Relationships**:
- One-to-one with EvaluationResult (via product_id)

### EvaluationResult
Represents the quality evaluation result for a product description.

**Fields**:
- `product_id` (string, required): References Product.product_id
- `quality_score` (integer, required): Quality score 0-5 (0=error/not found, 1=excellent, 5=very bad)
- `evaluation_timestamp` (datetime, required): When evaluation was performed
- `reason` (string, optional): Human-readable explanation of the evaluation
- `raw_response` (string, optional): Raw LLM response for debugging

**Validation Rules**:
- `quality_score` must be integer between 0 and 5
- `evaluation_timestamp` must be valid datetime
- `product_id` must reference existing product or be a failed lookup

**Relationships**:
- References Product (via product_id)

## Database Schema (Cloud SQL PostgreSQL)

```sql
CREATE TABLE products (
    product_id VARCHAR(255) PRIMARY KEY,
    description TEXT,
    name VARCHAR(255),
    category VARCHAR(255),
    brand VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE evaluation_results (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(255) NOT NULL REFERENCES products(product_id),
    quality_score INTEGER NOT NULL CHECK (quality_score >= 0 AND quality_score <= 5),
    evaluation_timestamp TIMESTAMP NOT NULL,
    reason TEXT,
    raw_response TEXT,
    UNIQUE(product_id)
);

-- Indexes for performance
CREATE INDEX idx_evaluation_results_product_id ON evaluation_results(product_id);
CREATE INDEX idx_evaluation_results_timestamp ON evaluation_results(evaluation_timestamp);
```

## Data Flow

1. CSV input → Product entities (in-memory)
2. Product entities → VTEX API → enriched Product entities
3. Product entities → LLM evaluation → EvaluationResult entities
4. EvaluationResult entities → CSV output + database storage

## Constraints

- Product IDs must be unique across processing runs
- Evaluation results are immutable (no updates, only inserts)
- Failed evaluations are logged but not stored in database
- Data retention: As needed for client (not specified in requirements)</content>
<parameter name="filePath">/Users/lucca.kazan/Documents/study_projects/catalog-evaluator-agent/specs/001-catalog-quality-evaluator/data-model.md