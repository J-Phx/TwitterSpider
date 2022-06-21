import json
import time
import requests
import os
from settings import *


follow_params = {
    "max_results": 1000,
}


def getFollowers(_url, _followers):
    response = requests.get(_url, params=follow_params, headers=REQUEST_HEADERS)
    if response.status_code != 200:
        print(f"ERROR: {response.text}")
        time.sleep(300)
        getFollowers(_url, _followers)

    result_json = response.json()
    if result_json.get("data"):
        for user in result_json["data"]:
            _followers[user["id"]] = user["username"]
    else:
        print("Can't find data")
        return

    print(f"The number of fans has been captured <{len(_followers)}>.")
    time.sleep(120)
    if result_json["meta"].get("next_token"):
        follow_params["pagination_token"] = result_json["meta"]["next_token"]
        getFollowers(_url, _followers)


if __name__ == "__main__":
    output_file_path = os.path.dirname(__file__)

    for user_id in REQOIRED_FOLLOW_ID.keys():
        followers_data = {}
        url = f"https://api.twitter.com/2/users/{user_id}/followers"
        getFollowers(url, followers_data)

        print("Ready to write files...")
        # write
        json.dump(followers_data,
                  open(
                      os.path.join(output_file_path, f'{REQOIRED_FOLLOW_ID[user_id]}_followers.json'),
                      'w', encoding='utf-8'),
                  ensure_ascii=False)
        time.sleep(600)
