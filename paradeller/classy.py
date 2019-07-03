from paradeller.dataprep import (
    tokenize,
    find_duplicates,
    filter_out_duplicates,
    filter_out_short,
    filter_out_oddballs,
    filter_out_oddballs_recursive,
    restructure_data,
    create_adj_list_by_word,
    create_adj_list_by_id,
)


class RoboPoet:
    def __init__(self, data):
        self.data = data
        self.duplicates = find_duplicates(data)

    def filter_data(self):
        data = filter_out_short(self.data)
        data = filter_out_duplicates(data, self.duplicates)
        data = filter_out_oddballs_recursive(data)
