import string
from collections import defaultdict
from itertools import combinations

import emoji
from tqdm import tqdm, trange


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

    # handle emoji characters
    emoji_pattern = emoji.get_emoji_regexp()
    if keep_emoji:
        # put space between emoji chars
        text = " ".join(emoji_pattern.split(text))
    else:
        # remove emoji chars
        text = emoji_pattern.sub("", text)

    # split into words & clean each word
    words = text.split()
    return [w.lower().strip() for w in words]


def make_adj_list_by_word(data):
    d = defaultdict(set)
    for item in data:
        # get tokens
        tokens = tokenize(item["text"])
        for token in tokens:
            d[token].add(item["id"])
    return dict(d)


def make_adj_list_by_id(data):
    d = defaultdict(set)
    for item in data:
        # get tokens
        tokens = tokenize(item["text"])
        d[item["id"]] = set(tokens)
    return dict(d)


def get_master_word_set(id1, id2, adj_list_ids):
    all_words = adj_list_ids[id1].union(adj_list_ids[id2])
    return all_words


def get_potential_tweets(id1, id2, adj_list_words, adj_list_ids):
    all_words = get_master_word_set(id1, id2, adj_list_ids)
    all_ids = set()
    for word in all_words:
        all_ids.update(adj_list_words[word])
    return all_ids - {id1, id2}


def filter_potential_tweets(pot_ids, adj_list_ids, master_word_set):
    def is_subset(i):
        words = adj_list_ids[i]
        return words <= master_word_set

    return list(filter(is_subset, pot_ids))


def find_valid_matches(ids, adj_list_ids, master_word_set):
    combos = list(combinations(ids, 2))
    valid = []
    for c in combos:
        words = adj_list_ids[c[0]].union(adj_list_ids[c[1]])
        if words == master_word_set:
            valid.append(c)
    return valid


def find_maches(id1, id2, adj_list_ids, adj_list_words):
    master_word_set = get_master_word_set(id1, id2, adj_list_ids)
    pot_ids = get_potential_tweets(id1, id2, adj_list_words, adj_list_ids)
    pot_ids = filter_potential_tweets(pot_ids, adj_list_ids, master_word_set)
    valid = find_valid_matches(pot_ids, adj_list_ids, master_word_set)
    return valid
