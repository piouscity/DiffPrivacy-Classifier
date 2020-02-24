IGNORE_CHECK = False    # Only ignore if taxonomy tree is ensured to be valid

# File paths
DATASET_PATH = "datasets/adult-1000.csv"
TAXO_TREE_PATH = "taxonomy-trees/adult.json"
RECORD_PATH = "private_datasets/adult-1000.csv"

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
EDP = 2
STEPS = 54
