import string
from collections import defaultdict
from statistics import mean
from typing import Dict, Iterable, List

import emoji
import numpy as np
from tqdm.auto import tqdm, trange

from paradeller.helper import load_archive, read_from_pickle, save_to_pickle


def tokenize(text):
    """
    Tokenize tweet text (split into list cleaned-up words)

    Returns
    -------
    list
        list of standardized tokens
    """
    # replace punctuation with whitespace
    punc = string.punctuation + "“" + "”"
    text = text.translate(str.maketrans(punc, " " * len(punc)))
    # remove emoji
    emoji_pattern = emoji.get_emoji_regexp()
    text = emoji_pattern.sub("", text)
    # split into words & clean each word
    words = text.split()
    return [w.lower().strip() for w in words]


# ---------- FILTERING ----------


def find_duplicates(data, **kwargs):
    """
    Keys are unique word sets (sorted tuples),
    values are list of ids
    """
    nobar = kwargs.get("nobar", False)
    duplicates = defaultdict(list)
    for item in tqdm(data, disable=nobar):
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


def filter_out_short(data, n=3, **kwargs):
    """Only keep tweets with # tokens >= n"""
    nobar = kwargs.get("nobar", False)
    return [x for x in tqdm(data, disable=nobar) if len(tokenize(x["text"])) >= n]


def filter_out_oddballs(data, **kwargs):
    """
    Filter out tweets that don't share each word with 2 other lines
    """
    # create an adj list by word
    adj_list_words = create_adj_list_by_word(data, **kwargs)
    # find words with too few matches
    filtered_adj_list_words = {k: v for k, v in adj_list_words.items() if len(v) < 3}
    # consolidate ids to remove
    rm_ids = set().union(*filtered_adj_list_words.values())
    # remove from data
    return [x for x in data if x["id"] not in rm_ids]


def filter_out_oddballs_recursive(data, verbose=True, **kwargs):
    printif = lambda s: print(s) if verbose else None
    start_len = len(data)
    data = filter_out_oddballs(data, **kwargs)
    diff = start_len - len(data)
    if diff == 0:
        printif("Nothing removed. Done filtering.")
        return data
    else:
        printif(f"{diff:,} tweets removed. Running again.")
        return filter_out_oddballs_recursive(data, verbose=verbose, **kwargs)


# ---------- RESTRUCTURING ----------


def restructure_data(data, **kwargs) -> tuple:
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
    nobar = kwargs.get("nobar", False)

    adj_list_by_word: Dict[str, set] = defaultdict(set)
    adj_list_by_id: Dict[int, set] = defaultdict(set)

    for item in tqdm(data, disable=nobar):
        tokens = tokenize(item["text"])
        adj_list_by_id[item["id"]] = tokens
        for token in tokens:
            adj_list_by_word[token].add(item["id"])
    return dict(adj_list_by_word), dict(adj_list_by_id)


def create_adj_list_by_id(data, **kwargs):
    nobar = kwargs.get("nobar", False)
    adj_list_by_id: Dict[int, set] = defaultdict(set)
    for item in tqdm(data, disable=nobar):
        tokens = tokenize(item["text"])
        adj_list_by_id[item["id"]] = tokens
    return dict(adj_list_by_id)


def create_adj_list_by_word(data, **kwargs):
    nobar = kwargs.get("nobar", False)
    adj_list_by_word: Dict[str, set] = defaultdict(set)
    for item in tqdm(data, disable=nobar):
        tokens = tokenize(item["text"])
        for token in tokens:
            adj_list_by_word[token].add(item["id"])
    return dict(adj_list_by_word)


def create_duplicates_dict(adj_list_ids, duplicates):
    """Restructure initial duplicates dictionary into a neater one"""
    d = {}
    for id_, words in adj_list_ids.items():
        sorted_words = tuple(sorted(words))
        dups = set(duplicates[sorted_words]) - {id_}
        if dups:
            d[id_] = list(dups)
    return d


# ---------- COMBINED ----------


def prep_data(data, verbose=True):
    """
    Returns tuple: data, duplicates, adj_list_words, adj_list_ids
    """
    showlen = lambda data: print(f"Length: {len(data):,}") if verbose else None
    printif = lambda s: print(s) if verbose else None
    nobar = not verbose

    showlen(data)
    printif("\nCleaning up data...")

    # remove too short
    printif("> Remove too short") if verbose else None
    data = filter_out_short(data, nobar=nobar)
    showlen(data)

    # remove duplicate phrases
    printif("> Remove duplicate phrases")
    duplicates = find_duplicates(data, nobar=nobar)
    data = filter_out_duplicates(data, duplicates)
    showlen(data)

    # remove oddballs (too few matches)
    printif("> Recursively remove oddballs")
    data = filter_out_oddballs_recursive(data, nobar=nobar, verbose=verbose)
    showlen(data)

    # make adj lists
    printif("\nCreating adjacency lists...")
    adj_list_words, adj_list_ids = restructure_data(data, nobar=nobar)

    # restructure duplicates
    printif("\nRestructing duplicates...")
    duplicates = create_duplicates_dict(adj_list_ids, duplicates)

    return data, duplicates, adj_list_words, adj_list_ids


def load_and_prep(use_pickle=False, update_pickle=False):
    """
    Load and prep all data, either from file or from pickle.
    Returns tuple: data, duplicates, adj_list_words, adj_list_ids
    """

    # TODO: If archive.json newer than stuff.pickle, update pickle

    if use_pickle:
        print("Loading real, processed data from pickle...")
        data, duplicates, adj_list_words, adj_list_ids = read_from_pickle()
    else:
        print("Loading unprocessed real data...")
        data = load_archive()
        data, duplicates, adj_list_words, adj_list_ids = prep_data(data)

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


# --------- SORT ----------


def sort_ids_by_popularity(adj_list_ids, adj_list_words):
    pop = []
    for id_, words in tqdm(adj_list_ids.items()):
        pop.append((id_, mean([len(adj_list_words[word]) for word in words])))
    pop.sort(key=lambda x: x[1], reverse=True)
    ids = [x[0] for x in pop]
    return ids
