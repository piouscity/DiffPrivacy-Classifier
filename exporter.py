import os, csv
from exceptions import OpenFileException, UnsupportedFileTypeException


CSV_EXT = ".csv"


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
