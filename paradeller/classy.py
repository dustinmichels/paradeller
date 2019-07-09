from paradeller.dataprep import (
    find_duplicates,
    filter_out_duplicates,
    filter_out_short,
    filter_out_oddballs_recursive,
)


class RoboPoet:
    def __init__(self, data):
        self.data = data
        self.duplicates = find_duplicates(data)

    def filter_data(self):
        data = filter_out_short(self.data)
        data = filter_out_duplicates(data, self.duplicates)
        data = filter_out_oddballs_recursive(data)
