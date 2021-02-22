# python 3
import requests
import tweepy
from typing import Sequence
import time
import yaml
import re

YAML_KEY="search_tweets_v2"
DESCRIBINGWORDS = "https://describingwords.io/api/descriptors?term="
# Also update recombine_and_mirror below
TEST_QUERY = "anais nin -is:retweet -has:media lang:en"

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
# print(recombine_and_mirror(["girl", "boy", "dragon"]))
def recombine_and_mirror(tweet_keywords: Sequence) -> str:
  pairings = []
  for keyword in tweet_keywords:
    # No need for more than 5 pairs
    if (len(pairings) >= 5):
       break
    # Otherwise every tweet sees this
    if re.match("a|Anais|n|Nin", keyword):
      continue
    time.sleep(.500)  # Otherwise we'll get throttled by the API
    try:
      pairings.append((get_descriptor(keyword), keyword))
    except:
      # If get_descriptor fails, ignore this word and try another
      continue

  new_post = ""
  for pair in pairings:
    new_post += " ".join(pair)
    new_post += "\n"
  return new_post.strip()


"""
Long-lived objects for accessing the Twitter API
"""
def setup_twitter():
  secrets = yaml.load(open(".twitter_keys.yaml"), Loader=yaml.FullLoader)

  auth = tweepy.OAuthHandler(consumer_key=secrets[YAML_KEY]["consumer_key"],
                             consumer_secret=secrets[YAML_KEY]["consumer_secret"])
  auth.set_access_token(secrets[YAML_KEY]["access_token"],
                        secrets[YAML_KEY]["access_token_secret"])

  return tweepy.API(auth, wait_on_rate_limit=True)


#####################################################################
tweeper = setup_twitter()

while True:
  # 2 tweets at most, don't want to overcrowd anyone's feed.
  tweets = tweeper.search(TEST_QUERY, lang="en", result_type="recent", count=2, include_entities=False)
  for tweet in tweets:
    try:
      # Don't want to comment on people's usernames, too close to a personal attack
      stripped_of_usernames = re.sub("@\w+", "", tweet._json["text"])
      keywords = re.findall("[a-zA-Z]{3,}", stripped_of_usernames)
      keywords = set(keywords) # uniques
      new_post = recombine_and_mirror(list(keywords))

      if len(new_post) == 0:
        continue

      new_post = "@{0}\n".format(tweet._json["user"]["screen_name"]) + new_post
      print(new_post)

      tweeper.update_status(new_post, in_reply_to_status_id=tweet._json["id"])

    except Exception as e:
      print(e)

  time.sleep(60*60)   # Wait 1 hour (ratelimit)
