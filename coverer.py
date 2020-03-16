import math, random, numpy, logging
from bisect import bisect
from typing import Iterator, List, Tuple

from validator import count_float_attribute
from settings import TAXO_ROOT, TAXO_NODE_NAME, TAXO_NODE_CHILD, TAXO_FROM, \
   TAXO_TO, CLASS_ATTRIBUTE, DIGIT
from utility import information_gain, exp_mechanism, RecordCounter


class CommonMapper:
    def get_general_value(self, value):
        raise NotImplementedError()

    def specialize(self, value):
        raise NotImplementedError()

    def clean_up(self):
        raise NotImplementedError()


class TaxonomyMapper(CommonMapper):
    parent_list = {}
    leaf_list = {}
    current_parent = {}
    exported = False

    def __init__(self, node:dict):
        assert node[TAXO_NODE_CHILD]
        root_value = node[TAXO_NODE_NAME]
        for child in node[TAXO_NODE_CHILD]:
            node_value = child[TAXO_NODE_NAME]
            leafs = self.__scan_tree(child)   
            logging.debug("Next parent of %s is %s", str(leafs), node_value)
            for leaf in leafs:
                self.current_parent[leaf] = root_value
            self.leaf_list[node_value] = leafs

    def __scan_tree(self, node:dict) -> list:
        node_value = node[TAXO_NODE_NAME]
        child_list = node[TAXO_NODE_CHILD]
        # Is a leaf
        if not child_list:   
            self.parent_list[node_value] = []
            return [node_value]
        # Not a leaf
        leafs = []
        for child in child_list:
            new_leafs = self.__scan_tree(child)
            leafs.extend(new_leafs)
        for leaf in leafs:
            self.parent_list[leaf].append(node_value)
        return leafs

    def get_general_value(self, value):
        if not self.exported:
            if not self.parent_list[value]:
                return value
            return self.parent_list[value][-1]
        return self.current_parent[value]

    def specialize(self, value):
        for leaf_value in self.leaf_list[value]:
            self.current_parent[leaf_value] = value
            # If value has leafs, then it is not a leaf
            self.parent_list[leaf_value].pop()
            new_parent = self.get_general_value(leaf_value)
            if new_parent != leaf_value: # leaf value still has parent
                if not new_parent in self.leaf_list:
                    self.leaf_list[new_parent] = []
                logging.debug(
                    "Next parent of %s is %s", 
                    leaf_value, new_parent
                    )
                self.leaf_list[new_parent].append(leaf_value)
        if not self.leaf_list[value]:   # Value is a leaf
            self.current_parent[value] = value
        else:
            self.leaf_list[value] = []

    def clean_up(self):
        self.exported = True
        self.parent_list = {}
        self.leaf_list = {}


class IntervalMapper(CommonMapper):
    split_values = []

    def __init__(self, from_value:float, to_value:float):
        self.split_values.append(from_value)
        self.split_values.append(to_value)

    def get_general_value(self, value:float) -> Tuple[float,float]:
        index = bisect(self.split_values, value)
        assert index > 0
        assert index < len(self.split_values)
        return (self.split_values[index-1], self.split_values[index])

    def specialize(self, value:float):
        self.split_values.append(value)

    def clean_up(self):
        self.split_values = sorted(self.split_values)


class ValueMapperSet:
    mappers = {}
    def __init__(self, taxo_tree:dict):
        for att in taxo_tree:
            if TAXO_ROOT in taxo_tree[att]: # Category attribute
                root = taxo_tree[att][TAXO_ROOT]
                self.mappers[att] = TaxonomyMapper(root)
            else: # Float attribute
                self.mapper[att] = IntervalMapper(
                    taxo_tree[att][TAXO_FROM], taxo_tree[att][TAXO_TO]
                    )
                
    def get_mapper_by_att(self, att) -> CommonMapper:
        return self.mappers[att]

    def clean_up(self):
        for att in self.mappers:
            mappers[att].clean_up()


class CutCandidate:
    data_nodes = []
    counter = None
    child_counter = {}
    splittable = True
    score = None

    def __init__(self, att):
        self.attribute = att
    
    def add_data_node(self, node:DatasetNode, counter:RecordCounter=None):
        self.data_nodes.append(node)
        if counter:
            if not self.counter:
                self.counter = counter
            else:
                self.counter = self.counter + counter

    def refresh_data_nodes(self):
        need_refresh = False
        for node in self.data_nodes:
            if not node.is_leaf():
                need_refresh = True
                break
        if not need_refresh:
            return
        new_nodes = []
        for node in self.data_nodes:
            if node.is_leaf():
                new_nodes.append(node)
            else:
                leafs = node.get_all_leafs()
                new_nodes.extend(leafs)
        self.data_nodes = new_nodes

    def get_all_items(self) -> Iterator[dict]:
        self.refresh_data_nodes()
        for node in self.data_nodes:
            for item in node.get_all_items():
                yield item

    def calculate_score(self):
        assert self.child_counter
        self.score = information_gain(self.counter, self.child_counter)

    def export_value(self):
        raise NotImplementedError()

    def transfer_value(self):
        self.refresh_data_nodes()
        value = self.export_value()
        for node in self.data_nodes:
            node.insert_represent_value(self.attribute, value)


class CategoryCutCandidate(CutCandidate):
    def __init__(self, att, taxo_node:dict):
        super().__init__(att)
        self.taxo_node = taxo_node

    def export_value(self):
        return self.taxo_node[TAXO_NODE_NAME]

    def child_count(self, class_list:list, mapper:TaxonomyMapper):
        logging.debug(
            "Couting child of %s, attribute %s", 
            self.export_value(), self.attribute
            )
        if not self.taxo_node[TAXO_NODE_CHILD]:
            self.splittable = False
            return
        value_counter = {
            node[TAXO_NODE_NAME]: RecordCounter(class_list)
            for node in self.taxo_node[TAXO_NODE_CHILD]
            }
        for item in self.get_all_items():
            value = item[self.attribute]
            general_value = mapper.get_general_value(value)
            value_counter[general_value].record(item[CLASS_ATTRIBUTE])
        self.child_counter = value_counter

    def specialize(self, mapper:TaxonomyMapper) \
        -> List[CategoryCutCandidate]:
        assert self.taxo_node[TAXO_NODE_CHILD]
        child_candidates = []
        data_node_record = {}
        for taxo_child in self.taxo_node[TAXO_NODE_CHILD]:
            child_value = taxo_child[TAXO_NODE_NAME]
            candidate = CategoryCutCandidate(self.attribute, taxo_child)
            candidate.counter = self.child_counter[child_value]
            child_candidates.append(candidate)
            data_node_record[child_value] = None
        self.refresh_data_nodes()
        for data_node in self.data_nodes:
            for value in data_node_record:
                new_node = DatasetNode()
                data_node.insert_child(new_node)
                data_node_record[value] = new_node
            for item in data_node.get_all_items():
                value = item[self.attribute]
                general_value = mapper.get_general_value(value)
                data_node_record[general_value].insert_item(item)
            data_node.clean_up()
            for candidate in child_candidates:
                candidate.add_data_node(
                    data_node_record[candidate.taxo_node[TAXO_NODE_NAME]]
                    )
        for taxo_child in self.taxo_node[TAXO_NODE_CHILD]:
            mapper.specialize(taxo_child[TAXO_NODE_NAME])
        return child_candidates


class IntervalCutCandidate(CutCandidate):
    split_value = None
    left = "left"
    right = "right"

    def __init__(self, att, from_value:float, to_value:float):
        super().__init__(att)
        self.from_value = from_value
        self.to_value = to_value

    def export_value(self) -> str:
        return "[{0},{1})".format(self.from_value, self.to_value)

    def find_split_value(self, class_list:list, sensi:float, edp:float):
        logging.debug(
            "Finding split value of %s, attribute %s", 
            self.export_value(), self.attribute
            )
        value_counter = {}
        # Count
        for item in self.get_all_items():
            value = item[self.attribute]
            if not (value in value_counter):
                value_counter[value] = RecordCounter(class_list)
            value_counter[value].record(item[CLASS_ATTRIBUTE])
        if not value_counter:
            self.splittable = False
            return
        # Prepare weight
        if not self.from_value in value_counter:
            value_counter[self.from_value] = RecordCounter(class_list)
        value_counter[self.to_value] = RecordCounter(class_list)
        part_counter = {
            self.left: RecordCounter(class_list),
            self.right: RecordCounter(class_list),
            }
        for value in value_counter:
            part_counter[self.right] += value_counter[value]
        sorted_values = sorted(value_counter.keys())
        weights = []
        intervals = []
        pre_value = sorted_values[0]
        # Weight calculation
        for value in sorted_values[1:]:
            part_counter[self.left] += value_counter[pre_value]
            part_counter[self.right] -= value_counter[pre_value]
            intervals.append((pre_value, value))
            score = information_gain(self.counter, part_counter)
            w = exp_mechanism(edp, sensi, score)\
                * (value-pre_value)
            weights.append(w)  
        logging.info("List of splitting intervals: %s", str(intervals))
        logging.info("List of corresponding weights: %s", str(weights))
        # Exp choose
        interval = random.choices(intervals, weights=weights)[0]
        while True:
            split_value = random.uniform(interval[0], interval[1])
            split_value = round(split_value, DIGIT)
            if split_value > interval[1]:
                split_value = interval[1]
            if (split_value > interval[0]) \
                and (split_value != self.to_value):  # Okay
                break
        logging.info("Split value is %f", split_value)
        # Re-count
        self.split_value = split_value
        self.child_counter = {
            self.left: RecordCounter(class_list),
            self.right: RecordCounter(class_list),
            }
        for value in sorted_values:
            if value < self.split_value:
                self.child_counter[self.left] += value_counter[value]
            else:
                self.child_counter[self.right] += value_counter[value]

    def specialize(self, mapper:IntervalMapper) -> List[IntervalCutCandidate]:
        assert self.split_value
        child_candidates = []
        interval = {
            self.left: (self.from_value, self.split_value),
            self.right: (self.split_value, self.to_value)
            }
        for part in interval:
            candidate = IntervalCutCandidate(
                self.attribute, 
                interval[part][0],
                interval[part][1]
                )
            candidate.counter = self.child_counter[part]
            child_candidates.append(candidate)
        self.refresh_data_nodes()
        for data_node in self.data_nodes:
            left_node = DatasetNode()
            right_node = DatasetNode()
            data_node.insert_child(left_node)
            data_node.insert_child(right_node)
            for item in data_node.get_all_items():
                value = item[self.attribute]
                if value < self.split_value:
                    left_node.insert_item(item)
                else:
                    right_node.insert_item(item)
            data_node.clean_up()
            for candidate in child_candidates:
                if candidate.to_value == self.split_value:
                    candidate.add_data_node(left_node)
                else:
                    candidate.add_data_node(right_node)
        mapper.specialize(self.split_value)
        return child_candidates


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


class DatasetNode:
    represent = {}
    childs = []

    def __init__(self, dataset:List[dict]=None):
        if not dataset:
            self.dataset = []
        else:
            assert isinstance(dataset, list)
            self.dataset = dataset

    def insert_item(self, item:dict):
        self.dataset.append(item)

    def insert_child(self, child_node:DatasetNode):
        self.childs.append(child_node)

    def clean_up(self):
        self.dataset = []

    def insert_represent_value(self, att, value):
        self.represent[att] = value

    def is_leaf(self) -> bool:
        return not self.childs

    def get_all_leafs(self) -> List[DatasetNode]:
        if not self.childs:
            return [self]
        leafs = []
        for child in self.childs:
            leafs.extend(child.get_all_leafs())
        return leafs

    def get_all_items(self) -> Iterator[dict]:
        for item in self.dataset:
            yield item

    def export_dataset(self, edp:float, class_list:list) -> List[dict]:
        ex_dataset = []
        leafs = self.get_all_leafs()
        for leaf in leafs:
            ex_item = leaf.represent.copy()
            counter = RecordCounter(class_list)
            for item in leaf.get_all_items():
                counter.record(item[CLASS_ATTRIBUTE])
            for cls in counter.count:
                cnt = counter.count[cls]
                cnt += numpy.random.laplace(scale=1/edp)
                if cnt < 0:
                    cnt = 0
                else:
                    cnt = round(cnt)
                header = "{att}:{val}".format(att=CLASS_ATTRIBUTE, val=cls)
                ex_item[header] = cnt
            ex_dataset.append(ex_item)
        return ex_dataset
            

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
