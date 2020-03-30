IGNORE_CHECK = False    # Only ignore if taxonomy tree is ensured to be valid

# Logging
import logging
LOG_LEVEL = logging.INFO
LOG_FILE = "logger/logging.txt"

# File paths
DATASET_PATH = "data/ds/adult.csv"
TAXO_TREE_PATH = "data/taxos/adult.json"
RECORD_TRAIN_PATH = "data/export/adult-train.csv"
RECORD_TEST_PATH = "data/export/adult-test.csv"

# Dataset setting
CLASS_ATTRIBUTE = "class"
MISSING_VALUE = "?"
TRAIN_DATA_SIZE = 0.8

# Taxonomy tree setting
TAXO_FROM = "min"
TAXO_TO = "max"
TAXO_ROOT = "root"
TAXO_NODE_NAME = "value"
TAXO_NODE_CHILD = "childs"

# Utility function settting
from src.utility import information_gain, max_func
UTILITY_FUNCTION = information_gain

# eps-DP setting
DIGIT = 0   # Rounding
EDP = 2
STEPS = 16

# classification setting
PRUNING_RATE = 0.8
