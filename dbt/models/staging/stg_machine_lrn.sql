{{ config(materialized='view') }}


select 

cast(video_name as string) as video_name,
cast(videoid as string) as videoid,
cast(playlist_possition as integer) as playlist_possition,
cast(commentCount as integer) as commentCount,
cast(favoriteCount as integer) as favoriteCount,
cast(likeCount as integer) as likeCount,
cast(viewCount as integer) as viewCount,
cast(publishedAt as timestamp) as publishedAt,
cast(channelTitle as string) as channelTitle,
cast(description as string) as description,
cast(playlist_name as string) as playlist_name

 from {{ source('staging','youtube_playlist_Machine Learning Zoomcamp 2022_info') }}