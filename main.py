import traceback, logging
from sklearn.model_selection import train_test_split

from src.exceptions import BaseException
from src.validator import check_valid_taxonomy_tree
from src.file_handler import import_dataset, import_taxonomy_tree, export_dataset
from settings import DATASET_PATH, TAXO_TREE_PATH, EDP, STEPS, \
    IGNORE_CHECK, LOG_LEVEL, LOG_FILE, RECORD_TRAIN_PATH, RECORD_TEST_PATH, \
    TRAIN_DATA_SIZE
from src.coverer.routine import generate_dp_dataset, apply_generalization
from src.classifier.routine import calculate_classification_accuracy, \
    calculate_lower_bound_accuracy, extract_group_dataset

try:
    logging.basicConfig(filename=LOG_FILE, filemode='w',level=LOG_LEVEL)
    dataset = import_dataset(DATASET_PATH)
    taxo_tree = import_taxonomy_tree(TAXO_TREE_PATH)
    if not IGNORE_CHECK:
        check_valid_taxonomy_tree(taxo_tree, dataset)
    train_dataset, test_dataset = train_test_split(
        dataset, train_size=TRAIN_DATA_SIZE
        )
    private_train_dataset, mapper_set, class_list = generate_dp_dataset(
        train_dataset, taxo_tree, EDP, STEPS
        )
    private_test_dataset = apply_generalization(
        test_dataset, mapper_set, class_list, EDP/2
        )
    export_dataset(RECORD_TRAIN_PATH, private_train_dataset)
    export_dataset(RECORD_TEST_PATH, private_test_dataset)
    raw_accuracy = calculate_classification_accuracy(train_dataset, test_dataset)
    anonymized_accuracy = calculate_classification_accuracy(
        extract_group_dataset(private_train_dataset),
        extract_group_dataset(private_test_dataset))
    lower_bound_accuracy = calculate_lower_bound_accuracy(train_dataset, test_dataset)
    print("Baseline accuracy (BA): {} %".format(raw_accuracy * 100))
    print("Classification accuracy (CA): {} %".format(anonymized_accuracy * 100))
    print("Lower bound accuracy (LA): {} %".format(lower_bound_accuracy * 100))
    print("Cost quality: {} %".format((raw_accuracy-anonymized_accuracy) * 100))
    print("Benefit: {} %".format((anonymized_accuracy-lower_bound_accuracy) * 100))
except BaseException as e:
    print("{} - {}".format(e.code, e.detail))
except:
    print("Uncatched exception")
    traceback.print_exc()
