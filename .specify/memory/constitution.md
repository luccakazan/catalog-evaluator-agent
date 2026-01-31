# Catalog Evaluator Agent Constitution
<!-- 
Sync Impact Report:
Version change: N/A → 1.0.0
List of modified principles: All principles added (new constitution)
Added sections: Technical Requirements, Development and Deployment Workflow
Removed sections: None
Templates requiring updates: plan-template.md (Constitution Check section needs to reflect new principles)
Follow-up TODOs: None
-->

## Core Principles

### I. Security and Data Protection
All sensitive data, including client API keys and processed entries, must be handled securely using industry-standard encryption, environment variables, and access controls. No secrets shall be hardcoded in source code. Data processing must comply with data protection best practices to prevent unauthorized access or leakage.

### II. Reliability and Trustworthiness
The system must be highly reliable for monthly bulk processing of hundreds of entries using Generative AI. Implement comprehensive error handling, logging, input validation, and output verification to ensure trustworthy results. Failures must be graceful and recoverable without data loss.

### III. Simplicity and Speed
Keep the implementation simple, maintainable, and fast to build and deploy. Use Python best practices and avoid unnecessary complexity. Prioritize clarity and efficiency in code and architecture to enable rapid development by machine learning engineers.

### IV. Testing and Validation
Comprehensive testing is required for all critical paths, including unit tests, integration tests, and validation of Generative AI outputs. Tests must cover security measures, data processing accuracy, and error scenarios. Automated testing shall be prioritized to ensure reliability.

### V. Observability and Monitoring
Implement structured logging and monitoring capabilities for all processing runs. Monthly executions must be observable with clear metrics on success rates, processing times, and error conditions. Logs must be secure and not expose sensitive data.

## Technical Requirements
The project must use Python as the primary language, suitable for machine learning engineers. It shall run locally for development and testing, and be deployable on Google Cloud Platform (GCP) with API exposure. Generative AI usage must be responsible, with proper validation and ethical considerations. The system is designed for low-scale usage (once monthly, hundreds of entries) but must maintain enterprise-grade security and reliability practices.

## Development and Deployment Workflow
Development occurs locally with proper environment isolation. Deployment targets GCP infrastructure with API endpoints for client access. Code reviews must verify compliance with all principles. Security audits are required before production deployments. Changes to sensitive data handling require additional approval.

## Governance
This constitution supersedes all other project practices and guidelines. Amendments require documentation, team consensus, and justification for changes. Versioning follows semantic versioning. All development activities must demonstrate compliance with these principles. Constitution violations must be resolved before proceeding with implementation.

**Version**: 1.0.0 | **Ratified**: 2026-01-31 | **Last Amended**: 2026-01-31
