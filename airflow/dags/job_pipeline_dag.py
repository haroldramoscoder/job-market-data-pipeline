from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys

sys.path.append("/opt/airflow/project")

from job_aggregator.main import main


def airflow_run():
    sys.argv = ["job-aggregator", "--keywords", "data"]
    main()


default_args = {
    "owner": "data_engineer",
    "start_date": datetime(2024, 1, 1),
}

with DAG(
    dag_id="job_pipeline",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
) as dag:

    run_pipeline = PythonOperator(
        task_id="run_job_pipeline",
        python_callable=airflow_run
    )