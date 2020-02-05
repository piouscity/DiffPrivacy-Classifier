from exceptions import BaseException
from importer import import_dataset, import_taxonomy_tree
from exporter import export_dataset
from settings import DATASET_PATH, TAXO_TREE_PATH, RECORD_PATH, EDP, STEPS
from protecter import generate_dp_dataset

try:
    dataset = import_dataset(DATASET_PATH)
    taxo_tree = import_taxonomy_tree(TAXO_TREE_PATH)
    private_dataset, attribute_mapping = generate_dp_dataset(dataset, taxo_tree, EDP, STEPS)
    export_dataset(RECORD_PATH, private_dataset)
except BaseException as e:
    print("{}: {}".format(e.code, e.detail))
except:
    print("Uncatched exeption")

