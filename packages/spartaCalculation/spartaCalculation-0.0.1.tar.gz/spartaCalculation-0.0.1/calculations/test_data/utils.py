import json
import os

dir_path = os.path.dirname(os.path.abspath(__file__))


def read_test_data(path):
    annotations_path = os.path.join(dir_path, path)
    annotations_file = open(annotations_path)

    return json.load(annotations_file)
