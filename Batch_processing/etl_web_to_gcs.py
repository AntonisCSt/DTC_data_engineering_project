from pathlib import Path
import pandas as pd
from youtube_watcher import main as youtube_watcher

from prefect import flow,task
from prefect_gcp.cloud_storage import GcsBucket

@task(log_prints=True,retries=3)
def fetch() -> pd.DataFrame:
    """Read youtube data from web into pandas DataFrame"""

    #run youtube_watcher and get the dataframe
    df = youtube_watcher()
    
    return df

@task(log_prints=True,retries=3)
def clean(df: pd.DataFrame) -> pd.DataFrame:
    """fix dtype issues"""

    df['publishedAt']  = pd.to_datetime(df['publishedAt'])
    df['channelTitle'] = df['channelTitle'].astype(str)

    print(df.head(2))
    print(f"columns: {df.dtypes}")
    print(f"number of rows: {len(df)}")

    return df

@task(log_prints=True)
def write_local(df: pd.DataFrame, dataset_file: str) -> Path:
    """write locally data"""
    path = Path(f"data/{dataset_file}.parquet")
    df.to_parquet(path, compression="gzip")
    return path

@task(log_prints=True)
def write_gcs(path: Path) -> None:
    """Upload file to Gcs"""

    gcp_cloud_storage_bucket_block = GcsBucket.load("zoom-gcs")
    gcp_cloud_storage_bucket_block.upload_from_path(
        from_path=f"{path}",
        to_path=path
    )
    return


@flow(name=" ETL-TO-GCS-BUCKET")
def etl_web_to_gcs() -> None:
    """the main ETL function"""


    df = fetch()
    df_clean = clean(df)
    dataset_file = 'DTC_DataEngineering_playlist_snapshot'
    path = write_local(df_clean,dataset_file)
    write_gcs(path)
if __name__ == '__main__':
    etl_web_to_gcs()