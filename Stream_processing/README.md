YOUTUBE WATCHER:

Thanks to @Kris Jenkins for this amazing tutorial: https://www.youtube.com/watch?v=jItIQ-UvFI4&t=0s


1) Description

2) Flow of work

3) Instructions

3.1) Requirements


To run this script you will have to use your own config.py:
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
3.2) Set-up
	# kafka instalation

`pip install confluent_kafka==2.1.0`
`pip install fastavro==1.7.3`
3.3) Queries for KSQL

3.4) Steps to take

4) Dashboard