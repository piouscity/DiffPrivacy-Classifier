import traceback, logging

from src.exceptions import BaseException
from src.validator import check_valid_taxonomy_tree
from src.file_handler import import_dataset, import_taxonomy_tree, export_dataset
from settings import DATASET_PATH, TAXO_TREE_PATH, RECORD_PATH, EDP, STEPS, \
    IGNORE_CHECK, LOG_LEVEL, LOG_FILE
from src.coverer.routine import generate_dp_dataset

try:
    logging.basicConfig(filename=LOG_FILE, filemode='w',level=LOG_LEVEL)
    dataset = import_dataset(DATASET_PATH)
    taxo_tree = import_taxonomy_tree(TAXO_TREE_PATH)
    if not IGNORE_CHECK:
        check_valid_taxonomy_tree(taxo_tree, dataset)
    private_dataset, mapper_set, class_list = generate_dp_dataset(
        dataset, taxo_tree, EDP, STEPS
        )
    export_dataset(RECORD_PATH, private_dataset)
except BaseException as e:
    print("{} - {}".format(e.code, e.detail))
except:
    print("Uncatched exception")
    traceback.print_exc()


