import duckdb
import os


def query_processed_jobs(sql_query):
    """
    Run a SQL query against all processed Parquet datasets.
    """

    parquet_path = "data/processed/*.parquet"

    if not os.path.exists("data/processed"):
        print("No processed datasets found.")
        return None

    conn = duckdb.connect()

    result = conn.execute(f"""
        SELECT *
        FROM read_parquet('{parquet_path}')
    """).df()

    if result.empty:
        print("No data available.")
        return None

    return conn.execute(sql_query).df()

def top_companies(limit=10):

    conn = duckdb.connect()

    return conn.execute("""
        SELECT company, COUNT(*) as jobs
        FROM read_parquet('data/processed/*.parquet')
        GROUP BY company
        ORDER BY jobs DESC
        LIMIT ?
    """, [limit]).df()


def top_skills(limit=10):

    conn = duckdb.connect()

    return conn.execute("""
        SELECT skills, COUNT(*) as frequency
        FROM read_parquet('data/processed/*.parquet')
        WHERE skills IS NOT NULL
        GROUP BY skills
        ORDER BY frequency DESC
        LIMIT ?
    """, [limit]).df()