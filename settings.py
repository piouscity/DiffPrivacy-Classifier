IGNORE_CHECK = False    # Only ignore if input data is ensured to be valid

# Logging
import logging
LOG_LEVEL = logging.INFO
LOG_FILE = "logger/logging.txt"
LOG_NOISE_LEN = 32
LOG_NOISE_ROW = 5

# File paths
DATASET_PATH = "data/ds/adult-full.csv"
TAXO_TREE_PATH = "data/taxos/adult-full.json"
TRAIN_PATH = "data/export/adult-train.csv"
TEST_PATH = "data/export/adult-test.csv"
COVERED_TRAIN_PATH = "data/export/covered-adult-train.csv"
COVERED_TEST_PATH = "data/export/covered-adult-test.csv"

MATRIX_PATH = "data/export/org-matrix.csv"
COVERED_MATRIX_PATH = "data/export/covered-matrix.csv"

# Dataset setting
CLASS_ATTRIBUTE = "class"
CLASS_COUNTER = "class_counter"
MISSING_VALUE = "?"
TRAIN_DATA_SIZE = 0.8

# Taxonomy tree setting
TAXO_FROM = "min"
TAXO_TO = "max"
TAXO_ROOT = "root"
TAXO_NODE_NAME = "value"
TAXO_NODE_CHILD = "childs"

# eps-DP setting
from src.utility import information_gain, max_gain
UTILITY_FUNCTION = information_gain
DIGIT = 0   # Rounding
EDP = 0.1
STEPS = 16

# Matrix release setting
SAMPLES = 2000
DEVIATION = 1
BOX = 2
ORG_DIM = 3
NEW_DIM = 2
ALPHA = 1
MIN_ENSURE = 0.85

# classification setting
PRUNING_RATE = 0.8
