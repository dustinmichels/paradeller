import json

import tweepy
from tqdm import tqdm, trange

from paradeller.helper import load_archive, update_archive
from paradeller.keys import (
    access_token,
    accss_token_secret,
    consumer_key,
    consumer_secret,
)


def get_tweets(api):
    query = "-filter:retweets -filter:links -filter:media"
    tweets = api.search(q=query, lang="en", count=100, include_entities=False)
    return [t for t in tweets if is_good(t.text)]


def is_good(t):
    """Filter out tweets that won't work well"""
    # has low word count?
    tweet_len = len(t.split())
    if (tweet_len < 3) or (tweet_len >= 10):
        return False
    # has blacklistd words/ sybols?
    for x in ["@", "\n"]:
        if x in t:
            return False
    return True


def save_status(status):
    return dict(
        id=status.id,
        text=status.text,
        author=status.author.screen_name,
        time=status.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    )


def main():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, accss_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    archive = load_archive()
    print(">> Load archive")
    print(">> archive length: ", len(archive))

    n = 100
    for i in trange(n):
        # get tweets
        statuses = get_tweets(api)
        # get into save format
        tweets = [save_status(s) for s in statuses]
        # add to archive list
        archive.extend(tweets)

    # save to file
    update_archive(archive)
    print(">> Saved to archive")
    print(">> archive length: ", len(archive))


if __name__ == "__main__":
    main()
