import time
import requests
import json
import pandas as pd
from settings import *


quote_url = f"https://api.twitter.com/2/tweets/{QUOTE_TWEET_ID}/quote_tweets"
rt_url = f"https://api.twitter.com/2/tweets/{QUOTE_TWEET_ID}/retweeted_by"
like_url = f"https://api.twitter.com/2/tweets/{QUOTE_TWEET_ID}/liking_users"

# Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
# expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
quote_query_params = {
    "max_results": MAX_RESULTS,
    "expansions": "author_id,referenced_tweets.id",
    "user.fields": "username",
    "tweet.fields": "entities,created_at,public_metrics"
}

rt_query_params = {
    "max_results": MAX_RESULTS,
    "tweet.fields": "author_id,created_at"
}

like_query_params = {
    "max_results": MAX_RESULTS
}

follow_params = {
    "max_results": 1000,
}


def req(_url, _query_params):
    response = requests.get(_url, params=_query_params, headers=REQUEST_HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"ERROR: {response.text}")


def data_processing(data, rt_users):
    quote_tweets = data["data"]
    user_ids = []
    for tweet in quote_tweets:
        referenced_tweets = tweet["referenced_tweets"]
        # 过滤非quote retweet
        if not "quoted" in [rt["type"] for rt in referenced_tweets]:
            continue
        # entities = tweet["entities"]
        # # 过滤无#tag
        # if entities.get("hashtags") is None:
        #     continue
        # hashtags = entities["hashtags"]
        # hashtags_lower = [tag["tag"].lower() for tag in hashtags]
        # # 过滤#tag不满足
        # if not REQUIRED_TAGS_LOWER.issubset(hashtags_lower):
        #     continue
        # 过滤官方推特
        if tweet["author_id"] in FILTER_USER_ID:
            continue

        # tweet_info = {}
        # tweet_info["user_id"] = tweet["author_id"]
        # tweet_info["tweet_created_at"] = tweet["created_at"]
        # tweet_info["like_count"] = tweet["public_metrics"]["like_count"]
        # tweet_info["quote_retweet_count"] = tweet["public_metrics"]["retweet_count"] + tweet["public_metrics"]["quote_count"]

        user_ids.append(tweet["author_id"])

    users = data["includes"]["users"]
    user_infos = {user["id"]: user["username"] for user in users}
    for user_id in user_ids:
        rt_users[user_id] = user_infos[user_id]
        # tweet_info["user_id"] = tweet_info["user_id"] + "\t"

    bIsContinue = False
    if data["meta"].get("next_token"):
        quote_query_params["pagination_token"] = data["meta"]["next_token"]
        bIsContinue = True

    return (bIsContinue, )


def data_rt_processing(data, rt_users, _type="rwtweet"):
    if data.get("data") is None:
        return (False, )
    retweets = data["data"]
    for retweet in retweets:
        rt_users[retweet["id"]] = retweet["username"]

    bIsContinue = False
    if data["meta"].get("next_token"):
        if _type == "rwtweet":
            rt_query_params["pagination_token"] = data["meta"]["next_token"]
        elif _type == "like":
            like_query_params["pagination_token"] = data["meta"]["next_token"]

        bIsContinue = True

    return (bIsContinue, )


def get_user_following(user_id, user_followings):
    time.sleep(5)
    url = f"https://api.twitter.com/2/users/{user_id}/following"
    response = requests.get(url, params=follow_params, headers=REQUEST_HEADERS)
    if response.status_code != 200:
        print(f"ERROR: {response.text}")
        return False

    result_json = response.json()
    if result_json.get("data"):
        user_followings.extend([data["id"] for data in result_json["data"]])
    else:
        time.sleep(900)

    if result_json["meta"].get("next_token"):
        follow_params["pagination_token"] = result_json["meta"]["next_token"]
        get_user_following(user_id, user_followings)


def data_persistence(data, filename):
    if not data:
        raise "No data can be persisted"

    columns_names = list(data[0].keys())
    # rows = [list(info.values()) for info in data]
    dataFrame_data = {}
    for column_name in columns_names:
        dataFrame_data[column_name] = [info.get(column_name) for info in data]

    dataFrame = pd.DataFrame(dataFrame_data)
    dataFrame.to_csv(filename, index=False, encoding='utf_8_sig')


def main():
    rt_users = {}
    # tweet_infos = []

    # quote tweet
    data = req(quote_url, quote_query_params)
    bIsContinue, = data_processing(data, rt_users)
    print(f"isContinue: {bIsContinue}")
    print(f"rt_users len: {len(rt_users)}")

    while bIsContinue is True:
        time.sleep(5)
        data = req(quote_url, quote_query_params)
        bIsContinue, = data_processing(data, rt_users)
        print(f"isContinue: {bIsContinue}")
        print(f"rt_users len: {len(rt_users)}")

    # retweet
    data = req(rt_url, rt_query_params)
    bIsContinue, = data_rt_processing(data, rt_users)
    print(f"isContinue: {bIsContinue}")
    print(f"rt_users len: {len(rt_users)}")

    while bIsContinue is True:
        time.sleep(5)
        data = req(rt_url, rt_query_params)
        bIsContinue, = data_rt_processing(data, rt_users)
        print(f"isContinue: {bIsContinue}")
        print(f"rt_users len: {len(rt_users)}")

    # like
    like_users = {}
    data = req(like_url, like_query_params)
    bIsContinue, = data_rt_processing(data, like_users, "like")
    print(f"isContinue: {bIsContinue}")
    print(f"like_users len: {len(like_users)}")

    while bIsContinue is True:
        time.sleep(5)
        data = req(like_url, like_query_params)
        bIsContinue, = data_rt_processing(data, like_users, "like")
        print(f"isContinue: {bIsContinue}")
        print(f"like_users len: {len(like_users)}")

    rt_and_like_users = rt_users.items() & like_users.items()
    print(f"Retweeted and liked by {len(rt_and_like_users)} users.")

    json.dump(dict(rt_and_like_users), open('rt_and_like_users.json', 'w', encoding='utf-8'), ensure_ascii=False)

    # sorted_datas = sorted(all_datas, key=lambda x: x["like_count"], reverse=True)
    # top10_datas = []
    # for data in sorted_datas:
    #     followings = []
    #     get_user_following(user_id=data["user_id"], user_followings=followings)
    #     isFollow = set(FILTER_USER_ID).issubset(followings)
    #     if isFollow:
    #         data["isFollowed"] = 1
    #         data["user_id"] = data["user_id"] + "\t"
    #         top10_datas.append(data)
    #     else:
    #         continue
    #     if len(top10_datas) >= 10:
    #         break


    # filename = f"twitter_active_top10_list.csv"
    # data_persistence(top10_datas, filename)
if __name__ == "__main__":
    main()
