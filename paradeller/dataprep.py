import string
from collections import defaultdict, Counter
from statistics import mean
from typing import Dict

import emoji
from tqdm.auto import tqdm

from paradeller.helper import load_archive, read_from_pickle, save_to_pickle


def tokenize(text):
    """
    Tokenize tweet text (split into list cleaned-up words)

    Returns
    -------
    list
        list of standardized tokens
    """
    # remove apostraphe
    text = text.replace("'", "")
    # replace other punctuation with space
    punc = '!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~“”'
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


def filter_out_short(data, n=4, **kwargs):
    """Only keep tweets with # tokens >= n"""
    nobar = kwargs.get("nobar", False)
    return [x for x in tqdm(data, disable=nobar) if len(tokenize(x["text"])) >= n]


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


def filter_out_oddballs(data, **kwargs):
    """
    Filter out tweets that:
      1) Don't share each word with at least 2 other lines
      2) Include a word enough times that too few remain to complete a poem
    """
    # --- SETUP ---
    # create an adj lists
    adj_list_words, adj_list_ids = restructure_data(data, **kwargs)

    # get overall word count
    overall_wc = Counter()
    for words in adj_list_ids.values():
        overall_wc.update(words)

    # --- INSUFFICIENT IDS ---
    # find words that don't appear in at least 3 tweets
    filtered_adj_list_words = {k: v for k, v in adj_list_words.items() if len(v) < 3}

    # consolidate ids to remove
    rm_ids = set().union(*filtered_adj_list_words.values())

    # --- INSUFFICIENT WORD COUNTS ---
    ids = list(adj_list_ids.keys())
    for i in ids:
        counts = Counter(adj_list_ids[i])
        sufficient = lambda word: overall_wc[word] - counts[word] >= (counts[word] * 2)
        if not all([sufficient(word) for word in counts]):
            rm_ids.add(i)

    # remove from data
    return [x for x in data if x["id"] not in rm_ids]


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
        (adj_list_by_word, adj_list_by_id)
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
    showlen = lambda data: print(f"  length: {len(data):,}\n") if verbose else None
    printif = lambda s: print(s) if verbose else None
    nobar = not verbose

    showlen(data)
    printif("\nCleaning up data...")

    # remove too short
    printif("> Remove too short") if verbose else None
    data = filter_out_short(data, n=4, nobar=nobar)
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
    print("")
    if use_pickle:
        print("Loading processed data from pickle...")
        data, duplicates, adj_list_words, adj_list_ids = read_from_pickle()
    else:
        print("Loading raw data from archive.json...")
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
