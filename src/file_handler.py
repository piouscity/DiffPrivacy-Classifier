import csv
import json
import numpy
import os

from settings import MISSING_VALUE
from src.exceptions import OpenFileException, UnsupportedFileTypeException


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
                if MISSING_VALUE in row.values():
                    continue
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


def export_dataset(file_path, dataset):
    file_name, file_ext = os.path.splitext(file_path)
    if file_ext == CSV_EXT:
        return export_csv_dataset(file_path, dataset)
    raise UnsupportedFileTypeException(file_path)


def export_csv_dataset(file_path, dataset):
    attributes = tuple(dataset[0].keys())
    data_export = [attributes]
    for row in dataset:
        item = tuple(row[attribute] for attribute in attributes)
        data_export.append(item)
    try:
        with open(file_path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerows(data_export)
    except IOError:
        raise OpenFileException(file_path)


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


def import_csv_matrix(file_path) -> numpy.array:
    reader = csv.reader(open(file_path), delimiter=",")
    data = list(reader)
    return numpy.array([[float(item) for item in row] for row in data])


def import_matrix(file_path) -> numpy.array:
    file_name, file_ext = os.path.splitext(file_path)
    if file_ext == CSV_EXT:
        return import_csv_matrix(file_path)
    raise UnsupportedFileTypeException(file_path)


def export_csv_matrix(file_path, matrix:numpy.array, cluster:numpy.array):
    try:
        with open(file_path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            for i in range(matrix.shape[0]):
                row = matrix[i].tolist()
                row.append('c'+str(cluster[i]))
                csv_writer.writerow(row)
    except IOError:
        raise OpenFileException(file_path)


def export_matrix(file_path, matrix:numpy.array, cluster:numpy.array):
    file_name, file_ext = os.path.splitext(file_path)
    if file_ext == CSV_EXT:
        return export_csv_matrix(file_path, matrix, cluster)
    raise UnsupportedFileTypeException(file_path)
