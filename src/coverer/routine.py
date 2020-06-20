import logging
import math
import numpy
from typing import List, Tuple

from settings import ALPHA, MIN_ENSURE, LOG_NOISE_ROW, JUMP, SEED, BUDGET_SPLIT
from src.validator import count_float_attribute
from .CutCandidateSet import CutCandidateSet
from .DatasetNode import DatasetNode
from .ValueMapperSet import ValueMapperSet


def determine_max_steps(dataset, edp, full_budget):
    len_data = round(len(dataset) + numpy.random.laplace(scale=1/edp))
    return round(math.log(len_data*full_budget*BUDGET_SPLIT/(2*math.sqrt(2))))


def generate_dp_dataset_auto_steps(
    dataset:List[dict], taxo_tree:dict, edp:float
    ) -> Tuple[List[dict], ValueMapperSet, list]:
    logging.info("Running diffgen with auto steps")
    assert SEED < 1
    budget = edp
    steps = determine_max_steps(dataset, edp*SEED, budget)
    budget -= edp*SEED
    logging.info("Top steps is %d", steps)
    float_att_cnt = count_float_attribute(dataset)
    edp_s = (budget - (budget*BUDGET_SPLIT)) / (float_att_cnt + 2*steps + (steps-1)//JUMP)
    logging.debug("edp' =  %f", edp_s)
    data_root = DatasetNode(dataset)
    cut_set = CutCandidateSet(taxo_tree, data_root)
    cut_set.determine_new_splits(edp_s)
    budget -= edp_s * float_att_cnt
    cut_set.calculate_candidate_score()
    for i in range(steps):
        logging.debug("Specializing, step %d", i+1)
        index = cut_set.select_candidate(edp_s)
        budget -= edp_s
        if index < 0:
            logging.warn("No more candidate to specialize. Step %d", i+1)
            break
        logging.info("Chosen candidate index: %d", index)
        cut_set.specialize_candidate(index)
        if (i+1 < steps) and ((i+1)%JUMP == 0):
            budget -= edp_s
            if data_root.should_stop(
                edp_s, math.sqrt(2)/budget, cut_set.class_list
                ):
                logging.info("Specialization stop at step %d", i+1)
                break
        affects = cut_set.determine_new_splits(edp_s)
        if affects:
            budget -= edp_s
        cut_set.calculate_candidate_score()
    cut_set.transfer_candidate_values()
    logging.info("@@@@@@@@@@@@@@@    Budget left of {}: {}".format(edp, budget))
    return (
        data_root.export_dataset(budget, cut_set.class_list),
        cut_set.export_mapper_set(),
        cut_set.class_list
        )


def generate_dp_dataset(
    dataset:List[dict], taxo_tree:dict, edp:float, steps:int
    ) -> Tuple[List[dict], ValueMapperSet, list]:
    logging.info("Running the original diffgen")
    float_att_cnt = count_float_attribute(dataset)
    edp_s = edp / 2 / (float_att_cnt + 2*steps)
    logging.debug("edp' =  %f", edp_s)
    data_root = DatasetNode(dataset)
    cut_set = CutCandidateSet(taxo_tree, data_root)
    cut_set.determine_new_splits(edp_s)
    cut_set.calculate_candidate_score()
    for i in range(steps):
        logging.debug("Specializing, step %d", i+1)
        index = cut_set.select_candidate(edp_s)
        if index < 0:
            logging.warn("No more candidate to specialize. Step %d", i+1)
            break
        logging.info("Chosen candidate index: %d", index)
        cut_set.specialize_candidate(index)
        cut_set.determine_new_splits(edp_s)
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


def generate_dp_matrix(org_matrix:numpy.array, new_dim:int, edp:float) \
    -> numpy.array:
    org_rows, org_dim = org_matrix.shape     
    projection = numpy.random.normal(       # d x k
        scale=1/math.sqrt(new_dim), size=(org_dim, new_dim)
        )
    logging.info("Projection matrix: \n%s", projection)
    reduced_matrix = org_matrix.dot(projection)     # n x k
    t_param = math.sqrt(ALPHA*2/new_dim*math.log(2*new_dim/(1-MIN_ENSURE)))
    c_param = new_dim * t_param
    logging.info("Param t = %f", t_param)
    logging.debug("Param c = %f", c_param)
    noise_matrix = numpy.random.laplace(            # n x k
        scale=c_param/edp, size=(org_rows, new_dim)
        )
    logging.info(
        "First rows of noise matrix: \n%s", 
        noise_matrix[:LOG_NOISE_ROW]
        )
    res_matrix = reduced_matrix + noise_matrix
    return res_matrix
