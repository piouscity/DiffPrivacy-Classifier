import logging
import traceback

from settings import TAXO_TREE_PATH, EDP, STEPS, TRAIN_PATH, TEST_PATH, \
    IGNORE_CHECK, LOG_LEVEL, LOG_FILE, COVERED_TRAIN_PATH, COVERED_TEST_PATH
from src.classifier.routine import calculate_classification_accuracy, \
    calculate_lower_bound_accuracy, extract_group_dataset, print_accuracy_result
from src.coverer.routine import generate_dp_dataset, apply_generalization, \
    generate_dp_dataset_auto_steps
from src.exceptions import BaseException
from src.file_handler import import_dataset, import_taxonomy_tree, \
    export_dataset
from src.validator import check_valid_input_data


try:
    logging.basicConfig(filename=LOG_FILE, filemode='w',level=LOG_LEVEL)
    # Import and check
    print("Importing dataset...")
    train_dataset = import_dataset(TRAIN_PATH)
    test_dataset = import_dataset(TEST_PATH)
    taxo_tree = import_taxonomy_tree(TAXO_TREE_PATH)
    if not IGNORE_CHECK:
        check_valid_input_data(taxo_tree, train_dataset+test_dataset)
    # Anonymize
    print("Anonymizing dataset...")
    edps = [0.1, 0.25, 0.5, 1]
    steps = [0, 3, 4, 5, 6, 7, 8, 9, 10]
    for edp in edps:
        print("##########           e-DP: {}      ##### ".format(edp))
        for step in steps:
            total = 0
            print("##################           step: {}      ##### ".format(step))
            for i in range(10):
                private_train_dataset, mapper_set, class_list = generate_dp_dataset(
                    train_dataset, taxo_tree, edp, step
                    ) if step > 0 else generate_dp_dataset_auto_steps(
                        train_dataset, taxo_tree, edp
                        )
                private_test_dataset = apply_generalization(
                    test_dataset, mapper_set, class_list, edp
                    )
                #export_dataset(COVERED_TRAIN_PATH, private_train_dataset)
                #export_dataset(COVERED_TEST_PATH, private_test_dataset)
                # Classify
                #print("Classifying and calculating...")
                #raw_accuracy = calculate_classification_accuracy(
                #    extract_group_dataset(train_dataset),
                #    extract_group_dataset(test_dataset)
                #    )
                anonymized_accuracy = calculate_classification_accuracy(
                    extract_group_dataset(private_train_dataset),
                    extract_group_dataset(private_test_dataset)
                    )
                total += anonymized_accuracy
                print(anonymized_accuracy*100)
                #lower_bound_accuracy = calculate_lower_bound_accuracy(
                #    train_dataset, test_dataset
                #    )
                #print_accuracy_result(
                #    raw_accuracy, anonymized_accuracy, lower_bound_accuracy
                #    )
            print(total*10)
except BaseException as e:
    print("{} - {}".format(e.code, e.detail))
except:
    print("Uncatched exception")
    traceback.print_exc()
