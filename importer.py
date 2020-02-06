import os, csv


def import_dataset(file_path):
    # file_name, file_ext = os.path.splitext(file_path)
    with open(file_path) as csv_file:
        dataset = [{key: float(value) for key, value in row.items()}
                   for row in csv.DictReader(csv_file, skipinitialspace=True)]

    return dataset


def import_taxonomy_tree(file_path):
    return {}
