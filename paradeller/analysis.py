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


def create_word_dict(data):
    d = defaultdict(list)
    for item in data:
        # get tokens
        tokens = tokenize(item["text"])
        for token in tokens:
            d[token].append(item["id"])
    return dict(d)


def get_combos(tokens):
    """
    Keep all combinations of token (sorted)
    """
    total = []
    for i in range(1, len(tokens) + 1):
        combos = list(combinations(sorted(tokens), i))
        total.extend(combos)
    return total


def load_all(data: list):
    """
    Create dict where combo-tuples are keys
    and list of ids are values
    """
    my_data = defaultdict(list)

    # for item in tqdm(data):
    for item in data:
        # tokenize
        tokens = tokenize(item["text"])
        # find comobos
        combos = get_combos(tokens)
        # add to record
        for combo in combos:
            my_data[combo].append(item["id"])
    return my_data
