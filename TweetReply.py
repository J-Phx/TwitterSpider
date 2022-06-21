import tweepy
from settings import *

# bear_token = 'XXXXXX'
client = tweepy.Client(bearer_token=BEARER_TOKEN)
# auth = tweepy.OAuth2AppHandler("27kBdl4CccojC43MTMSfXEafm", "czX4kDIv4WxJLiRABnNugshX1S6SjeThmTEhfqCqBovafHnMjg")
# api = tweepy.API(auth)
tweets_fields_list = ['created_at', 'id', 'text']
expansions_list = ['author_id']
client.search_all_tweets(query="conversation_id:1536679023254056960 -from:1474222235279925248",
                         tweet_fields=tweets_fields_list, expansions=expansions_list, max_results=500)

for response in tweepy.Paginator(
        client.search_all_tweets, query="conversation_id:1536679023254056960 -from:1474222235279925248",
        tweet_fields=tweets_fields_list, expansions=expansions_list, max_results=500):

    print("一共有：" + str(len(response.data)) + " 条回复")
    for tweet in response.data:
        print("-------------分割线----------------")
        print(tweet.author_id, tweet.id, tweet.created_at, tweet.text)
