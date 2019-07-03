from paradeller.analysis import tokenize
from .poems import sample1, sample2, sample3


def load_samples():
    counter = 0
    data1, counter = datafy_poem(sample1, "sample1", counter)
    data2, counter = datafy_poem(sample2, "sample2", counter)
    data3, counter = datafy_poem(sample3, "sample3", counter)
    return data1 + data2 + data3


def datafy_poem(text, name, counter):
    # get lines, remove duplicates
    lines = [" ".join(tokenize(x)) for x in text.split("\n") if x != ""]
    # convert to dict
    data = []
    for i, line in enumerate(lines):
        data.append(dict(id=counter, text=line, poem=name, line=i, author="unknown"))
        counter += 1
    return data, counter

