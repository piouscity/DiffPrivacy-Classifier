import math, logging, random
from itertools import chain
from typing import Iterator

from settings import CLASS_ATTRIBUTE, TAXO_ROOT, TAXO_FROM, TAXO_TO
from .CutCandidate import CategoryCutCandidate, IntervalCutCandidate
from .DatasetNode import DatasetNode
from .ValueMapperSet import ValueMapperSet
from .utility import RecordCounter, exp_mechanism


class CutCandidateSet:
    unsplittable_list = []
    candidate_list = []
    new_float_cands = []
    new_category_cands = []

    def __init__(self, taxo_tree:dict, root:DatasetNode):
        self.mapper_set = ValueMapperSet(taxo_tree)
        # Class attribute scan
        general_count = RecordCounter()
        for item in root.get_all_items():
            general_count.record(item[CLASS_ATTRIBUTE])
        self.class_list = list(general_count.count.keys())
        self.sensi = math.log2(len(self.class_list))
        assert self.sensi > 0
        # Generate candidates
        for att in taxo_tree:
            att_taxo = taxo_tree[att]
            if TAXO_ROOT in att_taxo: # Category attribute
                candidate = CategoryCutCandidate(att, att_taxo[TAXO_ROOT])
                self.new_category_cands.append(candidate)
            else:   # Float attribute
                candidate = IntervalCutCandidate(
                    att, att_taxo[TAXO_FROM], att_taxo[TAXO_TO]
                    )
                self.new_float_cands.append(candidate)
            candidate.add_data_node(root, general_count)
        self.category_count_childs()

    def determine_new_splits(self, edp:float):
        for candidate in self.new_float_cands:
            if (candidate.splittable) and (not candidate.split_value):
                candidate.find_split_value(self.class_list, self.sensi, edp)

    def category_count_childs(self):
        for candidate in self.new_category_cands:
            if (candidate.splittable) and (not candidate.child_counter):
                candidate.child_count(
                    self.class_list, 
                    self.mapper_set.get_mapper_by_att(candidate.attribute)
                    )

    def calculate_candidate_score(self):
        for candidate in chain(self.new_category_cands, self.new_float_cands):
            if candidate.splittable:
                candidate.calculate_score()
                logging.debug(
                    "Score of candidate %s is %f", 
                    candidate.export_value(), candidate.score
                    )
                self.candidate_list.append(candidate)
            else:
                self.unsplittable_list.append(candidate)
        self.new_category_cands = []
        self.new_float_cands = []
    
    def get_score_list(self) -> Iterator[float]:
        for candidate in self.candidate_list:
            assert candidate.score
            yield candidate.score

    def select_candidate(self, edp:float) -> int:
        if not self.candidate_list:
            return -1
        weights = [
            exp_mechanism(edp, self.sensi, score) 
            for score in self.get_score_list()
            ]
        logging.info("Candidate weights: %s", str(weights))
        chosen_index = random.choices(
            list(range(len(weights))), 
            weights=weights
            )[0]
        return chosen_index

    def specialize_candidate(self, index:int):
        assert index >= 0
        assert index < len(self.candidate_list)
        chosen_candidate = self.candidate_list[index]
        logging.info(
            "Candidate %s is chosen to be specialize", 
            chosen_candidate.export_value()
            )
        if index < len(self.candidate_list)-1:  # Not the last
            self.candidate_list[index] = self.candidate_list.pop()
        else:   # Is the last
            self.candidate_list.pop()
        # Commit
        child_candidates = chosen_candidate.specialize(
            self.mapper_set.get_mapper_by_att(chosen_candidate.attribute)
            )
        if isinstance(chosen_candidate, CategoryCutCandidate):
            self.new_category_cands.extend(child_candidates)
            self.category_count_childs()
        else:
            self.new_float_cands.extend(child_candidates)
        logging.debug(
            "New candidates: %s", 
            str([candidate.export_value for candidate in child_candidates])
            )

    def transfer_candidate_values(self):
        for candidate in chain(self.candidate_list, self.unsplittable_list):
            candidate.transfer_value()

    def export_mapper_set(self) -> ValueMapperSet:
        self.mapper_set.clean_up()
        return self.mapper_set
