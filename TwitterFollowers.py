import json
import time
import requests
import os
from settings import *


follow_params = {
    "max_results": 1000,
}


def pullRequest(_url):
    response = requests.get(_url, params=follow_params, headers=REQUEST_HEADERS)
    processResponse(response)


def processResponse(response):
    url = response.request.url
    if response.status_code != 200:
        print(f"ERROR: {response.text}")
        time.sleep(300)
        pullRequest(url)

    result_json = response.json()
    if result_json.get("data"):
        for user in result_json["data"]:
            followers_data[user["id"]] = user["username"]
    else:
        print("Over")
        return

    print(f"The number of fans has been captured <{len(followers_data)}>.")
    time.sleep(120)
    if result_json["meta"].get("next_token"):
        follow_params["pagination_token"] = result_json["meta"]["next_token"]
        pullRequest(url)


if __name__ == "__main__":
    output_file_path = os.path.dirname(__file__)

    for user_id in REQOIRED_FOLLOW_ID.keys():
        followers_data = {}
        url = f"https://api.twitter.com/2/users/{user_id}/followers"
        pullRequest(url)

        print("Ready to write files...")
        # write
        json.dump(followers_data,
                  open(
                      os.path.join(output_file_path, f'{REQOIRED_FOLLOW_ID[user_id]}_followers.json'),
                      'w', encoding='utf-8'),
                  ensure_ascii=False)
        time.sleep(600)
