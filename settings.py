IGNORE_CHECK = False    # Only ignore if taxonomy tree is ensured to be valid

# Logging
import logging
LOG_LEVEL = logging.INFO
LOG_FILE = "logger/logging.txt"

# File paths
DATASET_PATH = "data/ds/adult-1000.csv"
TAXO_TREE_PATH = "data/taxos/adult.json"
RECORD_TRAIN_PATH = "data/export/adult-train.csv"
RECORD_TEST_PATH = "data/export/adult-test.csv"

# Dataset setting
CLASS_ATTRIBUTE = "class"
MISSING_VALUE = "?"
PERCENTAGE_SPLIT = 0.8

# Taxonomy tree setting
TAXO_FROM = "min"
TAXO_TO = "max"
TAXO_ROOT = "root"
TAXO_NODE_NAME = "value"
TAXO_NODE_CHILD = "childs"

# eps-DP setting
DIGIT = 0   # Rounding
EDP = 2
STEPS = 18
