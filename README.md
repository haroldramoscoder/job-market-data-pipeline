# Job Aggregator CLI
![CI](https://github.com/haroldramoscoder/job-listing-automation/actions/workflows/python.yml/badge.svg)

A multi-source job aggregation command-line tool that fetches, filters, deduplicates, and analyzes job listings from multiple public job APIs.

This project demonstrates structured Python packaging, modular design, CLI implementation, automated testing, and CI integration.

---

## Features

* Aggregates jobs from multiple public APIs:
  - RemoteOK
  - Remotive
  - Arbeitnow
  - The Muse
* Keyword expansion with optional strict mode
* Freshness filtering (`--days`)
* Pagination support (`--pages`)
* Deduplication by job URL
* Multiple output formats:
  - Excel
  - CSV
  - JSON
* Structured logging:
  - Verbose mode
  - Log file support
* Summary analytics (top companies, recent jobs, source breakdown)
* Unit testing with pytest
* Continuous Integration via GitHub Actions

---

## Installation

Clone the repository:
```
git clone https://github.com/haroldramoscoder/job-listing-automation.git
cd job-listing-automation
```

## Install dependencies:

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
Filter jobs posted in the last 7 days:
```
job-aggregator --keywords data --days 7
```
Increase pagination (The Muse):
```
job-aggregator --keywords data --pages 10
```
Strict keyword mode (disable expansion):
```
job-aggregator --keywords data --strict
```
Change output format:
```
job-aggregator --keywords data --format csv
```
Enable verbose logging and save logs:
```
job-aggregator --keywords data --verbose --logfile app.log
```

## Example Output
```
==================================================
JOB SUMMARY
==================================================
Total Jobs: 278

Jobs by Source:
  TheMuse: 99
  RemoteOK: 94
  Arbeitnow: 65
  Remotive: 18

Top 5 Companies:
  K-tronik GmbH: 19
  SpaceX: 11
  Uber: 9
  Bank of America: 8
  Clean Harbors: 7

Most Recent Job Posted: 2026-03-03 16:35:32
Jobs Posted in Last 7 Days: 48
==================================================
```
Output files are saved in the output/ directory.

## Project Structure
```
job-listing-automation/
│
├── job_aggregator/
│   ├── __init__.py
│   ├── main.py
│   ├── cli.py
│   ├── utils.py
│   └── sources/
│       ├── remoteok.py
│       ├── remotive.py
│       ├── arbeitnow.py
│       └── muse.py
│
├── tests/
│   ├── test_keywords.py
│   └── test_utils.py
│
├── .github/workflows/
│   └── python.yml
│
├── requirements.txt
├── setup.py
├── README.md
└── .gitignore
```

## Future Improvements

* Salary normalization and comparison
* Async requests for improved performance
* Database integration (PostgreSQL / SQLite)
* Docker containerization
* Web dashboard interface
* API rate limiting handling improvements

## License

MIT License

## Author

Harold Ramos
Computer Engineering Student