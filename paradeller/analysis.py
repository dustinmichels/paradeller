import string
from collections import defaultdict
from itertools import combinations
from typing import Dict, Iterable, List

import emoji
import numpy as np
from tqdm.auto import tqdm, trange

# from joblib import Parallel, delayed
# from numba import jit


def find_matches_for_start_pairs(pairs, adj_list_ids, adj_list_words):
    """Given a collection of potential start pairs, look for matches on each"""
    all_valid = {}
    for p in tqdm(pairs):
        valid = find_matches(p[0], p[1], adj_list_ids, adj_list_words)
        if valid:
            all_valid[p] = valid
    return all_valid


def find_matches(id1, id2, adj_list_ids, adj_list_words):
    """Given a pair of tweets, look for matches to finish the stanza"""

    # combine words from tweets
    stanza_words = adj_list_ids[id1] + adj_list_ids[id2]

    # look for other tweets with those words
    pot_ids = get_potential_tweets(stanza_words, adj_list_words)

    # --- filter down ---
    # remove start tweets
    # ensure tweets contain subset of master_word_set
    pot_ids = pot_ids - {id1, id2}
    pot_ids = [x for x in pot_ids if set(adj_list_ids[x]) <= set(stanza_words)]

    # look for valid pairs of potential tweets
    if len(pot_ids) > 1:
        return find_valid_matches(pot_ids, adj_list_ids, stanza_words)
    return []


def get_potential_tweets(stanza_words, adj_list_words) -> set:
    """Get all tweets that share words with start tweets"""
    potential_ids: Set[int] = set()
    for word in stanza_words:
        potential_ids.update(adj_list_words[word])
    return potential_ids


def find_valid_matches(pot_ids, adj_list_ids, stanza_words):
    # make pairings of two potential tweets
    combos = list(combinations(pot_ids, 2))

    # for each pair:
    # get combination of words, check if equals stanza_words
    # TODO: check pair len? skip sorting?
    valid = []
    for pair in combos:
        words = adj_list_ids[pair[0]] + adj_list_ids[pair[1]]
        if sorted(words) == sorted(stanza_words):
            valid.append(pair)
    return valid


# EXPERIMENT - NOT IN USE
# def find_valid_matches_parallel(pot_ids, adj_list_ids, stanza_words):
#     # make pairings of two potential tweets
#     combos = list(combinations(pot_ids, 2))

#     def check_pair(pair):
#         a, b = pair
#         words = sorted(adj_list_ids[a] + adj_list_ids[b])
#         if words == stanza_words:
#             return pair
#         return None

#     valid = Parallel(n_jobs=2)(delayed(check_pair)(p) for p in combos)
#     valid = [x for x in valid if x is not None]
#     return valid


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
