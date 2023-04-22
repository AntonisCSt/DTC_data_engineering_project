# Data Engineering Project: DataTalks Club overview Youtube playlist 

## DataTalksClub Data Engineering Course 2023

## About the project

The projects goal is to show stats regarding youtube playlists. Specifally we choose the playlist of DataTalksClub courses. 
We show daily information through a Batch pipeline and live changes in a Stream pipeline. 
<img src="./images/dtc_eng_project.png" width="100%" height="100%">
**Batch process:** Takes daily general information (video name, description, video publication date, likes, views etc) about the playlist from the youtube API. This is schedule with Prefect. First, it cleans and saves the information in google storage, then it transforms and saves the information/dataset in big query. After prefect, dbt takes the table and peroforms additional (modeled) transformations. Finnaly, Through a dbt deployment enviroment, we it schedule it to daily give the information to Bigquery table that is connected to Locker Studio.

**Stream process:** Takes every minute accumulated information (total views, total comments, total likes) from each playlist from the YouTube API and sends it to Kafka. In Kafka we detect changes in these values through KSQL and append every change in a Bigquery table. The Bigquery table is also connected to Locker Studio.

## Requirements

To run the project you will need:

* Python ~ 3.9 (specifically the project was builded on `Python 3.9.16`)  

* Google cloud account with a project and a file (json usually) with the granted IAM roles (bigquery and gcp)

* Terraform Installation

* DBT cloud account

* Confluent Kafka cloud account

* Patience 

See the next section for more details.

### Instalation and set-up

### Python:

Download and install conda's python version ~ `Python 3.9.16`. Create and enviroment and run `pip install requirements.txt`.

### Batch process:

To run `/Batch_processing/youtube_watcher.py` in stream process you will need a `/Batch_processing/batch_config.py` file. 

The template is the following:
```python
config = {"google_api_key": "[Your google API key]",
    "youtube_playlist_id": "PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb",
```  

* `google_api_key`: [Document on how to get a google api key](https://developers.google.com/maps/documentation/javascript/get-api-key)

* youtube_playlist_id: the playlist id that is in the YouTube playlist we are interested. This one is the Data Engineering zoomcamp 2023. However, in the current version this field is no longer beeing used. So you can keep it the same.

Prefect requires gcp storage and google credentials blocks active. You can follow these tutorials: [Tutorial on how to activate a gcp storage and gcp credential block](https://www.youtube.com/watch?v=W-rMz_2GwqQ&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=21&t=1000s)
[Tutorial on how to edit the scripts to connect to bigquery ](https://www.youtube.com/watch?v=Cx5jt-V5sgE&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=21)

### Stream process:

* streaming and batch config:

To run `/Stream_processing/youtube_watcher.py` in stream process you will need a `/Stream_processing/config.py` file. 

The template is the following:
```python
config = {"google_api_key": "[Your google API]",
    "youtube_playlist_id": "PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb",
    "kafka":{
            "bootstrap.servers":"[Your kafka-bootstrap-server]",
            "security.protocol":"[Your security protocol]",
            "sasl.mechanism": "PLAIN",
            "sasl.username":"[your kafka API username]",
            "sasl.password":"[your kafka API secret]",



    },
    "schema_registry": {
        "url": "[Your registery url]",
        "basic.auth.user.info": "[registery username]/[registery secret]",
    }
```

A full tutorial to fill the config file is in: [How to fill config for stream](https://www.youtube.com/watch?v=jItIQ-UvFI4&t=0s)

* Spoiler alert!:

You will have to create a confulent kafka account https://confluent.cloud/login . There you will need to create a new enviroment and set up a connection with bigquery.


### 


### Improvements

* Possition column fix from youtube API
* Save playlist ids in a config
* Playlist names create a folder automatically