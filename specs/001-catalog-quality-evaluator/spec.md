# Feature Specification: Catalog Quality Evaluator

**Feature Branch**: `001-catalog-quality-evaluator`  
**Created**: 2026-01-31  
**Status**: Draft  
**Input**: User description: "This is a backend aplication that evaluates the catalog quality of a clients ecommerce hosted on VTEX. It expects to provide the following flow: 1 - The developer registers a csv file with a list of product_id from the clients VTEX product catalog (around 1000 product_id) 2 - The aplication hits VTEX catalog API to get the product information. The API allows us to get information for one product at a time, so we need error handling and reliability here. If one product fails, it should not break the entire process, but we need logs visilibity on it. More information on the API in the link: https://developers.vtex.com/docs/api-reference/catalog-api#get-/api/catalog/pvt/product/-productId- 3 - With the product information, the application should send it to be evaluated by an LLM with instructions to classify the content in the product description field in a 1 to 5 quality score. Being 1 excelent and 5 really bad. The process can be done in bulks (5 to 10 products at a time) to optime the application speed and cost. 4 - The result should be saved in a csv file and latter in a CPG database for consulting"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Evaluate Product Descriptions from CSV (Priority: P1)

As a developer, I want to upload a CSV file containing VTEX product IDs and receive quality scores for their product descriptions evaluated by an LLM.

**Why this priority**: This is the core functionality that enables catalog quality assessment, providing immediate value for identifying poor descriptions.

**Independent Test**: Can be fully tested by uploading a small CSV with 10 valid product IDs, processing it, and verifying that a results CSV is generated with quality scores for each product. This delivers standalone value as a basic evaluation tool.

**Acceptance Scenarios**:

1. **Given** a CSV file with a 'product_id' column containing valid VTEX product IDs, **When** the application processes the file, **Then** it fetches product data from VTEX API, evaluates descriptions via LLM, and saves results to a CSV with columns: product_id, quality_score, timestamp.
2. **Given** one product fetch fails due to invalid ID or API error, **When** processing the batch, **Then** the system logs the error, skips that product, and continues processing remaining products without crashing.
3. **Given** product descriptions to evaluate, **When** sent to LLM in batches of 5-10, **Then** each description receives a quality score from 1 (excellent) to 5 (very bad) based on content assessment.

---

### User Story 2 - Store Evaluation Results in GCP Database (Priority: P2)

As a developer, I want evaluation results to be stored in a GCP database for long-term storage and querying.

**Why this priority**: Enables data persistence and analysis beyond CSV files, supporting future reporting and insights.

**Independent Test**: Can be fully tested by taking evaluation results from CSV and successfully storing them in the GCP database, then querying to verify data integrity. This provides value for data management separate from evaluation.

**Acceptance Scenarios**:

1. **Given** evaluation results in CSV format, **When** uploaded to GCP database, **Then** data is stored in a structured table with proper indexing for querying.
2. **Given** stored evaluation data, **When** queried by product_id or date range, **Then** results are returned accurately and efficiently.

---

## Functional Requirements

Each requirement below is testable and unambiguous:

- **FR1**: System shall accept CSV input file with 'product_id' column containing VTEX product identifiers.
- **FR2**: For each product_id, system shall make authenticated API call to VTEX catalog endpoint to retrieve product information.
- **FR3**: System shall handle API failures gracefully: log errors with product_id and reason, skip failed products, continue processing batch.
- **FR4**: System shall extract product description field from VTEX API response for evaluation.
- **FR5**: System shall batch product descriptions (5-10 items) and send to LLM for quality classification.
- **FR6**: LLM shall evaluate description content and assign integer score 1-5 (1=excellent, 5=very bad) based on clarity, completeness, and accuracy.
- **FR7**: System shall output results to CSV file with columns: product_id, quality_score, evaluation_timestamp.
- **FR8**: System shall provide visibility into processing status via structured logs for each step.
- **FR9**: System shall integrate with Google Gemini for evaluation.
- **FR10**: System shall store results in Cloud SQL (PostgreSQL) for persistence.
- **FR11**: System shall implement exponential backoff with jitter to handle VTEX API constraints.

## Success Criteria

- **Processing Time**: System processes 1000 products in under 2 hours total execution time.
- **Reliability**: API call success rate exceeds 95% for valid product IDs.
- **Accuracy**: LLM evaluation accuracy >85% as measured by manual review of 100 random samples.
- **Error Handling**: System continues processing after individual failures, with <1% total failure rate.
- **Data Integrity**: All successful evaluations saved to CSV and database without data loss.
- **Observability**: All processing steps logged with timestamps and error details.

## Key Entities

- **Product**: Contains product_id (string), description (text), and other VTEX metadata.
- **EvaluationResult**: Contains product_id (string), quality_score (integer 1-5), evaluation_timestamp (datetime).

## Assumptions

- VTEX API credentials (app key, app token) are provided via environment variables.
- LLM API is accessible and configured with appropriate authentication.
- GCP database is pre-configured and accessible.
- Product descriptions are in text format suitable for LLM analysis.
- Network connectivity is stable during processing.
- CSV input contains valid VTEX product IDs.
