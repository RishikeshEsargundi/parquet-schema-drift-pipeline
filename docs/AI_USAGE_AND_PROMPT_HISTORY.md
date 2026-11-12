# AI Usage and Prompt History

## 1. AI Tool Used

**Tool:** ChatGPT by OpenAI

ChatGPT was used as an AI assistance tool during the development of this project.

No other AI tools were used for this project.

## 2. Purpose of AI Assistance

ChatGPT assisted with the following development activities:

- Understanding the project requirements and breaking the work into implementation phases.
- Planning the Python project structure and module responsibilities.
- Developing guidance for Parquet schema inspection and schema drift detection.
- Implementing schema compatibility and approved schema evolution logic.
- Designing data transformation and record validation.
- Implementing file quarantine and publishing logic.
- Developing automated test cases using Pytest.
- Debugging issues identified during test execution.
- Designing integration tests for pipeline failure and recovery.
- Developing a performance benchmarking script.
- Interpreting benchmark results.
- Preparing project documentation and submission checklists.

## 3. Prompt History

The prompts below summarize the main development requests made to ChatGPT. They are organized by development phase.

**Note:** This section is a categorized summary, not a verbatim export of every prompt submitted. The original conversation should be retained as supporting prompt-history evidence.

### Phase 1: Project planning and architecture

- Help me build the Data Engineering assignment step by step.
- Explain the project structure and responsibilities of the different Python modules.
- Guide me through implementing the pipeline incrementally.

### Phase 2: Schema drift detection

- Help implement Parquet schema inspection using PyArrow.
- Explain how to detect added, missing and incompatible columns.
- Help distinguish approved schema additions from breaking schema changes.

### Phase 3: Transformation and quarantine

- Help normalize compatible Parquet batches into a target schema.
- Help implement file-level quarantine for incompatible schemas.
- Explain how to preserve original input files and quarantine metadata.

### Phase 4: Record validation and publishing

- Help implement record-level validation rules.
- Help handle duplicate customer IDs and select the latest record.
- Help implement idempotent Parquet publishing.

### Phase 5: Pipeline integration and monitoring

- Help combine the individual processing components into an integrated pipeline.
- Help implement execution logging and run-level JSON reports.
- Help verify record reconciliation and pipeline execution status.

### Phase 6: Automated testing

- Help create Pytest tests for schema detection, validation and publishing.
- Help test quarantine preservation.
- Help test empty input, malformed Parquet files, successful publishing and recovery after failure.
- Help troubleshoot test failures.

### Phase 7: Performance benchmarking

- Help create a reproducible benchmark for different Parquet batch sizes.
- Help measure execution duration, throughput and input/output sizes.
- Help resolve a Windows file-lock error during temporary-directory cleanup.
- Help interpret benchmark results and prepare a performance analysis report.

### Phase 8: Submission documentation

- Help review the YottaFlex AI submission guidelines and FAQ.
- Help prepare the README.
- Help identify missing submission requirements.
- Help prepare this AI usage disclosure and prompt-history document.

## 4. Areas Where AI Accelerated Development

ChatGPT accelerated development by helping structure the implementation into manageable stages, suggesting test scenarios, explaining Python and PyArrow concepts, and assisting with debugging.

It also helped prepare documentation and interpret observed test and benchmark results.

## 5. Areas of Significant AI Assistance

AI assistance was substantial in:

- Initial architecture and implementation planning.
- Guidance and code drafting for several pipeline components.
- Automated test design.
- Integration-test design.
- Benchmark script development.
- Documentation preparation.

The project should therefore be understood as AI-assisted development rather than code written entirely without AI assistance.

## 6. Candidate Review and Validation

The candidate worked through the implementation in a local Windows and VS Code environment using Python and a virtual environment.

The candidate executed the scripts and reviewed actual terminal output during development.

Observed validation activities included:

- Generating synthetic Parquet input batches.
- Running schema inspection and compatibility checks.
- Executing transformation and validation scripts.
- Verifying quarantine outputs.
- Checking published customer records for duplicate IDs.
- Running the integrated pipeline.
- Executing the automated test suite.
- Running performance benchmarks at three batch sizes.

The complete automated test suite reported **25 passing tests**.

The performance benchmark processed up to **700,000 input rows** in approximately **2.9 seconds** in the local development environment.

The candidate should be prepared to explain the implementation, design choices, dependencies, assumptions and limitations during the project review.

## 7. Limitations of Prompt History

This document provides a categorized summary of the main prompts used during development. It is not a verbatim transcript of every prompt.

The ChatGPT conversation should be retained as additional supporting evidence of the development process.

## 8. Declaration

I acknowledge that ChatGPT was used as an AI assistance tool during this project. I have run the implementation in my development environment and reviewed its behavior through execution, automated tests and performance benchmarks.

I understand that responsibility for the submitted project, its correctness, design decisions and explanation remains mine.