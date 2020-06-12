from settings import DATASET_PATH, TAXO_TREE_PATH


MAX_STEP = 16

dataset = import_dataset(DATASET_PATH)
taxo_tree = import_taxonomy_tree(TAXO_TREE_PATH)
for i in range(MAX_STEP):
    pass
