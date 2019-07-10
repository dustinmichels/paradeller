import os
import sys
from itertools import combinations
from multiprocessing import Pool

from tqdm.auto import tqdm

import googlecloudprofiler
from paradeller.analysis import (
    consolidate_poems,
    consolidate_stanzas,
    find_final_stanzas,
    find_matches,
)
from paradeller.dataprep import load_and_prep, sort_ids_by_popularity
from paradeller.helper import save_results


def find_matches_for_pair(p):
    """Helper function to find initial stanzas, given a pair of lines"""
    return find_matches(p[0], p[1], adj_list_ids, adj_list_words)


def find_final_stanzas_helper(stanzas):
    """Helper function to find final stanzas, given a group of 3 stanzas"""
    return find_final_stanzas(*stanzas, adj_list_ids, adj_list_words)


def init_google_profiler():
    # Profiler initialization. It starts a daemon thread which continuously
    # collects and uploads profiles. Best done as early as possible.
    try:
        googlecloudprofiler.start(
            service="paradeller",
            service_version="1.0.1",
            # verbose is the logging level. 0-error, 1-warning, 2-info,
            # 3-debug. It defaults to 0 (error) if not set.
            verbose=3,
            # project_id must be set if not running on GCP.
            # project_id='my-project-id',
        )
    except (ValueError, NotImplementedError) as exc:
        print(exc)  # Handle errors here


if __name__ == "__main__":
    # init profiling
    if os.getenv("USER", "") == "dustin7538":
        init_google_profiler()

    # parse command line arguments
    default_n = "100"
    default_style = "load"  # or "load" | "fresh"

    args_dict = dict(enumerate(sys.argv))
    n = int(args_dict.get(1, default_n))
    style = args_dict.get(2, default_style)

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
    with Pool(os.cpu_count()) as pool:
        res = list(tqdm(pool.imap(find_matches_for_pair, pairs), total=len(pairs)))

    # zip results with search pairs, filter out empty
    valid_stanzas = [x for x in list(zip(pairs, res)) if x[1]]
    stanzas = consolidate_stanzas(valid_stanzas)
    print(f"Found {len(stanzas)} results.")

    # ---------- LOOK FOR PARADELLES ----------
    if len(stanzas) >= 3:
        # find combos to chcek
        print("Finding combos to check (this may take a while)...")
        all_combos = combinations(stanzas, 3)
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
    results = dict(stanzas=stanzas, poems=poems, duplicates=duplicates)
    save_results(results)
    print("results saved to data/found/results_[datetime].pickle")
