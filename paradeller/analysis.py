import string
from collections import defaultdict
from itertools import combinations, chain
from typing import Dict, Iterable, List, Set

import emoji
import numpy as np
from tqdm.auto import tqdm, trange

# ---------- FIND STANZAS ----------


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


def get_potential_tweets(stanza_words, adj_list_words) -> Set[int]:
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
    valid = []
    for pair in combos:
        words = adj_list_ids[pair[0]] + adj_list_ids[pair[1]]
        if sorted(words) == sorted(stanza_words):
            valid.append(pair)
    return valid


# ---------- FIND POEMS ----------


def find_final_stanzas(stan1, stan2, stan3, adj_list_ids, adj_list_words, all_valid):

    pair1, pair2, pair3 = stan1[:2], stan2[:2], stan3[:2]

    # combine words from tweets
    prev_stanza_words = list(
        chain.from_iterable([adj_list_ids[line] for line in [*pair1, *pair2, *pair3]])
    )

    # look for other tweets with those words
    pot_ids = get_potential_final_lines(prev_stanza_words, adj_list_words)

    # --- filter down ---
    # remove lines from previous stanzas
    # ensure tweets contain subset of master_word_set
    pot_ids = pot_ids - {*stan1, *stan2, *stan3}
    pot_ids = [x for x in pot_ids if set(adj_list_ids[x]) <= set(prev_stanza_words)]

    # look for valid pairs of potential tweets
    if len(pot_ids) > 1:
        return find_valid_matches(pot_ids, adj_list_ids, stanza_words)
    return []


def get_potential_final_lines(stanza_words, adj_list_words) -> Set[int]:
    """Potential lines for final stanza"""
    potential_ids: Set[int] = set()
    for word in stanza_words:
        potential_ids.update(adj_list_words[word])
    return potential_ids


def find_valid_lines(pot_ids, adj_list_ids, stanza_words):
    """Find valid lines for final stanza"""

    # make pairings of two potential tweets
    combos = list(combinations(pot_ids, 2))

    # for each pair:
    # get combination of words, check if equals stanza_words
    valid = []
    for pair in combos:
        words = adj_list_ids[pair[0]] + adj_list_ids[pair[1]]
        if sorted(words) == sorted(stanza_words):
            valid.append(pair)
    return valid


# ---------- READ RESULTS ----------


def get_stanzas(all_valid):
    stanzas = []
    for pair, matches in all_valid:
        t1, t2 = pair
        stanza_start = [t1, t2]
        for match in matches:
            a, b = match
            stanza = stanza_start + [a, b]
        stanzas.append(tuple(stanza))
    return stanzas
