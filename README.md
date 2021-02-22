# network cultures bot

MirrorBot mines an incoming stream of tweets to find concepts (noun words) and cross-references them against adjective-noun phrases culled from an external corpus of printed English literature: everything from Project Gutenberg and then a little more besides (100 GB total).

The bot retweets and @'s the original tweeter. Please comment if you would prefer this bot does not contact you.

It uses the [DescribingWords](https://describingwords.io) API for cross-referencing and the Tweepy API for contacting Twitter.

The bot was created as part of the MIT CMS.614 Network Cultures class assignments.

Usage:
update the TEST_QUERY field in bot.py to match your preferred media content.
update recombine_and_mirror re.match so it doesn't match against very common keywords - it's
nicer to avoid repetitive tweets.

run python3 bot.py


Further ideas:
- automatically switch search queriesi every day. Searching for #NetworkMirrorBot as originally planned is likely to not lead to anything. But we don't want to stay frozen on a single author all the time. 
- delete all tweets older than 2 days with no likes or comments,



