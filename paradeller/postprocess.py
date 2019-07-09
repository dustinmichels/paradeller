def stanza_sorter_maker(adj_list_ids):
    def stanza_sorter(stanza):
        """
        Sort by interesting-ness
        """

        # --- points for length ---
        ids = set(stanza)
        len_pts = sum((len(adj_list_ids[i]) for i in ids))

        # --- points for variance ---
        lineA = adj_list_ids[stanza[0]]
        lineB = adj_list_ids[stanza[1]]
        lineC = adj_list_ids[stanza[2]]
        lineD = adj_list_ids[stanza[3]]

        # diff b/w A and B
        diff_pts = len(set(lineA) ^ set(lineB))

        # points for different start words
        start_letters = set((x[0] for x in [lineA, lineB, lineC, lineD]))
        start_pts = len(start_letters)

        pts = sum((len_pts, (diff_pts * 8), (start_pts * 20)))
        return pts

    return stanza_sorter


def print_stanza(stanza, data):
    get_line = lambda id: next(x for x in data if x["id"] == id)
    for i in [0, 0, 1, 1, 2, 3]:
        id_ = stanza[i]
        line = get_line(id_)
        print(f"@{line['author']:20} {line['text']} ")


def print_stanzas(stanzas, data, n=50):
    for stanza in stanzas[:n]:
        print("~" * 50)
        print_stanza(stanza, data)


def print_poems(poems, data, n=50):
    get_line = lambda id: next(x for x in data if x["id"] == id)
    for poem in poems[:n]:
        print("~" * 50)
        *init_stanzas, last_stanza = poem
        for s in init_stanzas:
            print_stanza(s, data)
            print()
        for id_ in last_stanza:
            line = get_line(id_)
            print(f"@{line['author']:20} {line['text']} ")
