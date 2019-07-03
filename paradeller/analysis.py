import string
from collections import defaultdict
from itertools import combinations
from typing import Dict, Iterable, List

import emoji
import numpy as np
from joblib import Parallel, delayed
from numba import jit
from tqdm.auto import tqdm, trange

# ---------- PREP DATA ----------


def tokenize(text, keep_emoji=False):
    """
    Tokenize tweet text (split into list cleaned-up words)

    Parameters
    ----------
    keep_emoji : bool
        Whether emojis should be retained like words
        or stripped away like punctuation

    Returns
    -------
    list
        list of standardized tokens
    """
    # replace punctuation with whitespace
    text = text.translate(
        str.maketrans(string.punctuation, " " * len(string.punctuation))
    )
    # either add space between emoji chars or remove
    emoji_pattern = emoji.get_emoji_regexp()
    if keep_emoji:
        text = " ".join(emoji_pattern.split(text))
    else:
        text = emoji_pattern.sub("", text)
    # split into words & clean each word
    words = text.split()
    return [w.lower().strip() for w in words]


# EXPERIMENT - NOT IN USE
def find_duplicates_jit(data):
    """
    Keys are unique word sets (sorted tuples),
    values are list of ids
    """
    # empty_int_list = lambda: [np.int64(x) for x in range(0)]
    duplicates = {}

    for item in data:
        words = tokenize(item["text"])
        words_tup = tuple(sorted(words))
        duplicates[words_tup] = duplicates.get(
            words_tup, [np.int64(x) for x in range(0)]
        ) + [item["id"]]
    return dict(duplicates)


def find_duplicates(data):
    """
    Keys are unique word sets (sorted tuples),
    values are list of ids
    """
    duplicates = defaultdict(list)
    for item in tqdm(data):
        words = tokenize(item["text"])
        words_tup = tuple(sorted(words))
        duplicates[words_tup].append(item["id"])
    return dict(duplicates)


def filter_out_duplicates(data, duplicates):
    """
    Only keep first instance of every phrase
    """
    unique_phrase_ids = [x[0] for x in list(duplicates.values())]
    unique_phrase_ids = set(unique_phrase_ids)
    return [x for x in data if x["id"] in unique_phrase_ids]


def filter_out_oddballs(data):
    """
    Filter out tweets that don't share each word with 2 other lines
    """
    # create an adj list by word
    adj_list_words = create_adj_list_by_word(data)

    # find words with too few matches
    filtered_adj_list_words = {k: v for k, v in adj_list_words.items() if len(v) < 3}

    # consolidate ids to remove
    rm_ids = set().union(*filtered_adj_list_words.values())

    # remove from data
    return [x for x in data if x["id"] not in rm_ids]


def restructure_data(data) -> tuple:
    """
    Restructure data into 2 adjacency lists.

    Parameters
    ----------
    data : list
        list of tweet dicts, each with "text" and "id"

    Returns
    -------
    tuple
        adj_list_by_word -- {word: {ids}}
        adj_list_by_id ---- {id  : [words]}
    """
    adj_list_by_word: Dict[str, set] = defaultdict(set)
    adj_list_by_id: Dict[int, set] = defaultdict(set)

    for item in tqdm(data):
        tokens = tokenize(item["text"])
        adj_list_by_id[item["id"]] = tokens
        for token in tokens:
            adj_list_by_word[token].add(item["id"])
    return dict(adj_list_by_word), dict(adj_list_by_id)


def create_adj_list_by_id(data):
    adj_list_by_id: Dict[int, set] = defaultdict(set)
    for item in tqdm(data):
        tokens = tokenize(item["text"])
        adj_list_by_id[item["id"]] = tokens
    return dict(adj_list_by_id)


def create_adj_list_by_word(data):
    adj_list_by_word: Dict[str, set] = defaultdict(set)
    for item in tqdm(data):
        tokens = tokenize(item["text"])
        for token in tokens:
            adj_list_by_word[token].add(item["id"])
    return dict(adj_list_by_word)


# ---------- FIND MATCHES ----------


def find_matches_for_start_pairs(pairs, adj_list_ids, adj_list_words):
    """Given a collection of potential start pairs, look for matches on each"""
    all_valid = {}
    for p in tqdm(pairs):
        valid = find_matches(p[0], p[1], adj_list_ids, adj_list_words)
        if valid:
            all_valid[p] = valid
    return all_valid


def find_matches(id1, id2, adj_list_ids, adj_list_words, verbose=False):
    """Given a pair of tweets, look for matches to finish the stanza"""

    # combine words from tweets
    stanza_words = sorted(adj_list_ids[id1] + adj_list_ids[id2])

    # look for other tweets with those words
    pot_ids = get_potential_tweets(stanza_words, adj_list_words)

    if verbose:
        print("stanza words :", stanza_words)
        print("pot_ids      :", len(pot_ids))

    # --- filter down ---
    # remove start tweets
    # ensure tweets contain subset of master_word_set
    pot_ids = pot_ids - {id1, id2}
    pot_ids = [x for x in pot_ids if set(adj_list_ids[x]) <= set(stanza_words)]

    if verbose:
        print("filt pot_ids :", len(pot_ids))

    # look for valid pairs of potential tweets
    if len(pot_ids) > 1:
        return find_valid_matches(pot_ids, adj_list_ids, stanza_words)
    return []


def get_potential_tweets(stanza_words, adj_list_words):
    """Get all tweets that share words with start tweets"""
    potential_ids = set()
    for word in stanza_words:
        potential_ids.update(adj_list_words[word])
    return potential_ids


# @jit(nopython=True)
def find_valid_matches(pot_ids, adj_list_ids, stanza_words):
    # make pairings of two potential tweets
    combos = list(combinations(pot_ids, 2))

    # for each pair:
    # get combination of words, check if equals stanza_words
    valid = []
    for pair in combos:
        a, b = pair
        words = sorted(adj_list_ids[a] + adj_list_ids[b])
        if words == stanza_words:
            valid.append(pair)
    return valid


# EXPERIMENT - NOT IN USE
def find_valid_matches_parallel(pot_ids, adj_list_ids, stanza_words):
    # make pairings of two potential tweets
    combos = list(combinations(pot_ids, 2))

    def check_pair(pair):
        a, b = pair
        words = sorted(adj_list_ids[a] + adj_list_ids[b])
        if words == stanza_words:
            return pair
        return None

    valid = Parallel(n_jobs=2)(delayed(check_pair)(p) for p in combos)
    valid = [x for x in valid if x is not None]
    return valid


# def display_matches(all_valid):
#     for pair, matches in all_valid.items():
#         t1, t2 = pair
#         stanza_start = [t1, t1, t2, t2]
#         for match in matches:
#             a, b = match
#             stanza = stanza_start + [a, b]
#             print("~" * 50)
#             for t in stanza:
#                 tweet = get_tweet(t)
#                 print(f"@{tweet['author']:20} {tweet['text']} ")
