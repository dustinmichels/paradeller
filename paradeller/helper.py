import json
import os
import pickle


fp = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/archive.json"))
pickle_fp = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../data/stuff.pickle")
)


def load_archive():
    """Load data file from json"""
    with open(fp) as file:
        return json.load(file)


def update_archive(archive):
    """Save data file to json"""
    with open(fp, "w") as file:
        json.dump(archive, file)


def save_to_pickle(stuff):
    """
    Save "stuff" as pickle.
    Stuff should be tuple: (data, duplicates, adj_list_words, adj_list_ids)
    """
    with open(pickle_fp, "wb") as file:
        pickle.dump(stuff, file)


def read_from_pickle():
    """
    Load "stuff" from pickle.
    Stuff should be tuple: (data, duplicates, adj_list_words, adj_list_ids)
    """
    with open(pickle_fp, "rb") as file:
        return pickle.load(file)
