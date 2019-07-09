import os
import pickle
import sys
from datetime import datetime
from itertools import combinations
from multiprocessing import Pool
from statistics import mean

from tqdm.auto import tqdm

from paradeller.analysis import (
    find_matches,
    find_matches_for_start_pairs,
    get_stanzas,
    find_final_stanzas,
)
from paradeller.helper import read_from_pickle

# load saved data from pickle
print("loading saved data from pickle...")
_, _, adj_list_words, adj_list_ids = read_from_pickle()

# sort tweet ids by avg popularity of its words
print("sorting by popularity...")
pop = []
for tweet_id, words in tqdm(adj_list_ids.items()):
    pop.append((tweet_id, mean([len(adj_list_words[word]) for word in words])))
pop.sort(key=lambda x: x[1], reverse=True)

# define helper functions that takes single parameter


def find_matches_for_pair(p):
    return find_matches(p[0], p[1], adj_list_ids, adj_list_words)


def find_final_stanzas_helper(stanzas):
    find_final_stanzas(*stanzas, adj_list_ids, adj_list_words)


if __name__ == "__main__":
    default_n = "100"

    # parse command line arguments
    args_dict = dict(enumerate(sys.argv))
    n = int(args_dict.get(1, default_n))

    # ---------- LOOK FOR STANZAS ----------

    # choose some IDS
    some_ids = [x[0] for x in pop[:n]]
    pairs = list(combinations(some_ids, 2))

    # search
    print("searching for matches, using {} ids".format(n))
    with Pool(os.cpu_count()) as pool:
        res = list(tqdm(pool.imap(find_matches_for_pair, pairs), total=len(pairs)))

    # zip results with search pairs, filter out empty
    all_valid = [x for x in list(zip(pairs, res)) if x[1]]
    print("Found {} results.".format(len(all_valid)))

    # get filename
    d = datetime.utcnow()
    filename = "data/found_stanzas_{}.pickle".format(d.strftime("%Y-%m-%d-%H-%M"))

    # save to file
    with open(filename, "wb") as f:
        pickle.dump(all_valid, f)
    print("stanzas saved to data/found_stanzas_[datetime].pickle")

    # ---------- LOOK FOR PARADELLES ----------
    if len(all_valid) >= 3:
        stanzas = get_stanzas(all_valid)

        # find combos to chcek
        print("Finding combos to check...")
        all_combos = combinations(stanzas, 3)
        combos = [c for c in all_combos if len(set().union(*c)) == 12]

        # look for complete paradelles
        print("searching for complete paradelles within found stanzas")
        with Pool(os.cpu_count()) as pool:
            res = list(
                tqdm(pool.imap(find_final_stanzas_helper, combos), total=len(combos))
            )
        all_poems = [x for x in list(zip(combos, res)) if x[1]]
        print("Found {} poems.".format(len(all_poems)))

        # get filename
        filename = "data/found_poems_{}.pickle".format(d.strftime("%Y-%m-%d-%H-%M"))

        # save to file
        with open(filename, "wb") as f:
            pickle.dump(all_valid, f)
        print("results saved to data/found_poems_[datetime].pickle")
    else:
        print("No complete poems found :(")
