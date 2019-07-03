import pickle
from itertools import combinations
from statistics import mean

from joblib import Parallel, delayed
from tqdm.auto import tqdm

from paradeller.analysis import find_matches, find_matches_for_start_pairs
from paradeller.helper import read_from_pickle


def main(n=10):
    _, _, adj_list_words, adj_list_ids = read_from_pickle()

    # sort tweet ids by avg popularity of its words
    print("sorting by popularity")
    pop = []
    for tweet_id, words in tqdm(adj_list_ids.items()):
        pop.append((tweet_id, mean([len(adj_list_words[word]) for word in words])))
    pop.sort(key=lambda x: x[1], reverse=True)

    # choose some IDS
    some_ids = [x[0] for x in pop[:n]]
    pairs = list(combinations(some_ids, 2))

    # search
    print(f"searching for matches, using {n} ids")
    all_valid = find_matches_for_start_pairs(pairs, adj_list_ids, adj_list_words)

    # save to file
    with open("data/found.pickle", "wb") as f:
        pickle.dump(all_valid, f)


# def run_parallel():
#     data, duplicates, adj_list_words, adj_list_ids = read_from_pickle()

#     def find_matches_for_pair(p):
#         return find_matches(p[0], p[1], adj_list_ids, adj_list_words)

#     Parallel(n_jobs=4)(delayed(find_matches_for_pair)(p) for p in pairs)


if __name__ == "__main__":
    main()
