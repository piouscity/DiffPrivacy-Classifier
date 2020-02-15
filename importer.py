import os, csv
from exceptions import OpenFileException


def import_dataset(file_path):
    return import_csv_dataset(file_path)


def import_csv_dataset(file_path):
    try:
        with open(file_path) as csv_file:
            dataset = [{key: float(value) for key, value in row.items()}
                       for row in csv.DictReader(csv_file, skipinitialspace=True)]
    except IOError:
        raise OpenFileException(file_path)
    return dataset


def import_taxonomy_tree(file_path):
    return {}
