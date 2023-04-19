from pathlib import Path
import pandas as pd
from youtube_watcher import main as youtube_watcher

from prefect import flow,task
from prefect_gcp.cloud_storage import GcsBucket

@task(log_prints=True,retries=3)
def fetch(playlist_id:str) -> pd.DataFrame:
    """Read youtube data from web into pandas DataFrame"""

    #run youtube_watcher and get the dataframe
    df,playlist_name = youtube_watcher(playlist_id)
    
    return df,playlist_name

@task(log_prints=True,retries=3)
def clean_and_edit(df: pd.DataFrame,playlist_name:str) -> pd.DataFrame:
    """fix dtype issues"""

    df['publishedAt']  = pd.to_datetime(df['publishedAt'])
    df['channelTitle'] = df['channelTitle'].astype(str)
    df['playlist_name'] = playlist_name

    print(df.head(2))
    print(f"columns: {df.dtypes}")
    print(f"number of rows: {len(df)}")
    print(playlist_name)
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

@flow(name="ETL-TO-GCS-BUCKET")
def etl_web_to_gcs(playlist_id:str) -> None:
    """the main ETL function"""

    df,playlist_name = fetch(playlist_id)
    df_clean = clean_and_edit(df,playlist_name)
    dataset_file = f'DTC_{playlist_name}_playlist_snapshot'
    path = write_local(df_clean,dataset_file)
    write_gcs(path)

@flow(name="Parent_ETL-TO-GCS-BUCKET")
def etl_parent_web_to_gcs(playlist_id_list:list[str]) -> None:
    """the proud parent of ETL function"""

    for playlist_id in playlist_id_list:
        etl_web_to_gcs(playlist_id)

if __name__ == '__main__':
    playlist_id_list = ["PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb","PL3MmuxUbc_hIhxl5Ji8t4O6lPAOpHaCLR","PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK"]
    etl_parent_web_to_gcs(playlist_id_list)