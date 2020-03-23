import logging
from typing import List, Tuple
from sklearn.model_selection import train_test_split

from src.validator import count_float_attribute
from settings import TRAIN_DATA_SIZE
from .CutCandidateSet import CutCandidateSet
from .DatasetNode import DatasetNode
from .ValueMapperSet import ValueMapperSet


def split_dataset(dataset):
    train_data, test_data = train_test_split(dataset, train_size=TRAIN_DATA_SIZE)
    return train_data, test_data


def generate_dp_dataset(
    dataset:List[dict], taxo_tree:dict, edp:float, steps:int
    ) -> Tuple[List[dict], ValueMapperSet, list]:
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
        cut_set.export_mapper_set(),
        cut_set.class_list
        )


def apply_generalization(
    dataset:List[dict], mapper_set:ValueMapperSet, class_list:list, edp:float
    ) -> List[dict]:
    data_root = DatasetNode(dataset)
    leaf_list = data_root.get_all_leafs()
    for att in mapper_set.get_attributes():
        mapper = mapper_set.get_mapper_by_att(att)
        new_leaf_list = []
        for data_node in leaf_list:
            child_record = {}
            for item in data_node.get_all_items():
                gen_value = mapper.get_general_value(item[att])
                if not gen_value in child_record:
                    new_child = DatasetNode()
                    new_child.insert_represent_value(att, gen_value)
                    data_node.insert_child(new_child)
                    child_record[gen_value] = new_child
                child_record[gen_value].insert_item(item)
            data_node.clean_up()
            new_leaf_list.extend(data_node.get_all_leafs())
        leaf_list = new_leaf_list
    return data_root.export_dataset(edp, class_list)
