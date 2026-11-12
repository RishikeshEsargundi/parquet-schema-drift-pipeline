# Parquet Schema Drift Pipeline

A Python-based data engineering project that ingests multiple Parquet batches, detects schema drift, applies approved schema evolution, validates records, quarantines incompatible data, and publishes a deduplicated customer dataset.

Developed as part of the YottaFlex AI Candidate Project.

---

## 1. Project Overview

Data engineering pipelines frequently receive datasets with changing schemas. Some changes are backward-compatible, such as adding optional columns, while others can break downstream processing, such as changing the data type of a required column or removing a required field.

This project implements a local Parquet processing pipeline to handle these scenarios safely.

### Key capabilities

- Ingest multiple Parquet batches.
- Detect schema differences against a predefined target schema.
- Support approved schema additions.
- Identify incompatible schema changes.
- Quarantine incompatible Parquet files.
- Normalize compatible datasets into a consistent target structure.
- Perform record-level data validation.
- Separate valid and rejected records.
- Publish a deduplicated customer dataset.
- Generate execution logs and run-level JSON reports.
- Support automated testing and performance benchmarking.

## 2. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Pipeline implementation |
| Pandas | DataFrame processing and validation |
| PyArrow | Parquet reading, writing and schema inspection |
| Pytest | Automated testing |
| JSON | Run reports and quarantine metadata |
| CSV | Benchmark result export |

The project runs locally and does not require a hosted data platform.

## 3. Architecture and Data Flow

The pipeline follows this processing sequence:

1. **Ingestion:** Discover incoming Parquet files from the input directory.
2. **Schema detection:** Inspect incoming schemas and compare them against the target schema.
3. **Schema compatibility:** Identify approved additions, missing required columns, incompatible data types and unapproved columns.
4. **Schema quarantine:** Copy incompatible Parquet files into quarantine and generate metadata describing the incompatibility.
5. **Transformation:** Normalize compatible batches into the target column structure and data types.
6. **Record validation:** Apply data quality checks to individual records.
7. **Record quarantine:** Store rejected records separately with their rejection reasons.
8. **Publishing:** Select the latest valid record for each customer ID and publish the target dataset.
9. **Monitoring:** Record execution metrics, status, duration and reconciliation results.

### Architecture flow

```text
             Parquet Input Batches
                      |
                      v
                Schema Detection
                      |
                      v
              Schema Compatibility
                 /          \
                /            \
        Compatible         Incompatible
            |                    |
            v                    v
       Transformation       File Quarantine
            |                    |
            v                    v
      Record Validation     Quarantine Metadata
          /       \
         /         \
      Valid       Rejected
        |             |
        v             v
    Publishing   Record Quarantine
        |
        v
  Customer Target Dataset
        |
        v
  Run Reports and Logs
```

## 4. Target Schema and Evolution Policy

The pipeline uses a predefined target schema.

| Column | Expected type | Classification |
|---|---|---|
| customer_id | int64 | Required |
| customer_name | string | Required |
| age | int64 | Required |
| email | string | Required |
| updated_at | timestamp | Required |
| city | string | Optional |
| salary | float64 | Optional |

### Compatible changes

The pipeline accepts the following approved schema changes:

- Addition of the optional `city` column.
- Addition of the optional `salary` column.
- Absence of optional columns, which are normalized into the target structure.

### Incompatible changes

The pipeline identifies the following changes as incompatible:

- Changing the data type of a required column.
- Removing a required column.
- Introducing an unapproved column.

Incompatible batches are quarantined rather than silently converted.

## 5. Record-Level Data Validation

Compatible batches undergo record-level validation.

The implemented validation rules include:

- Customer ID must not be null.
- Customer name must not be null or empty.
- Age must be numeric and between 18 and 100, inclusive.
- Email must match the configured email validation pattern.
- Updated timestamp must be parseable.
- Salary, when present, must be numeric and non-negative.
- Duplicate customer IDs within a batch are resolved by retaining the latest timestamp and source-row order.

Rejected records retain source information and rejection reasons to support investigation.

## 6. Publishing Strategy

Valid records from compatible batches are combined before publishing.

The publishing process:

- Selects the latest record for each customer ID.
- Uses timestamp and source information to resolve ties.
- Checks that customer IDs are unique.
- Writes through a temporary Parquet file before replacing the target.

The published customer dataset is stored at:

`data/target/customers.parquet`

The publisher is tested for idempotent output when the same valid dataset is published repeatedly.

## 7. Project Structure

```text
parquet-schema-drift-pipeline/
│
├── data/
│   ├── input/
│   ├── output/
│   ├── quarantine/
│   ├── target/
│   └── expected/
│
├── src/
│   ├── __init__.py
│   ├── logger.py
│   ├── pipeline.py
│   ├── publisher.py
│   ├── quarantine.py
│   ├── schema_detector.py
│   ├── transformer.py
│   └── validator.py
│
├── scripts/
│   ├── generate_data.py
│   ├── process_batches.py
│   ├── check_schemas.py
│   ├── check_rejections.py
│   ├── validate_records.py
│   ├── publish_target.py
│   ├── verify_outputs.py
│   ├── verify_target.py
│   ├── verify_run_report.py
│   └── benchmark.py
│
├── tests/
│   ├── test_validator.py
│   ├── test_schema_detector.py
│   ├── test_publisher.py
│   ├── test_quarantine.py
│   └── test_pipeline.py
│
├── reports/
│   ├── benchmark_results.csv
│   ├── benchmark_results.json
│   └── performance_analysis.md
│
├── docs/
│
├── requirements.txt
├── README.md
└── .gitignore
```

The `data/` directory contains synthetic input data and generated pipeline outputs. Generated files and temporary artifacts should not be committed unless they are intentionally included as supporting sample artifacts.

## 8. Installation and Setup

### Prerequisites

- Python installed.
- Git installed.
- Windows PowerShell or another compatible terminal.

### Clone the repository

```powershell
git clone <YOUR_PUBLIC_GITHUB_REPOSITORY_URL>
cd parquet-schema-drift-pipeline
```

### Create a virtual environment

```powershell
python -m venv venv
```

### Activate the environment

```powershell
.\venv\Scripts\Activate.ps1
```

### Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The project dependencies are:

- pandas
- pyarrow
- pytest

## 9. Running the Project

### Step 1: Generate synthetic input data

```powershell
python -m scripts.generate_data
```

The generator creates sample Parquet batches demonstrating compatible and incompatible schema changes, duplicate records and record-quality scenarios.

### Step 2: Run the integrated pipeline

```powershell
python -m src.pipeline
```

The integrated pipeline processes the input batches and generates normalized data, quarantine artifacts, published output, logs and a run-level JSON report.

### Step 3: Verify the run report

```powershell
python -m scripts.verify_run_report
```

### Additional verification commands

Check detected schemas:

```powershell
python -m scripts.check_schemas
```

Check rejected records:

```powershell
python -m scripts.check_rejections
```

Verify generated outputs:

```powershell
python -m scripts.verify_outputs
```

Verify the published target:

```powershell
python -m scripts.verify_target
```

The repository also contains separate scripts for processing, validation and publishing individual stages.

## 10. Automated Testing

Run the complete test suite:

```powershell
python -m pytest -v
```

### Test coverage

| Component | Number of tests |
|---|---:|
| Schema detection | 7 |
| Record validation | 10 |
| Publishing | 3 |
| Quarantine | 1 |
| Pipeline integration | 4 |
| **Total** | **25** |

### Verified test result

```text
25 passed in 2.70s
```

The test suite covers:

- Compatible and incompatible schema changes.
- Missing required columns and unapproved columns.
- Invalid records and age boundaries.
- Duplicate customer ID handling.
- Empty input handling.
- Malformed Parquet files.
- Quarantine preservation.
- Publishing idempotency.
- Pipeline failure reporting.
- Recovery after correcting malformed input.

This result was observed in the development environment. Test execution time may vary across machines.

## 11. Performance Benchmarking

Run the benchmark:

```powershell
python -m scripts.benchmark
```

The benchmark generates seven synthetic Parquet batches for each configured batch size.

### Observed benchmark results

| Rows per batch | Total input rows | Execution time | Throughput |
|---:|---:|---:|---:|
| 1,000 | 7,000 | 0.622 sec | 11,246.11 rows/sec |
| 10,000 | 70,000 | 0.741 sec | 94,467.84 rows/sec |
| 100,000 | 700,000 | 2.900 sec | 241,411.46 rows/sec |

The largest benchmark processed 700,000 input rows in approximately 2.9 seconds.

### Benchmark observations

- Throughput increased with larger batch sizes.
- Fixed processing overhead had a greater relative impact on smaller workloads.
- Schema-incompatible batches were quarantined.
- Record-level validation continued to reject invalid records while allowing valid records to be published.
- Published customer records maintained unique customer IDs.

### Benchmark output files

- `reports/benchmark_results.csv`
- `reports/benchmark_results.json`
- `reports/performance_analysis.md`

These measurements were collected on a local Windows development environment. They are environment-specific and are not production performance guarantees.

## 12. Sample Pipeline Execution Results

In the sample development run, the pipeline processed seven input batches.

| Metric | Observed result |
|---|---:|
| Total input rows | 142 |
| Schema-quarantined rows | 40 |
| Record-level rejected rows | 8 |
| Valid rows | 94 |
| Published rows | 94 |
| Final status | SUCCESS_WITH_REJECTS |

The row reconciliation was:

```text
142 = 40 + 8 + 94
```

The pipeline also verified that the published customer IDs were unique.

## 13. Monitoring and Run Reports

Each integrated pipeline execution generates a unique run ID.

The JSON report records execution information including:

- Run ID and timestamps.
- Total input rows.
- Accepted and quarantined batches.
- Schema-quarantined rows.
- Valid and rejected record counts.
- Published record count.
- Execution duration.
- Final pipeline status.
- Failure information, when applicable.

Execution logs are written to the `logs/` directory.

## 14. Assumptions and Limitations

- The project is designed as a local Python batch-processing solution.
- The target schema and approved optional columns are predefined.
- Schema-incompatible files are quarantined rather than automatically coerced.
- Record validation follows the rules implemented in the validator module.
- Duplicate resolution uses the available timestamp and source-row ordering information.
- The publishing process produces a customer snapshot from the records supplied in that run; it is not a distributed database or streaming system.
- Distributed execution, cloud orchestration, schema registries and production-scale monitoring are outside the current implementation scope.
- Benchmark measurements depend on the local machine and environment.

## 15. AI Usage and Development Transparency

AI assistance was used during development for implementation guidance, debugging, test design, benchmarking and documentation.

A separate document is provided to describe the AI tools used, prompt history, areas where AI accelerated development, and the implementation decisions and validation reviewed by the candidate.

See:

`docs/AI_USAGE_AND_PROMPT_HISTORY.md`

## 16. Author and Submission

Prepared as an individual candidate project submission for the YottaFlex AI Recruitment Drive.

The implementation, design choices, testing results, assumptions and limitations should be reviewed and understood by the candidate before submission.