import string
from collections import defaultdict
from typing import Dict, Iterable, List

import emoji
import numpy as np
from tqdm.auto import tqdm, trange

from paradeller.helper import load_archive, read_from_pickle, save_to_pickle


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
    """Only keep tweets with # tokens >= n"""
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


# ---------- COMBINED ----------


def load_and_prep(use_pickle=False, update_pickle=False):
    """
    Load and prep all data, either from file or from pickle.
    Returns tuple: data, duplicates, adj_list_words, adj_list_ids
    """

    if use_pickle:
        print("Loading real, processed data from pickle...")
        data, duplicates, adj_list_words, adj_list_ids = read_from_pickle()
    else:
        print("Loading unprocessed real data...")
        data = load_archive()

        showlen = lambda data: print(f"Length: {len(data):,}")

        showlen(data)
        print("\nCleaning up data...")

        # remove too short
        print("> Remove too short")
        data = filter_out_short(data)
        showlen(data)

        # remove duplicate phrases
        print("> Remove duplicate phrases")
        duplicates = find_duplicates(data)
        data = filter_out_duplicates(data, duplicates)
        showlen(data)

        # remove oddballs (too few matches)
        print("> Recursively remove oddballs")
        data = filter_out_oddballs_recursive(data)
        showlen(data)

        print("\nCreating adjacency lists...")
        # make adj lists
        adj_list_words, adj_list_ids = restructure_data(data)

        if update_pickle:
            print("\nSaving new data to pickle...")
            save_to_pickle((data, duplicates, adj_list_words, adj_list_ids))

    print("-" * 50)
    print("DONE\n")
    stuff = {
        "data": data,
        "duplicates": duplicates,
        "adj_list_words": adj_list_words,
        "adj_list_ids": adj_list_ids,
    }
    for k, v in stuff.items():
        print(f"{k:15} type: {type(v)}\tlen: {len(v):,}")

    return data, duplicates, adj_list_words, adj_list_ids
