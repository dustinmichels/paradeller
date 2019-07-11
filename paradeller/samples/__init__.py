from paradeller.dataprep import tokenize
from .poems import samples


def load_samples():
    counter = 0
    data = []
    for i, sample in enumerate(samples):
        name = f"sample{i}"
        sample_data, counter = datafy_poem(sample, name, counter)
        data.extend(sample_data)
    return data


def datafy_poem(text, name, counter):
    # get lines, remove duplicates
    lines = [" ".join(tokenize(x)) for x in text.split("\n") if x != ""]
    # convert to dict
    data = []
    for i, line in enumerate(lines):
        data.append(dict(id=counter, text=line, poem=name, line=i, author="unknown"))
        counter += 1
    return data, counter

