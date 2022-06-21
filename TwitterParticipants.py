import time
import requests
import pandas as pd
from settings import *


url = f"https://api.twitter.com/2/tweets/{QUOTE_TWEET_ID}/quote_tweets"

# Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
# expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
query_params = {
    "max_results": MAX_RESULTS,
    "tweet.fields": "author_id,entities,created_at,referenced_tweets"
}
query_infos = [{
    "type": "quote_tweet",
    "url": f"https://api.twitter.com/2/tweets/{QUOTE_TWEET_ID}/quote_tweets",
    "query_params": {
        "max_results": MAX_RESULTS,
        "tweet.fields": "author_id,entities,created_at,referenced_tweets"
    }
},
    {
    "type": "retweet",
    "url": f"https://api.twitter.com/2/tweets/{QUOTE_TWEET_ID}/retweeted_by",
    "query_params": {
        "max_results": MAX_RESULTS,
        "tweet.fields": "author_id"
    }
},
    {
    "type": "like",
    "url": f"https://api.twitter.com/2/tweets/{QUOTE_TWEET_ID}/liking_users",
    "query_params": None
}]


def get_quote_tweets(url, query_params=None):
    response = requests.get(url, params=query_params, headers=REQUEST_HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"ERROR: {response.text}")


def data_processing(data, t):
    global quote_tweet_users, rt_users, like_uesrs, brewery_users, medieval_users

    quote_tweets = data["data"]
    tweet_infos = []
    for tweet in quote_tweets:
        referenced_tweets = tweet["referenced_tweets"]
        # 过滤非quote retweet
        if not "quoted" in [rt["type"] for rt in referenced_tweets]:
            continue
        entities = tweet["entities"]
        # 过滤无#tag
        if entities.get("hashtags") is None:
            continue
        hashtags = entities["hashtags"]
        hashtags_lower = [tag["tag"].lower() for tag in hashtags]
        # 过滤#tag不满足
        if not REQUIRED_TAGS_LOWER.issubset(hashtags_lower):
            continue
        # 过滤官方推特
        if tweet["author_id"] in FILTER_USER_ID:
            continue

        tweet_info = {}
        tweet_info["user_id"] = tweet["author_id"]
        tweet_info["tweet_created_at"] = tweet["created_at"]
        tweet_info["like_count"] = tweet["public_metrics"]["like_count"]
        tweet_info["quote_retweet_count"] = tweet["public_metrics"]["retweet_count"] + tweet["public_metrics"]["quote_count"]

        tweet_infos.append(tweet_info)

    users = data["includes"]["users"]
    user_infos = {user["id"]: user["username"] for user in users}
    for tweet_info in tweet_infos:
        tweet_info["user_username"] = user_infos[tweet_info["user_id"]]
        # tweet_info["user_id"] = tweet_info["user_id"] + "\t"

    bIsContinue = False
    if data["meta"].get("next_token"):
        query_params["pagination_token"] = data["meta"]["next_token"]
        bIsContinue = True

    return (bIsContinue, tweet_infos)


def main():
    quote_tweet_users = []
    rt_users = []
    like_uesrs = []
    brewery_users = []
    medieval_users = []
    # tweet_infos = []

    data = get_quote_tweets()
    bIsContinue, tweet_infos = data_processing(data)
    print(f"isContinue: {bIsContinue}, tweet_infos_len: {len(tweet_infos)}")
    all_datas.extend(tweet_infos)
    print(f"all_datas len: {len(all_datas)}")

    while bIsContinue is True:
        time.sleep(2)
        data = get_quote_tweets()
        bIsContinue, tweet_infos = data_processing(data)
        print(f"isContinue: {bIsContinue}, tweet_infos_len: {len(tweet_infos)}")
        all_datas.extend(tweet_infos)
        print(f"all_datas len: {len(all_datas)}")

    sorted_datas = sorted(all_datas, key=lambda x: x["like_count"], reverse=True)
    top10_datas = []
    for data in sorted_datas:
        followings = []
        get_user_following(user_id=data["user_id"], user_followings=followings)
        isFollow = set(FILTER_USER_ID).issubset(followings)
        if isFollow:
            data["isFollowed"] = 1
            data["user_id"] = data["user_id"] + "\t"
            top10_datas.append(data)
        else:
            continue
        if len(top10_datas) >= 10:
            break

    filename = f"twitter_active_top10_list.csv"
    data_persistence(top10_datas, filename)


if __name__ == "__main__":
    main()
