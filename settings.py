from dotenv import dotenv_values

config = dotenv_values(".env")
BEARER_TOKEN = config["BEARER_TOKEN"]

REQUEST_HEADERS = {
    'Authorization': f'Bearer {BEARER_TOKEN}',
}

MAX_RESULTS = 100

TWITTER_TARGET = ["solanium_io", "AvalaunchApp"]


# ################################## ACTIVE SETTINGS##################################
QUOTE_TWEET_ID = "1537359722311200768"

REQUIRED_TAGS = ["BREonMEXC"]
REQUIRED_TAGS_LOWER = set([tag.lower() for tag in REQUIRED_TAGS])

REQOIRED_FOLLOW = ["boba_brewery", "AntmonsOfficial"]
REQOIRED_FOLLOW_ID = {"1499589607133892614": "Antmons", "1474222235279925248": "boba_brewery"}
# REQOIRED_FOLLOW_ID = {"1474222235279925248": "boba_brewery"}
# 978566222282444800 -- MEXC_Global
# 1427160102365106182 -- NeopetsMeta
# 1474659758896463875 -- cyberpopnw
# 1474222235279925248 -- boba_brewery
# 1499589607133892614 -- Antmons
FILTER_USER_ID = ["1499589607133892614", "1474222235279925248"]
