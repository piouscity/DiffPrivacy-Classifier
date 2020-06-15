import logging
import math

from settings import DATASET_PATH, TAXO_TREE_PATH, EDP, LOG_FILE, LOG_LEVEL
from src.file_handler import import_dataset, import_taxonomy_tree
from src.coverer.DatasetNode import DatasetNode
from src.coverer.CutCandidateSet import CutCandidateSet


MAX_STEP = 16
SQ2 = math.sqrt(2)

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
    impact = data_root.predict_noise_impact(EDP/2*SQ2, cut_set.class_list)
    print("Level {0}, noise impact is {1}".format(i+1, impact))
    cut_set.determine_new_splits(None)
    cut_set.calculate_candidate_score()
