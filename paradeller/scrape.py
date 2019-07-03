import json
import os
import sys

import tweepy
from tqdm import tqdm, trange

from paradeller.helper import load_archive, update_archive, fp

from paradeller.dataprep import tokenize

from paradeller.keys import (
    access_token,
    accss_token_secret,
    consumer_key,
    consumer_secret,
)

# init tweepy API
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, accss_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)


def get_tweets():
    """
    Search twitter for tweets matching basic criteria
    (not retweets, no links, no media)

    Returns
    -------
    list
        Curated list tweepy status object
    """
    query = "-filter:retweets -filter:links -filter:media"
    tweets = api.search(q=query, lang="en", count=100, include_entities=False)
    return [t for t in tweets if is_good(t.text)]


def is_good(text) -> bool:
    """
    Returns True of text looks useable, False otherwise.
    """

    # word count too low or too high?
    tweet_len = len(tokenize(text))
    if (tweet_len < 3) or (tweet_len > 10):
        return False

    # has blacklisted words/symbols?
    blacklist = ["@", "\n"]
    for char in blacklist:
        if char in text:
            return False

    return True


def format_status(status):
    """
    Extract relevant info from Status object

    Returns
    -------
    dict
        Basic status info (id, text, author, time)
    """
    return dict(
        id=status.id,
        text=status.text,
        author=status.author.screen_name,
        time=status.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    )


def main(n=200):
    """
    Scrape twitter using API

    Parameters
    ----------
    n : int
        The number of times to call get_tweets
        Each call gets ~100 tweets
    """

    # load archive JSON file into Python list
    data = load_archive()

    # print message
    pre_len = len(data)
    print(f"\nScraping ~{n*100:,} tweets")
    print("...Loaded archive from file")
    print(f"...Initial archive length: {pre_len:,}")

    # repeatedly get tweets using API, format, add to archive list
    print("\nScraping!")
    for _ in trange(n):
        try:
            statuses = get_tweets()
            tweets = [format_status(s) for s in statuses]
            data.extend(tweets)
        except tweepy.TweepError as e:
            print(e)

    # remove duplicate ids
    d = {}
    for item in data:
        d[item["id"]] = item
    data = list(d.values())

    # save list to file
    update_archive(data)

    # print message
    post_len = len(data)
    size_mb = os.path.getsize(fp) / 1e6
    print("\n...Saved archive to file")
    print(f"...New archive length: {post_len:,}")
    print(f"...Added {post_len - pre_len:,} tweets")
    print(f"...Archive file is now {size_mb:.2f} MB")


if __name__ == "__main__":
    default_n = "200"

    # parse command line arguments
    args_dict = dict(enumerate(sys.argv))
    n = int(args_dict.get(1, default_n))

    # call main
    main(n)
