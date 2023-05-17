import argparse
from pathlib import Path
import pandas as pd
from prefect import flow, task, get_run_logger
from prefect_gcp.cloud_storage import GcsBucket



@task(name="Cleaning data", log_prints=True)
def clean(df=pd.DataFrame) -> pd.DataFrame:
    """ Will clean data with pyspark """
    logger = get_run_logger()
    logger.info("Will clean data with pyspark")
    return df

@task(name="Write data to local", log_prints=True)
def write_local(df, df_name) -> Path:
    logger = get_run_logger()
    local_path = f"data/{df_name}"
    df.to_parquet(local_path, compression="gzip")
    return Path(local_path)


@task(name="Write data to GCS", log_prints=True)
def write_gcs(local_path: Path) -> None:
    """ Upload local parquet file to GCP """
    logger = get_run_logger()
    gcs_block = GcsBucket.load("de2023-gcs")
    gcs_block.upload_from_path(
        from_path=local_path,
        to_path=f"project/{local_path.name}"
    )



@flow(name="from_web_to_GCS", log_prints=True)
def from_web_to_gcs(urls, data_names) -> None:
    """ The main ETL function"""
    logger = get_run_logger()
    for i in range(len(urls)):
        url = urls[i]
        data_name = data_names[i]
        df = pd.read_csv(url, compression='gzip')
        local_path = write_local(df, f"{data_name}.parquet")
        write_gcs(local_path)
    
    logger.info("--- DONE ---")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--url_0', required=True)
    parser.add_argument('--url_1', required=True)
    parser.add_argument('--url_2', required=True)

    parser.add_argument('--data_name_0', required=True)
    parser.add_argument('--data_name_1', required=True)
    parser.add_argument('--data_name_2', required=True)

    args = parser.parse_args()

    urls = [args.url_0, args.url_1, args.url_2]
    data_names = [args.data_name_0, args.data_name_1, args.data_name_2]
    from_web_to_gcs(urls, data_names)

