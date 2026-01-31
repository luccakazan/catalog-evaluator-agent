# Research: Catalog Quality Evaluator

**Date**: 2026-01-31
**Plan**: [specs/001-catalog-quality-evaluator/plan.md](specs/001-catalog-quality-evaluator/plan.md)

## Research Tasks

### VTEX API Integration Best Practices
**Task**: Research VTEX Catalog API integration patterns for reliable product data fetching.

**Findings**:
- VTEX API uses App Key and App Token for authentication
- Rate limits apply; implement exponential backoff for retries
- API returns JSON with product details including description field
- Handle 4xx errors as permanent failures, 5xx as retryable
- Use requests library with session for connection reuse

**Decision**: Use requests with tenacity for retry logic and exponential backoff.
**Rationale**: Ensures reliability for sequential API calls without overwhelming VTEX servers.
**Alternatives considered**: Custom retry loop (rejected for complexity), aiohttp (rejected for sync simplicity).

### Google Gemini Batch Processing
**Task**: Research Google Gemini API for batch text evaluation.

**Findings**:
- Gemini API supports individual requests, not native batching
- For efficiency, send multiple requests concurrently with asyncio
- Use google-genai library for Python integration
- Prompt engineering needed for consistent quality scoring
- Cost optimization by batching prompts with multiple descriptions

**Decision**: Use google-genai with concurrent requests (5-10 parallel) for batch processing.
**Rationale**: Balances speed and cost while staying within API limits.
**Alternatives considered**: Sequential requests (slower), single batch prompt (less accurate).

### Cloud SQL PostgreSQL Connection
**Task**: Research secure Cloud SQL connection patterns for Python applications.

**Findings**:
- Use google-cloud-sql-connector for IAM authentication
- Supports connection pooling with SQLAlchemy
- Environment-based configuration for credentials
- Connection string format for psycopg2

**Decision**: Use google-cloud-sql-connector with psycopg2 for database operations.
**Rationale**: Secure, managed connection without exposing credentials.
**Alternatives considered**: Direct IP connection (less secure), Cloud SQL Proxy (more complex setup).

### CSV Processing with Pandas
**Task**: Research pandas for CSV handling in data processing scripts.

**Findings**:
- Efficient for reading/writing CSV files
- DataFrame operations for validation and transformation
- Memory efficient for 1000+ rows
- Error handling for malformed files

**Decision**: Use pandas for CSV I/O operations.
**Rationale**: Simplifies data handling and validation.
**Alternatives considered**: csv module (more verbose), openpyxl (unnecessary for CSV).

### Logging and Observability
**Task**: Research logging patterns for batch processing applications.

**Findings**:
- Use Python logging with structured format
- Log levels: INFO for progress, ERROR for failures, DEBUG for details
- Include timestamps, product IDs in logs
- Consider log aggregation for GCP deployment

**Decision**: Use Python logging with JSON format for structured logs.
**Rationale**: Enables monitoring and debugging of monthly runs.
**Alternatives considered**: Print statements (not structured), custom logger (unnecessary).

## Summary
All technical choices align with constitution principles: security (env vars, secure connections), reliability (retry logic, error handling), simplicity (standard libraries), testing (testable components), observability (structured logging).</content>
<parameter name="filePath">/Users/lucca.kazan/Documents/study_projects/catalog-evaluator-agent/specs/001-catalog-quality-evaluator/research.md