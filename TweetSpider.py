# import json
import time
import datetime
import requests
import pandas as pd
from settings import *


def get_userInfo(username):
    response = requests.get(f'https://api.twitter.com/2/users/by/username/{username}', headers=REQUEST_HEADERS)
    if response.status_code == 200:
        result = response.json()
        return result["data"].get("id")


def get_timeline(userId, untilId=None):

    if not untilId:
        params = (
            ('max_results', MAX_RESULTS),
            ('tweet.fields', 'created_at,public_metrics,referenced_tweets'),
        )
    else:
        params = (
            ('max_results', MAX_RESULTS),
            ('tweet.fields', 'created_at,public_metrics,referenced_tweets'),
            ('until_id', untilId),
        )

    url = f"https://api.twitter.com/2/users/{userId}/tweets"
    response = requests.get(url, headers=REQUEST_HEADERS, params=params)
    if response.status_code == 200:
        return response.json()


def data_processing(result_json, containers):
    if not result_json:
        raise "Failed to get tweet info"
    data = result_json["data"]
    for info in data:
        tweetInfo = {}
        tweetInfo["created_at"] = transfer_datetime(info["created_at"])
        tweetInfo["text"] = info["text"]
        if info.get("referenced_tweets"):
            referenced_tweets = ",".join([i["type"] for i in info["referenced_tweets"]])
        else:
            referenced_tweets = "original"
        tweetInfo["referenced_tweets"] = referenced_tweets
        tweetInfo["reply_count"] = info["public_metrics"]["reply_count"]
        tweetInfo["retweet_count"] = info["public_metrics"]["retweet_count"]
        tweetInfo["quote_count"] = info["public_metrics"]["quote_count"]
        tweetInfo["like_count"] = info["public_metrics"]["like_count"]
        
        containers.append(tweetInfo)
    
    result_count = result_json["meta"]["result_count"]
    bIsContinue = False
    if result_count >= MAX_RESULTS:
        until_id = result_json["meta"]["oldest_id"]
        bIsContinue = True
        return (bIsContinue, until_id, containers)
    else:
        return (bIsContinue, None, containers)
        

def transfer_datetime(utc):
    UTC_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
    utc_time = datetime.datetime.strptime(utc, UTC_FORMAT)
    local_time = utc_time + datetime.timedelta(hours=8)
    local_date_str = datetime.datetime.strftime(local_time ,'%Y-%m-%d %H:%M:%S')
    return local_date_str


def data_persistence(data, filename):
    if not data:
        raise "No data can be persisted"
    
    columns_names = list(data[0].keys())
    # rows = [list(info.values()) for info in data]
    dataFrame_data = {}
    for column_name in columns_names:
        dataFrame_data[column_name] = [info.get(column_name) for info in data]
    
    dataFrame = pd.DataFrame(dataFrame_data)
    dataFrame.to_csv(filename, index=False, encoding='utf_8_sig', date_format="%Y-%m-%d %H:%M:%S")
    # with open(filename, "w", encoding='utf-8') as csvfile:
    #     writer = csv.writer(csvfile)
    #     writer.writerow(columns_names)
    #     writer.writerows(rows)


def main():
    for username in TWITTER_TARGET:
        userId = get_userInfo(username)
        if not userId:
            raise "Failed to get user id"
        containers = []
        result_json = get_timeline(userId)
        (isContinue, until_id, containers) = data_processing(result_json, containers)
        print(f"isContinue: {isContinue}, until_id: {until_id}, containers_len: {len(containers)}")
        while isContinue is True:
            time.sleep(2)
            result_json = get_timeline(userId, untilId=until_id)
            (isContinue, until_id, containers) = data_processing(result_json, containers)
            print(f"while --- isContinue: {isContinue}, until_id: {until_id}, containers_len: {len(containers)}")
        
        filename = f"{username}.csv"
        data_persistence(containers, filename)

if __name__ == "__main__":
    main()

    # filename = f"demo.csv"
    # result_json = json.load(open("D:\Code\Test\TweetSpider\demo.json", encoding='utf-8'))
    # containers = []
    # data = result_json["data"]
    # for info in data:
    #     tweetInfo = {}
    #     tweetInfo["created_at"] = transfer_datetime(info["created_at"])
    #     tweetInfo["text"] = info["text"]
    #     if info.get("referenced_tweets"):
    #         referenced_tweets = ",".join([i["type"] for i in info["referenced_tweets"]])
    #     else:
    #         referenced_tweets = "Original"
    #     tweetInfo["referenced_tweets"] = referenced_tweets
    #     tweetInfo["reply_count"] = info["public_metrics"]["reply_count"]
    #     tweetInfo["retweet_count"] = info["public_metrics"]["retweet_count"]
    #     tweetInfo["quote_count"] = info["public_metrics"]["quote_count"]
    #     tweetInfo["like_count"] = info["public_metrics"]["like_count"]
        
    #     containers.append(tweetInfo)

    # data_persistence(containers, filename)

