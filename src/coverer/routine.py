import logging
from typing import List, Tuple

from src.validator import count_float_attribute
from .CutCandidateSet import CutCandidateSet
from .DatasetNode import DatasetNode
from .ValueMapperSet import ValueMapperSet
            

def generate_dp_dataset(
    dataset:List[dict], taxo_tree:dict, edp:float, steps:int
    ) -> Tuple[List[dict], ValueMapperSet]:
    float_att_cnt = count_float_attribute(dataset)
    single_edp = edp / 2 / (float_att_cnt + 2*steps)
    logging.debug("edp' =  %f", single_edp)
    data_root = DatasetNode(dataset)
    cut_set = CutCandidateSet(taxo_tree, data_root)
    cut_set.determine_new_splits(single_edp)
    cut_set.calculate_candidate_score()
    for i in range(steps):
        logging.debug("Specializing, step %d", i+1)
        index = cut_set.select_candidate(single_edp)
        if index == -1:
            logging.warn("No more candidate to specialize. Step %d", i+1)
            break
        logging.info("Chosen candidate index: %d", index)
        cut_set.specialize_candidate(index)
        cut_set.determine_new_splits(single_edp)
        cut_set.calculate_candidate_score()
    cut_set.transfer_candidate_values()
    return (
        data_root.export_dataset(edp/2, cut_set.class_list),
        cut_set.export_mapper_set()
        )
