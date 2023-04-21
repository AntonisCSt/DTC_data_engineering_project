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

* Python 3.9 or higher version 

* Google cloud account with a project and a file (json usually) with the granted IAM roles (bigquery and gcp)

* Terraform Installation

* DBT cloud account

* Confluent Kafka cloud account

### Instalation

* Python:

`pip install requirements.txt`

* Batch process:
    - batch config file for youtube API: create a 
    
    


* Stream process:
    - streaming and 

* streaming and batch config
* gcp account credentials
* prefect gcp storage and google credentials blocks active






### 


### Improvements

* Possition column fix from youtube API
* Save playlist ids in a config
* Playlist names create a folder automatically