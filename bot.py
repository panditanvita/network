# python 3
import requests
import tweepy
from typing import Sequence
import time
import yaml
import re
from searchtweets import collect_results, load_credentials, gen_request_parameters

YAML_KEY="search_tweets_v2"
DESCRIBINGWORDS = "https://describingwords.io/api/descriptors?term="
TWITTER_QUERY = "#NetworkedMirrorBot -is:retweet -has:media"
TEST_QUERY = "madame bovary -is:retweet -has:media lang:en"

""" Get a JSON object listing the descriptors for a term

Other option for sortType is "frequency"
Function will raise an error if `term` is not a valid noun
in the DescribingWords corpus, or the site rejects us for any
reason.
"""
def get_descriptor(term: str, sortType: str = "unique"):
  r = requests.get(DESCRIBINGWORDS + term + "&sortType=" + sortType)
  return r.json()[0]["word"]

# Example query:
# print(get_pairings(["girl", "boy", "dragon"]))
def get_pairings(tweet_keywords: Sequence):
  pairings = []
  for keyword in tweet_keywords:
    # No need for more than 5 pairs
    if (len(pairings) >= 5):
       break
    # Otherwise every tweet sees this
    if re.match("m|Madame|B|bovary", keyword):
      continue
    time.sleep(.500)  # Otherwise we'll get throttled by the API
    try:
      pairings.append((get_descriptor(keyword), keyword))
    except:
      # If get_descriptor fails, ignore this word and try another
      continue
  return pairings

def pairings_to_tweet(pairings):
  new_post = ""
  for pair in pairings:
    new_post += " ".join(pair)
    new_post += "\n"
  return new_post


"""
Long-lived objects for accessing the Twitter API
"""
def setup_twitter():
  secrets = yaml.load(open(".twitter_keys.yaml"), Loader=yaml.FullLoader)

  auth = tweepy.OAuthHandler(consumer_key=secrets[YAML_KEY]["consumer_key"],
                             consumer_secret=secrets[YAML_KEY]["consumer_secret"])
  auth.set_access_token(secrets[YAML_KEY]["access_token"],
                        secrets[YAML_KEY]["access_token_secret"])

  # Start watching for tweets that mention the bot.
  search_args = load_credentials(".twitter_keys.yaml", yaml_key=YAML_KEY, env_overwrite=False)
  query = gen_request_parameters(TEST_QUERY, results_per_call=10)

  return search_args, query, tweepy.API(auth, wait_on_rate_limit=True)


#####################################################################
search_args, query, tweeper = setup_twitter()

while True:
  tweets = collect_results(query, max_tweets=10, result_stream_args=search_args)

  for tweet in tweets:
    # We are at the end of the tweets
    if "id" not in tweet.keys():
      break

    try:
      keywords = re.findall("[a-zA-Z]{3,}", tweet["text"])
      keywords = set(keywords) # uniques
      pairings = get_pairings(list(keywords))

      if len(pairings) == 0:
        continue

      new_post = pairings_to_tweet(pairings)
      print(new_post)

      tweeper.update_status(new_post)
    except Exception as e:
      print(e)

  time.sleep(60*60)   # Wait 60 minutes between spurts (ratelimit)
