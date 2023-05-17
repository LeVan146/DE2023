

import subprocess
import argparse
from pathlib import Path
import pandas as pd
from prefect import flow, task, get_run_logger
from prefect_gcp.cloud_storage import GcsBucket


@task(name="Submit spark job", log_prints=True)
def spark_submit(file: str, data_names: list):
    logger = get_run_logger()
    logger.info(f"Starting job: {file}")
    res = subprocess.run(
        [
            "gcloud",
            "dataproc",
            "jobs",
            "submit",
            "pyspark",
            "--cluster=van-de23-cluster",
            "--region=us-central1",
            "--jars=gs://spark-lib/bigquery/spark-bigquery-latest_2.12.jar",
            file,
            "--",
            f"--input_0={data_names[0]}",
            f"--input_1={data_names[1]}",
            f"--input_2={data_names[2]}"
        ]
    )
    logger.info(f"Job status code: {res.returncode}")




@flow(name="from_BQ_to_BQ", log_prints=True)
def from_bq_to_bq(data_names) -> None:
    """ The main ETL function"""
    logger = get_run_logger()
    jobs = [
        "source/from_bq_to_bq.py"
    ]
    for job in jobs:
        spark_submit(job, data_names)
    
    logger.info("--- DONE ---")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--data_name_0', required=True)
    parser.add_argument('--data_name_1', required=True)
    parser.add_argument('--data_name_2', required=True)

    args = parser.parse_args()

    data_names = [args.data_name_0, args.data_name_1, args.data_name_2]
    from_bq_to_bq(data_names)

