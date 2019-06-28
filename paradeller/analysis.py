import emoji
import string


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
    # remove punctuaation
    text = text.translate(str.maketrans("", "", string.punctuation))

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
