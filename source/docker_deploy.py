
from prefect import flow, task, get_run_logger
from prefect_gcp.cloud_storage import GcsBucket, GcpCredentials
from prefect.deployments import Deployment
from typing import List
import subprocess
from from_web_to_gcs import from_web_to_gcs
from from_gcs_to_bq import from_gcs_to_bq
from spark_job import from_bq_to_bq
from info import healthcheck


deployments: List[Deployment] = [
    Deployment.build_from_flow(
        flow=from_web_to_gcs,
        name="web_to_gcs_from_py",
        parameters={
            "urls": ["https://cdn.rebrickable.com/media/downloads/inventory_sets.csv.gz?1682147607.450634",
                    "https://cdn.rebrickable.com/media/downloads/sets.csv.gz?1682147600.4386284",
                    "https://cdn.rebrickable.com/media/downloads/themes.csv.gz?1683011566.062824"],
            "data_names": ["inventory_sets","sets","themes"]
        },
    ),
    Deployment.build_from_flow(
        flow=from_gcs_to_bq,
        name="gcs_to_bg_from_py",
        parameters={"data_names": ["inventory_sets", "sets", "themes"]},
    ),
    Deployment.build_from_flow(
        flow=from_bq_to_bq,
        name="from_bq_to_bq_from_py",
    ),
    # Deployment.build_from_flow(
    #     flow=healthcheck,
    #     name="healthcheck_from_py",
    # ),
]


if __name__ == "__main__":
    for deployment in deployments:
        deployment.apply()