# Job Market Data Pipeline
![CI](https://github.com/haroldramoscoder/job-listing-automation/actions/workflows/python.yml/badge.svg)

Production-style **Data Engineering pipeline** that collects job postings from multiple APIs, builds a data lake architecture, and produces ML-ready datasets for analytics and business intelligence.

This project demonstrates modern **data engineering practices**, including:

- Async data ingestion
- Raw vs processed data layers
- Incremental data warehouse
- Airflow orchestration
- Docker containerization
- Pipeline monitoring and logging
- Skill demand analytics
- ML dataset preparation

---

## System Architecture
```
Job APIs
   ↓
Async Data Ingestion
   ↓
Raw Data Layer
   ↓
Cleaning + Validation
   ↓
Processed Data Layer
   ↓
Parquet Data Warehouse
   ↓
ML Dataset Export
   ↓
Skill Trend Analytics
   ↓
Pipeline Monitoring
   ↓
Airflow Scheduling
```
## Features

## Data Ingestion

Aggregates jobs from multiple APIs:

- RemoteOK
- Remotive
- Arbeitnow
- The Muse

Additional capabilities:

- Async API ingestion for faster pipeline execution
- Configurable API sources via `config/sources.yaml`

---

## Data Engineering Pipeline

- Raw data storage (data lake style)
- Cleaning and normalization pipeline
- Dataset validation and schema checks
- Incremental data warehouse updates
- Automatic deduplication of job listings

---

## Analytics

- Skill extraction from job descriptions
- Skill categorization by industry
- Job market trend tracking
- Top skill demand analysis
- Job change detection (new and removed jobs)

---

## ML & BI Integration

Exports structured datasets for downstream analysis.

Example dataset:
data/ml/job_market_dataset_YYYY-MM-DD.parquet

Used for:

- Machine learning models
- PowerBI dashboards
- Job market analytics

---

## Pipeline Observability

Pipeline monitoring includes:

- Structured logging
- Execution time tracking
- Pipeline run summaries
- Pipeline metadata logging

Metadata dataset:
data/pipeline_runs/pipeline_runs.parquet

---

## Infrastructure

- Docker containerization
- Airflow orchestration for scheduled runs
- Config-driven pipelines
- Automated dataset retention policies

## Data Layers

The pipeline follows a **modern data engineering architecture**.

---

## Raw Data Layer

Stores original API responses for reproducibility.
```
data/raw/
    remoteok/
    remotive/
    muse/
    arbeitnow/
```
Example:
```
data/raw/remoteok/2026-03-11.json
```
---

## Processed Data Layer

Cleaned datasets ready for analytics.
```
data/processed/jobs_YYYY-MM-DD.parquet
```
---

## Data Warehouse

Historical dataset of all collected jobs.
```
data/warehouse/jobs.parquet
```
Supports incremental ingestion and deduplication.

---

## ML Dataset

Structured dataset used for ML training and analytics.
```
data/ml/job_market_dataset_YYYY-MM-DD.parquet
```

Dataset fields:
```
job_id
title
company
location
date_posted
source
description
skills
```

## Installation

Clone the repository:

```
git clone https://github.com/haroldramoscoder/job-listing-automation.git
cd job-listing-automation
```

Install dependencies:
```
pip install -r requirements.txt
pip install -e .
```
This installs the CLI tool locally.

## Usage

Basic search:
```
job-aggregator --keywords data analyst
```
Optional arguments:
```
--days 7          Filter jobs posted within last 7 days
--pages 10        Number of pages to fetch from The Muse
--strict          Disable keyword expansion
--format csv      Export format (excel, csv, json)
--verbose         Enable debug logging
--logfile app.log Save logs to file
```

## Example Output
```
==================================================
JOB SUMMARY
==================================================
Total Jobs: 278

Jobs by Source:
  TheMuse: 99
  RemoteOK: 91
  Arbeitnow: 68
  Remotive: 20

Top 5 Companies:
  Uber: 10
  SpaceX: 10
  Bank of America: 8

Most Recent Job Posted: 2026-03-11
Jobs Posted in Last 7 Days: 72
==================================================

Top Skills in Job Market
------------------------------
python: 20
aws: 17
sql: 14
machine learning: 11
```
---

## Skill Trend Analytics

The pipeline tracks **skill demand trends over time**.

Example output:
```
Top Skills Last 30 Days

Python
SQL
AWS
Machine Learning
```

Trend dataset:
```
data/analytics/skill_trends.parquet
```

Used for job market analytics and dashboards.

---

## Pipeline Monitoring

Each pipeline run logs metadata such as:

- execution runtime
- jobs collected
- jobs after deduplication

Stored in:
```
data/pipeline_runs/pipeline_runs.parquet
```

---

## Running the Pipeline with Docker

Build and run the pipeline:

```
docker compose up --build
```

This launches the pipeline environment including Airflow.

## Airflow Orchestration

The project includes an Airflow DAG:
```
daily_job_pipeline
```
The pipeline runs automatically every 24 hours.

Pipeline steps:

1. Fetch job APIs
2. Save raw data
3. Clean and normalize data
4. Update data warehouse
5. Export ML dataset
6. Generate analytics datasets

## Project Structure
```
job-listing-automation
│
├── job_aggregator
│   ├── sources
│   ├── async_fetcher.py
│   ├── cleaning.py
│   ├── cli.py
│   ├── main.py
│   ├── skills.py
│   └── utils.py
│
├── dags
│   └── job_pipeline_dag.py
│
├── config
│   └── sources.yaml
│
├── data
│   ├── raw
│   ├── processed
│   ├── warehouse
│   ├── ml
│   └── analytics
│
├── tests
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── setup.py
└── README.md
```

## Future Improvements

* Salary normalization and compensation analytics
* Job market forecasting models
* Automated PowerBI dashboard
* Cloud deployment (AWS / GCP)
* Real-time streaming ingestion

## Technologies Used

* Python
* Pandas
* AsyncIO
* Docker
* Apache Airflow
* Parquet
* DuckDB
* GitHub Actions

## License
MIT License

## Author
Harold Ramos
Computer Engineering Student