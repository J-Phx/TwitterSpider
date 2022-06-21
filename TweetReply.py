import time
import requests
import json
import pandas as pd
from settings import *


search_url = f"https://api.twitter.com/2/tweets/search/all"

# Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
# expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
search_params = {
    "query": f"conversation_id:{SEARCH_TWEET_ID} to:boba_brewery -from:boba_brewery",
    "max_results": 500,
    "expansions": "author_id,entities.mentions.username",
    "user.fields": "username",
    "tweet.fields": "entities,created_at,public_metrics",
    # "end_time":
}

response = requests.get(search_url, params=search_params, headers=REQUEST_HEADERS)
print(response.text)

# {"client_id":"23074266","detail":"When authenticating requests to the Twitter API v2 endpoints, you must use keys and tokens from a Twitter developer App that is attached to a Project. You can create a project via the developer portal.","registration_url":"https://developer.twitter.com/en/docs/projects/overview","title":"Client Forbidden","required_enrollment":"Standard Basic","reason":"client-not-enrolled","type":"https://api.twitter.com/2/problems/client-forbidden"}

# 当前权限不够, 不支持全局搜索
# https://developer.twitter.com/en/docs/twitter-api/getting-started/about-twitter-api#v2-access-leve
