import os
import sys
from collections import defaultdict
from datetime import datetime
from itertools import combinations
from multiprocessing import Pool

import googlecloudprofiler
from tqdm.auto import tqdm

from paradeller.analysis import (
    consolidate_poems,
    consolidate_stanzas,
    find_final_stanzas,
    find_matches,
)
from paradeller.dataprep import load_and_prep, sort_ids_by_popularity
from paradeller.helper import DATE_FMT, save_results


def find_matches_for_pair(p):
    """Helper function to find initial stanzas, given a pair of lines"""
    return find_matches(p[0], p[1], adj_list_ids, adj_list_words)


def find_final_stanzas_helper(stanzas):
    """Helper function to find final stanzas, given a group of 3 stanzas"""
    return find_final_stanzas(*stanzas, adj_list_ids, adj_list_words)


if __name__ == "__main__":
    # init profiling, if running on Google Compute Engine
    if os.getenv("USER", "") == "dustin7538":
        print("Initialzing Google profiler...")
        googlecloudprofiler.start(service="paradeller", verbose=1)

    # parse command line arguments
    args_dict = dict(enumerate(sys.argv))
    n = int(args_dict.get(1, "100"))  # number of ids to pair off
    style = args_dict.get(2, "load")  # load from picke, or prepare data anew

    # note start time
    start_time = datetime.utcnow()

    # ---------- LOOK FOR STANZAS ----------

    # load & prepare data
    use_pickle = style == "load"
    data, duplicates, adj_list_words, adj_list_ids = load_and_prep(
        use_pickle=use_pickle
    )

    # sort tweet ids by avg popularity of its words
    print("\nSorting by popularity...")
    sorted_ids = sort_ids_by_popularity(adj_list_ids, adj_list_words)

    # choose some IDS
    some_ids = sorted_ids[:n]
    pairs = list(combinations(some_ids, 2))

    # search for stanzas
    print(f"\nSearching for matches, using {n} ids")
    d = defaultdict(list)
    for pair in tqdm(pairs):
        w1 = adj_list_ids[pair[0]]
        w2 = adj_list_ids[pair[1]]
        words = tuple(sorted(w1 + w2))
        d[words].append(pair)

    # zip results with search pairs, filter out empty
    valid_stanzas = [x for x in list(zip(pairs, res)) if x[1]]
    stanzas = consolidate_stanzas(valid_stanzas)
    print(f"Found {len(stanzas)} results.")

    # ---------- LOOK FOR PARADELLES ----------
    if len(stanzas) >= 3:
        print("Finding stanza combinations to check...")
        # all combinations of stanzas
        all_combos = combinations(stanzas, 3)
        # create generator for stanza combimations where all lines are unique
        combos = (c for c in all_combos if len(set().union(*c)) == 12)

        # look for complete paradelles
        print("Searching for complete paradelles")
        with Pool(os.cpu_count()) as pool:
            res = list(tqdm(pool.imap(find_final_stanzas_helper, combos)))
        valid_poems = [x for x in list(zip(combos, res)) if x[1]]
        poems = consolidate_poems(valid_poems)
        print(f"Found {len(poems)} poems.")
    else:
        print("Not enough stanzas to check for poems")
        poems = []

    # ---------- SUMMARIZE & SAVE ----------
    stop_time = datetime.utcnow()
    meta = dict(
        start_time=start_time.strftime(DATE_FMT),
        stop_time=stop_time.strftime(DATE_FMT),
        n=n,
        style=style,
        data_len=len(data),
    )
    results = dict(meta=meta, stanzas=stanzas, poems=poems, duplicates=duplicates)
    save_results(results)
