from pathlib import Path
import pandas as pd

from prefect import flow,task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials

@task(log_prints=True,retries=2)
def extract_from_gcs(playlist_name:str) -> Path:
    """Download trip data from GCS"""

    gcs_path = f"data/DTC_{playlist_name}_playlist_snapshot.parquet"
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
def write_bq(df: pd.DataFrame,playlist_name:str) -> None:
    """Write DataFrame to BigQuery"""
    gcp_credentials_block = GcpCredentials.load("gcp-credentials")
    df.to_gbq(destination_table=f"youtube_playlist.youtube_playlist_{playlist_name}_info",
        project_id="my-rides-antonis",
        credentials= gcp_credentials_block.get_credentials_from_service_account(),
        chunksize=500000,
        if_exists="replace"
    )
    return

@flow(name="ETL-TO-BIG-QUERY")
def etl_gcs_to_bq(playlist_name:str) -> None:
    """Main ETL flow to load data into Big Query"""
    
    path = extract_from_gcs(playlist_name)
    df = transform(path)
    write_bq(df,playlist_name)
    

@flow(name="Parent-ETL-TO-BIG-QUERY")
def etl_parent_gcs_to_bq(playlist_name_list:list[str]) -> None:
    """Parent of ETL flow to load data into Big Query"""
    
    #for every playlist create a different table
    for playlist_name in playlist_name_list:
        etl_gcs_to_bq(playlist_name)

if __name__ == '__main__':
    playlist_name_list = ['Data Engineering Zoomcamp 2023','Machine Learning Zoomcamp 2022','MLOps Zoomcamp 2022']
    etl_parent_gcs_to_bq(playlist_name_list)
