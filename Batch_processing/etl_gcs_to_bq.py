from pathlib import Path
import pandas as pd

from prefect import flow,task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials

@task(log_prints=True,retries=2)
def extract_from_gcs() -> Path:
    """Download trip data from GCS"""

    gcs_path = f"data/DTC_DataEngineering_playlist_snapshot.parquet"
    gcs_block = GcsBucket.load("zoom-gcs")
    gcs_block.get_directory(from_path=gcs_path, local_path=f"./data/")
    print(f"path: ./data/{gcs_path}")

    return Path(f"./data/{gcs_path}")

@task(log_prints=True)
def transform(path: Path) -> pd.DataFrame:
    """Data cleaning for bq"""
    print(path)
    df = pd.read_parquet(path)
    print(f"number of rows: {len(df)}")
    
    #df[''].fillna(df[''].mean(),inplace=True)
  
    return df

@task(log_prints=True,retries=2)
def write_bq(df: pd.DataFrame) -> None:
    """Write DataFrame to BigQuery"""
    gcp_credentials_block = GcpCredentials.load("gcp-credentials")
    df.to_gbq(destination_table="youtube_playlist.youtube_playlist_info",
        project_id="my-rides-antonis",
        credentials= gcp_credentials_block.get_credentials_from_service_account(),
        chunksize=500000,
        if_exists="replace"
    )
    return

@flow(name="ETL-TO-BIG-QUERY")
def etl_gcs_to_bq() -> None:
    """Main ETL flow to load data into Big Query"""
    
    path = extract_from_gcs()
    df = transform(path)
    write_bq(df)
    



if __name__ == '__main__':

    etl_gcs_to_bq()
