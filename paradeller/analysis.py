import string
from collections import defaultdict
from itertools import combinations
from typing import Dict, Iterable, List

import emoji
from tqdm import tqdm, trange

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
        adj_list_by_word -- {word: {set of ids}}
        adj_list_by_id ---- {id  : {set of words}}
    """
    adj_list_by_word: Dict[str, set] = defaultdict(set)
    adj_list_by_id: Dict[int, set] = defaultdict(set)
    for item in data:
        tokens = tokenize(item["text"])
        adj_list_by_id[item["id"]] = set(tokens)
        for token in tokens:
            adj_list_by_word[token].add(item["id"])
    return dict(adj_list_by_word), dict(adj_list_by_id)


# ---------- FILTER CHOICE ----------


def get_nondup_ids(adj_list_ids):
    duplicates = find_duplicates(adj_list_ids)
    ids = [x[0] for x in list(duplicates.values())]
    return set(ids)


def find_duplicates(adj_list_ids):
    """
    Keys are unique word sets (sorted tuples),
    values are list of ids
    """
    duplicates = defaultdict(list)
    for id_, words in adj_list_ids.items():
        unique_word_set = tuple(sorted(words))
        duplicates[unique_word_set].append(id_)
    return duplicates


# ---------- FIND MATCHES ----------


def find_maches(id1, id2, adj_list_ids, adj_list_words):
    master_word_set = adj_list_ids[id1].union(adj_list_ids[id2])

    # find potential tweets
    pot_ids = get_potential_tweets(master_word_set, adj_list_words)

    # --- filter down ---
    # remove start tweets
    # ensure tweets contain subset of master_word_set
    pot_ids = pot_ids - {id1, id2}
    pot_ids = [x for x in pot_ids if adj_list_ids[x] <= master_word_set]

    # check if they are valid
    valid = find_valid_matches(pot_ids, adj_list_ids, master_word_set)
    return valid


def get_potential_tweets(master_word_set, adj_list_words):
    """Get all tweets that share words with start tweets"""
    all_ids = set()
    for word in master_word_set:
        all_ids.update(adj_list_words[word])
    return all_ids


def find_valid_matches(pot_ids, adj_list_ids, master_word_set):
    # make pairings of two potential tweets
    combos = list(combinations(pot_ids, 2))

    # for each pair: get all words in union of two tweets
    # if this set equals master word set, we found valid set
    valid = []
    for pair in combos:
        a, b = pair
        words = adj_list_ids[a].union(adj_list_ids[b])
        if words == master_word_set:
            valid.append(pair)
    return valid

