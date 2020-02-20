import os, csv, json
from exceptions import OpenFileException, UnsupportedFileTypeException


CSV_EXT = ".csv"
JSON_EXT = ".json"


def import_dataset(file_path):
    file_name, file_ext = os.path.splitext(file_path)
    if file_ext == CSV_EXT:
        return import_csv_dataset(file_path)
    raise UnsupportedFileTypeException(file_path)


def import_csv_dataset(file_path):
    dataset = []
    try:
        with open(file_path) as csv_file:
            for row in csv.DictReader(csv_file, skipinitialspace=True):
                converted_row = {}
                for key, value in row.items():
                    try:
                        float_value = float(value)
                        value = float_value
                    except ValueError:
                        pass
                    converted_row[key] = value
                dataset.append(converted_row)
    except IOError:
        raise OpenFileException(file_path)
    return dataset


def import_taxonomy_tree(file_path):
    file_name, file_ext = os.path.splitext(file_path)
    if file_ext == JSON_EXT:
        return import_json_taxonomy_tree(file_path)
    raise UnsupportedFileTypeException(file_path)


def import_json_taxonomy_tree(file_path):
    taxo_tree = {}
    try:
        with open(file_path) as json_file:
            taxo_tree = json.load(json_file)
    except IOError:
        raise OpenFileException(file_path)
    return taxo_tree
