# python 3
import requests
from typing import Sequence
import time
from searchtweets import collect_results, load_credentials, gen_request_parameters

DESCRIBINGWORDS = "https://describingwords.io/api/descriptors?term="
TWITTER_QUERY = "#NetworkedMirrorBot -is:retweet -has:media"
TEST_QUERY = "madame bovary"

""" Get a JSON object listing the descriptors for a term

Other option for sortType is "frequency"
"""
def get_descriptor(term: str, sortType: str = "unique"):
  r = requests.get(DESCRIBINGWORDS + term + "&sortType=" + sortType)
  return r.json()[0]["word"]


def get_pairings(tweet_keywords: Sequence):
  pairings = []
  for keyword in tweet_keywords:
    time.sleep(.500)  # Otherwise we'll get throttled by the API
    pairings.append((get_descriptor(keyword), keyword))
  return pairings

# print(get_pairings(["girl", "boy", "dragon"]))

def run():
  # Start watching for tweets that mention the bot.
  search_args = load_credentials(".twitter_keys.yaml", yaml_key="search_tweets_v2", env_overwrite=False)

  query = gen_request_parameters(TEST_QUERY, results_per_call=10)
  tweets = collect_results(query, max_tweets=10, result_stream_args=search_args)

  for tweet in tweets:
    print(tweet)
    # get nouns for each tweet
    # Call get_pairings and post output(only for tweets that it's not seen before)

run()
