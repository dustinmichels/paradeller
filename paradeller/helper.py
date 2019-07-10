import json
import os
import pickle
from datetime import datetime

data_fp = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
archive_fp = os.path.join(data_fp, "archive.json")
pickle_fp = os.path.join(data_fp, "stuff.pickle")


def load_archive():
    """Load data file from json"""
    with open(archive_fp) as file:
        return json.load(file)


def update_archive(archive):
    """Save data file to json"""
    with open(archive_fp, "w") as file:
        json.dump(archive, file)


def save_results(results):
    """Save results dict as JSON"""
    dt_string = datetime.utcnow().strftime("%Y-%m-%d-%H%M")
    filename = f"results_{dt_string}.json"
    fp = os.path.join(data_fp, "found", filename)
    with open(fp, "w") as file:
        json.dump(results, file)
    print(f"results saved to {fp}")


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
