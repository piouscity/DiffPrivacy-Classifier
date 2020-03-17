IGNORE_CHECK = False    # Only ignore if taxonomy tree is ensured to be valid

# Logging
import logging
LOG_LEVEL = logging.INFO
LOG_FILE = "logger/logging.txt"

# File paths
DATASET_PATH = "data/datasets/adult-1000.csv"
TAXO_TREE_PATH = "data/taxonomy-trees/adult.json"
RECORD_PATH = "data/private_datasets/adult-1000.csv"

# Dataset setting
CLASS_ATTRIBUTE = "class"
MISSING_VALUE = "?"

# Taxonomy tree setting
TAXO_FROM = "min"
TAXO_TO = "max"
TAXO_ROOT = "root"
TAXO_NODE_NAME = "value"
TAXO_NODE_CHILD = "childs"

# eps-DP setting
DIGIT = 2   # Rounding
EDP = 2
STEPS = 54
