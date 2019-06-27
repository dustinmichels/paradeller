import json
import os

fp = os.path.abspath("../data/archive.json")


def load_archive():
    with open(fp) as file:
        return json.load(file)


def update_archive(archive):
    with open(fp, "w") as file:
        json.dump(archive, file)
