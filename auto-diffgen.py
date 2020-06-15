import logging

from settings import DATASET_PATH, TAXO_TREE_PATH, EDP
from src.coverer.DatasetNode import DatasetNode


MAX_STEP = 16

logging.basicConfig(filename=LOG_FILE, filemode='w',level=LOG_LEVEL)
dataset = import_dataset(DATASET_PATH)
taxo_tree = import_taxonomy_tree(TAXO_TREE_PATH)

data_root = DatasetNode(dataset)
cut_set = CutCandidateSet(taxo_tree, data_root)
cut_set.determine_new_splits(None)
cut_set.calculate_candidate_score()
for i in range(MAX_STEP):
    index = cut_set.select_candidate(None)
    if index < 0:
        break
    cut_set.specialize_candidate(index)
    cut_set.determine_new_splits(None)
    cut_set.calculate_candidate_score()