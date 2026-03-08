import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="Multi-source Job Aggregator")

    parser.add_argument(
        "--keywords",
        nargs="+",
        required=True,
        help="Keywords to search for"
    )

    parser.add_argument(
        "--days",
        type=int,
        default=None,
        help="Filter jobs posted within the last X days"
    )

    parser.add_argument(
        "--pages",
        type=int,
        default=5,
        help="Number of pages to fetch from The Muse"
    )

    parser.add_argument(
        "--strict",
        action="store_true",
        help="Disable keyword expansion"
    )

    parser.add_argument(
        "--format",
        choices=["excel", "csv", "json"],
        default="excel",
        help="Output format (excel, csv, json)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose (debug) logging"
    )

    parser.add_argument(
        "--logfile",
        type=str,
        default=None,
        help="Optional log file path"
    )

    parser.add_argument(
        "--use-raw",
        action="store_true",
        help="Process previously saved raw data instead of calling APIs"
    )

    return parser.parse_args()