# Performance Benchmark Analysis

## 1. Objective

The objective of this benchmark was to evaluate the performance and scalability of the Parquet Schema Drift Pipeline under different input batch sizes.

## 2. Benchmark Environment

- Language: Python
- Data processing: Pandas
- Storage format: Apache Parquet
- Parquet engine: PyArrow
- Operating system: Windows
- Execution: Local environment

## 3. Benchmark Results

Seven Parquet batches were generated for each benchmark configuration.

| Rows per batch | Total input rows | Execution time (seconds) | Throughput (rows/second) |
|---:|---:|---:|---:|
| 1,000 | 7,000 | 0.622 | 11,246.11 |
| 10,000 | 70,000 | 0.741 | 94,467.84 |
| 100,000 | 700,000 | 2.900 | 241,411.46 |

## 4. Data Quality Results

| Rows per batch | Schema quarantined | Record rejected | Published |
|---:|---:|---:|---:|
| 1,000 | 2,000 | 2 | 4,998 |
| 10,000 | 20,000 | 2 | 49,998 |
| 100,000 | 200,000 | 2 | 499,998 |

All benchmark runs completed with the status `SUCCESS_WITH_REJECTS`.

## 5. Performance Observations

- The pipeline processed 700,000 input rows in approximately 2.9 seconds in the largest benchmark.
- Throughput increased as batch size increased.
- Larger batches reduced the relative impact of fixed processing overhead.
- Schema-incompatible batches were quarantined without entering the publishing process.
- Record-level validation continued to reject invalid records while allowing valid records to be published.
- Published customer records maintained unique customer IDs.

## 6. Data Reconciliation

For every benchmark run:

**Input rows = Schema-quarantined rows + Record-rejected rows + Valid rows**

All three benchmark configurations satisfied this reconciliation.

## 7. Conclusion

The benchmark demonstrates that the pipeline can process increasingly large Parquet workloads while maintaining schema validation, record-level quality checks, quarantine handling, and idempotent publishing.

The results represent measurements from a local development environment. They are not production capacity guarantees. Repeated benchmark runs would provide a more reliable estimate of average performance and variability.

## 8. Reproducibility

Run the benchmark using:

`python -m scripts.benchmark`

The generated machine-readable results are available in:

- `reports/benchmark_results.csv`
- `reports/benchmark_results.json`