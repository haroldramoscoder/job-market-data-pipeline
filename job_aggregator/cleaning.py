import pandas as pd
import re


def clean_jobs_dataframe(df):
    """
    Perform cleaning and normalization on the jobs dataset.
    """

    # ---- Normalize dates ----
    if "Date Posted" in df.columns:
        df["Date Posted"] = pd.to_datetime(
            df["Date Posted"],
            errors="coerce"
        ).dt.tz_localize(None)

    # ---- Remove invalid rows ----
    required_fields = ["Title", "Company", "URL"]

    for field in required_fields:
        if field in df.columns:
            df = df[df[field].notna()]

    # ---- Clean HTML from descriptions ----
    if "Description" in df.columns:

        def strip_html(text):
            if not text:
                return text

            clean = re.sub("<.*?>", "", str(text))
            return clean.strip()

        df["Description"] = df["Description"].apply(strip_html)

    # ---- Normalize remote locations ----
    if "Location" in df.columns:

        def normalize_location(loc):
            if not loc:
                return loc

            loc = str(loc).lower()

            if "remote" in loc:
                return "Remote"

            return loc.title()

        df["Location"] = df["Location"].apply(normalize_location)

    return df