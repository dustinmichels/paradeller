import string
from collections import defaultdict
from typing import Dict, Iterable, List

import emoji
import numpy as np
from joblib import Parallel, delayed
from numba import jit
from tqdm.auto import tqdm, trange


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


# ---------- FILTERING ----------


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


def filter_out_short(data, n=3):
    """Only keep tweets with >= n tokens"""
    return [x for x in tqdm(data) if len(tokenize(x["text"])) >= n]


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


def filter_out_oddballs_recursive(data):
    start_len = len(data)
    data = filter_out_oddballs(data)
    diff = start_len - len(data)
    if diff == 0:
        print("Nothing removed. Done filtering.")
        return data
    else:
        print(f"{diff} tweets removed. Running again.")
        return filter_out_oddballs_recursive(data)


# ---------- RESTRUCTURING ----------


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
        adj_list_by_id -- {id  : [words]}
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
