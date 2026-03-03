from setuptools import setup, find_packages

setup(
    name="job_aggregator",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "pandas",
        "openpyxl"
    ],
    entry_points={
        "console_scripts": [
            "job-aggregator=job_aggregator.main:main",
        ],
    },
)