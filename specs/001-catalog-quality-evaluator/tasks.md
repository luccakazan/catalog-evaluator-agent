# Tasks: Catalog Quality Evaluator

**Input**: Design documents from `/specs/001-catalog-quality-evaluator/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are not explicitly requested in the feature specification, so no test tasks are included. Basic testing can be added during implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend service**: `app/`, `tests/` at repository root
- Adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project structure per implementation plan in app/ directory
- [X] T002 Update requirements.txt with dependencies: google-genai, google-cloud-sql-connector, psycopg2-binary, pandas
- [ ] T003 Setup environment configuration with .env template and validation

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 [P] Implement logging infrastructure in app/utils/logger.py
- [X] T005 [P] Create data models in app/models/product.py and app/models/evaluation_result.py
- [X] T006 [P] Implement CSV handler utility in app/utils/csv_handler.py
- [X] T007 [P] Setup database connection service in app/services/database.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

## Phase 3: User Story 1 - Evaluate Product Descriptions from CSV (Priority: P1) 🎯 MVP

**Goal**: Enable processing of CSV files with VTEX product IDs to generate quality scores for product descriptions using Google Gemini LLM.

**Independent Test**: Can be fully tested by uploading a CSV with 10 valid product IDs, processing it, and verifying that a results CSV is generated with quality scores (1-5) for each product. This delivers standalone value as a basic evaluation tool.

- [X] T008 Implement VTEX client service with API authentication and product fetching in app/services/vtex_client.py
- [X] T009 Implement Gemini evaluator service with batch processing (5-10 products) in app/services/gemini_evaluator.py
- [X] T010 Create main pipeline logic to orchestrate CSV reading, API calls, evaluation, and CSV writing in app/main.py
- [X] T011 Add error handling and exponential backoff retry logic for VTEX API failures
- [X] T012 Integrate all components and add command-line interface for CSV input/output

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

## Phase 4: User Story 2 - Store Evaluation Results in GCP Database (Priority: P2)

**Goal**: Enable persistence of evaluation results in Cloud SQL PostgreSQL database for long-term storage and querying.

**Independent Test**: Can be fully tested by taking evaluation results from CSV and successfully storing them in the database, then querying to verify data integrity. This provides value for data management separate from evaluation.

- [X] T013 Implement database service methods for storing and retrieving evaluation results in app/services/database.py
- [X] T014 Add database storage integration to the main pipeline
- [X] T015 Create database schema migration script for Cloud SQL setup

**Checkpoint**: At this point, User Story 2 should be fully functional and testable independently

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: API exposure, deployment readiness, and final improvements

- [X] T016 Add FastAPI endpoints for CSV upload and result retrieval in app/api.py
- [X] T017 Implement job status tracking and async processing for API
- [X] T018 Add comprehensive observability with structured logging and metrics
- [X] T019 Create Dockerfile and deployment configuration for Cloud Run
- [X] T020 Update README.md and deployment documentation

## Dependencies

**Story Completion Order**:
1. US1 (Evaluate CSV) → US2 (Store in DB) - US1 must be complete before US2 can integrate database storage
2. Foundation → US1/US2 - All foundational tasks must complete first

**Task Dependencies**:
- T008-T012 depend on T004-T007 (foundation)
- T013-T015 depend on T008-T012 (US1 complete)
- T016-T020 can run in parallel with US1/US2 but depend on foundation

## Parallel Execution Opportunities

**Within Foundation (Phase 2)**: All tasks T004-T007 can run in parallel as they create independent utilities.

**Within US1 (Phase 3)**: T008 (VTEX client) and T009 (Gemini evaluator) can be developed in parallel, then integrated in T010-T012.

**Within US2 (Phase 4)**: T013 and T015 can run in parallel, then T014 integrates them.

**Cross-Phase**: Once foundation is complete, US1 and US2 can be developed in parallel by different team members.

## Implementation Strategy

**MVP Scope**: Complete Phase 1-3 (US1) for basic CSV evaluation functionality.

**Incremental Delivery**: 
- Week 1: Foundation + US1 core (CSV processing)
- Week 2: US2 (database storage) + Polish (API, deployment)

**Risk Mitigation**: Start with small CSV tests (10 products) before scaling to 1000+ products.</content>
<parameter name="filePath">/Users/lucca.kazan/Documents/study_projects/catalog-evaluator-agent/specs/001-catalog-quality-evaluator/tasks.md