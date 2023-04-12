#code is following Kris's tutorial: https://www.youtube.com/watch?v=jItIQ-UvFI4&t=1357s
#props to him for his amazing tutorial.
import random
import logging
import requests
import pandas as pd
import time
from pprint import pformat
from DTC_data_engineering_project.Batch_processing.batch_config import config
import json

from datetime import datetime

def fetch_playlist_items_page(google_api_key,youtube_playlist_id, page_token=None):

    response = requests.get("https://www.googleapis.com/youtube/v3/playlistItems", params={
        "key": google_api_key, 
        "playlistId": youtube_playlist_id,
        "part": "snippet,contentDetails,status,id",
        "pageToken":page_token,
        })
    
    payload = json.loads(response.text)
    logging.debug("GOT %s", pformat(payload))
    print('#########################')
   
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
def get_video_info_list(video:dict)-> dict:
    """
    Summarizes information about a given video dict.

    Args:
        video (dict): A dictionary containing information about the video.

    Returns:
        list: A listcontaining selected info of the video.
    """
    # We use .get to handle cases where a field we want is missing from the JSON.
    row = [
        video['id'], 
        int(video['statistics']['commentCount']), 
        int(video['statistics']['favoriteCount']), 
        int(video['statistics']['likeCount']), 
        int(video['statistics']['viewCount']),
        pd.to_datetime(video['snippet']['publishedAt']),
        video['snippet']['channelTitle']
    ]

    return row


def on_delivery(err,record):
    pass

def main():
    logging.info("START")

    google_api_key = config["google_api_key"]
    youtube_playlist_id = config["youtube_playlist_id"]


    #initiate video's stats dictionary:
    data_videos = []
    playlist_first_page = fetch_playlist_items_page(google_api_key,youtube_playlist_id, page_token=None)


    playlist_name = playlist_first_page["items"][0]["snippet"]["title"]

    #start looping in each video of playlist
    for video_item in fetch_playlist_items(google_api_key,youtube_playlist_id):
        video_id = video_item["contentDetails"]["videoId"]

        for video in fetch_videos(google_api_key, video_id):
            logging.info("GOT %s", video_id)

            video_row = get_video_info_list(video)
            data_videos.append(video_row)
    
    # create the dataframe from the data list and add column names
    df = pd.DataFrame(data_videos, columns=['videoid', 'commentCount', 'favoriteCount', 'likeCount', 'viewCount', 'publishedAt', 'channelTitle'])

    logging.info("GOT %s", df)
  
    #sent messages to kafka
    

if __name__== "__main__":
    logging.basicConfig(level=logging.INFO)
    main()  
    #sys.exit(main())