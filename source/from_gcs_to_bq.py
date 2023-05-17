import argparse
import pandas as pd
from io import BytesIO
from pathlib import Path

from prefect_gcp import GcpCredentials
from prefect import flow, task, get_run_logger
from prefect_gcp.cloud_storage import GcsBucket


@task(name="Download data from GCS", log_prints=True)
def extract_from_gcs(input_file) -> Path:
    """ Download trip data from GCS """
    logger = get_run_logger()
    gcs_path = f"project/{input_file}.parquet"
    gcs_block = GcsBucket.load("de2023-gcs")
    file_path = gcs_block.read_path(f"{gcs_path}")
    return file_path


@task(name="Read and transform data", log_prints=True)
def transform(file_path) -> pd.DataFrame:
    """ Data clearning example """
    logger = get_run_logger()
    df = pd.read_parquet(BytesIO(file_path))
    return df

@task(name="Write data to BigQuery", log_prints=True)
def write_bq(df: pd.DataFrame, table_name) -> None:
    """ Write DataFrame to BigQuery """
    logger = get_run_logger()
    # from prefect_gcp import GcpCredentials
    gcp_credentials_block = GcpCredentials.load("van-de2023")

    df.to_gbq(
        destination_table=f"vande2023.{table_name}",
        project_id="vande2023",
        credentials=gcp_credentials_block.get_credentials_from_service_account(),
        # chunksize=500_000,
        if_exists="replace"
    )


@flow(name="from_GCS_to_BQ", log_prints=True)
def from_gcs_to_bq(data_names):
    """ Main ETL flow to load data from GCS into Big Query """
    logger = get_run_logger()
    for i in range(len(data_names)):
        data_name = data_names[i]
        file_path = extract_from_gcs(f"{data_name}")

        clean_df = transform(file_path)
        
        write_bq(clean_df, data_name)
    
    logger.info("--- DONE ---")
 

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--data_name_0', required=True)
    parser.add_argument('--data_name_1', required=True)
    parser.add_argument('--data_name_2', required=True)

    args = parser.parse_args()

    data_names = [args.data_name_0, args.data_name_1, args.data_name_2]
    from_gcs_to_bq(data_names)

