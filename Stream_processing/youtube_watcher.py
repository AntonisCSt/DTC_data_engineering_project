#code is following Kris's tutorial: https://www.youtube.com/watch?v=jItIQ-UvFI4&t=1357s
#props to him for his amazing tutorial.
import random
import logging
import requests
import time
from pprint import pformat
from config import config
import json
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.serialization import StringSerializer
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka import SerializingProducer

from datetime import datetime

def fetch_playlist_items_page(google_api_key,youtube_playlist_id, page_token=None):

    response = requests.get("https://www.googleapis.com/youtube/v3/playlistItems", params={
        "key": google_api_key, 
        "playlistId": youtube_playlist_id,
        "part": "snippet,contentDetails",
        "pageToken":page_token,
        })
    
    payload = json.loads(response.text)
    logging.debug("GOT %s", pformat(payload))

    return payload

def fetch_videos_page(google_api_key,video_id, page_token=None):

    response = requests.get("https://www.googleapis.com/youtube/v3/videos", params={
        "key": google_api_key, 
        "id": video_id,
        "part": "snippet,statistics",
        "pageToken":page_token,
        })
    
    payload = json.loads(response.text)
    logging.debug("GOT %s", pformat(payload))

    return payload

def fetch_playlist_items(google_api_key, youtube_playlist_id, page_token=None):
    #fetch one page
    payload = fetch_playlist_items_page(google_api_key, youtube_playlist_id, page_token)

    #serve up items from that page
    yield from payload["items"]
    
    
    #if there are more pages next
    next_page_token = payload.get("nextPageToken")

    if next_page_token is not None:
        yield from fetch_playlist_items(google_api_key,youtube_playlist_id,next_page_token)
        #carry on from there

def fetch_videos(google_api_key, youtube_playlist_id, page_token=None):
    #fetch one page
    payload = fetch_videos_page(google_api_key, youtube_playlist_id, page_token)

    #serve up items from that page
    yield from payload["items"]
    
    #if there are more pages next
    next_page_token = payload.get("nextPageToken")

    if next_page_token is not None:
        yield from fetch_videos(google_api_key,youtube_playlist_id,next_page_token)
        #carry on from there
def summarize_video(video:dict)-> dict:
    """
    Summarizes information about a given video dict.

    Args:
        video (dict): A dictionary containing information about the video.

    Returns:
        dict: A dictionary containing a summary of the video information.
    """
    # We use .get to handle cases where a field we want is missing from the JSON.
    output_dict = {
        "video_id": video["id"],
        "title": video["snippet"]["title"],
        "views": video["statistics"].get("viewCount",int(0)),
        "likes": video["statistics"].get("likeCount",int(0)),
        "comments_count":video["statistics"].get("commentCount",int(0)),

    }

    return output_dict

def summarize_videos_stats(details_dict:dict)-> dict:
    likes_total = sum(int(details['likes']) for details in details_dict.values())
    views_total = sum(int(details['views']) for details in details_dict.values())
    comments_total = sum(int(details['comments_count']) for details in details_dict.values())
    total_videos = len(details_dict)

    now = datetime.now()
    timestamp = int(datetime.timestamp(now))
    random_number = random.randint(0, 9999)
    message_id = f"{timestamp}_{random_number}"

    return {'message_id': message_id,'total_videos': total_videos,'total_likes': likes_total, 'total_views': views_total, 'total_comments': comments_total}

def on_delivery(err,record):
    pass

def main(playlist_id:str):
    logging.info("START")
    schema_registry_client = SchemaRegistryClient(config["schema_registry"])
    youtube_videos_value_schema = schema_registry_client.get_latest_version("youtube_dtc_playlist_stats-value")

    kafka_config = config["kafka"].copy()
    kafka_config.update({
        "key.serializer": StringSerializer(),
        "value.serializer": AvroSerializer(
            schema_registry_client,
            youtube_videos_value_schema.schema.schema_str,
        ),
    })
    producer = SerializingProducer(kafka_config)

    google_api_key = config["google_api_key"]
    youtube_playlist_id = playlist_id
    #config["youtube_playlist_id"]


    #initiate video's stats dictionary:
    dict_videos = {}
    playlist_first_page = fetch_playlist_items_page(google_api_key,youtube_playlist_id, page_token=None)


    playlist_name = playlist_first_page["items"][0]["snippet"]["title"]
    logging.info("GOT %s", playlist_name)
    #start looping in each video of playlist
    logging.info('generating data...')
    for video_item in fetch_playlist_items(google_api_key,youtube_playlist_id):
        video_id = video_item["contentDetails"]["videoId"]

        for video in fetch_videos(google_api_key, video_id):
            logging.debug("GOT %s", video_id)

            dict_videos[video_id] = summarize_video(video)
            
    results_dict = summarize_videos_stats(dict_videos)
    logging.info("GOT %s", pformat(results_dict))
  
    #sent messages to kafka
    producer.produce(
        topic = 'youtube_dtc_playlist_stats',
        key = results_dict["message_id"],
        value = {
            "PLAYLIST_NAME": str(playlist_name),
            "TOTAL_VIDEOS": results_dict["total_videos"],
            "TOTAL_VIEWS": results_dict["total_views"],
            "TOTAL_LIKES": results_dict["total_likes"],
            "TOTAL_COMMENTS": results_dict["total_comments"],   
            },
        on_delivery = on_delivery,
    
    )

    producer.flush()

if __name__== "__main__":
    while True:
        for playlist_id in ["PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb","PL3MmuxUbc_hIhxl5Ji8t4O6lPAOpHaCLR","PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK"]:
            logging.basicConfig(level=logging.INFO)
            main(playlist_id)
        time.sleep(60)
    #sys.exit(main())