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
* Keyword expansion for broader results
* Freshness filtering (`--days`)
* Pagination support (`--pages`)
* Deduplication by job listings
* Multiple output formats:
  - Excel
  - CSV
  - JSON
* Structured logging:
  - Verbose mode
  - Log file support
* Summary analytics (top companies, recent jobs, source breakdown, top skills)
* CLI interface for flexible searching
* Logging and debug mode

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
User keywords: ['data']
Expanded keywords: ['machine learning', 'data', 'analytics', 'scientist', 'python', 'ai', 'ml', 'analyst', 'sql']
2026-03-04 13:23:58,001 - INFO - RemoteOK processed
2026-03-04 13:23:58,785 - INFO - Remotive processed
2026-03-04 13:23:59,621 - INFO - Arbeitnow processed
2026-03-04 13:24:02,383 - INFO - The Muse processed

==================================================
JOB SUMMARY
==================================================
Total Jobs: 295

Jobs by Source:
  TheMuse: 99
  RemoteOK: 93
  Arbeitnow: 84
  Remotive: 19

Top 5 Companies:
  SpaceX: 12
  Apiron Group: 10
  Uber: 9
  acemate.ai: 8
  Bank of America: 7

Most Recent Job Posted: 2026-03-04 16:35:17
Jobs Posted in Last 7 Days: 55
==================================================


Top Skills in Job Market
------------------------------
machine learning: 4
analytics: 2
azure: 2

Saved 295 jobs to output/jobs_2026-03-04_13-24-02.xlsx
```
Output files are saved in the output/ directory.

## Job Market Skill Analysis

The tool also analyzes extracted job data to identify the most frequently mentioned skills across listings.

Example output:
```
Top Skills in Job Market
------------------------------
machine learning: 4
analytics: 2
azure: 2
```

## Project Structure
```
job-listing-automation
│
├── job_aggregator
│   ├── sources
│   │   ├── arbeitnow.py
│   │   ├── muse.py
│   │   ├── remoteok.py
│   │   └── remotive.py
│   │
│   ├── cli.py
│   ├── main.py
│   ├── skills.py
│   └── utils.py
│
├── tests
│   ├── test_keywords.py
│   └── test_utils.py
│
├── .github/workflows
│   └── python.yml
│
├── requirements.txt
├── setup.py
├── README.md
├── LICENSE
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