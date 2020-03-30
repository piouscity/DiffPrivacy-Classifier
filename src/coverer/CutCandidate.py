import logging, random, math
from typing import Iterator, List

from settings import TAXO_NODE_NAME, TAXO_NODE_CHILD, CLASS_ATTRIBUTE, DIGIT, \
    UTILITY_FUNCTION
from .CommonMapper import TaxonomyMapper, IntervalMapper
from .DatasetNode import DatasetNode
from src.utility import RecordCounter, exp_mechanism, interval_to_str


SMALLEST_SEG = math.pow(10, DIGIT)


class CutCandidate:
    def __init__(self, att):
        self.attribute = att
        self.data_nodes = []
        self.counter = None
        self.child_counter = {}
        self.splittable = True
        self.score = None
    
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
        self.score = UTILITY_FUNCTION(self.counter, self.child_counter)

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
        -> List['CategoryCutCandidate']:
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
    LEFT = "left"
    RIGHT = "right"

    def __init__(self, att, from_value:float, to_value:float):
        super().__init__(att)
        self.from_value = from_value
        self.to_value = to_value
        self.split_value = None

    def export_value(self) -> str:
        return interval_to_str(self.from_value, self.to_value)

    def find_split_value(self, class_list:list, sensi:float, edp:float):
        logging.debug(
            "Finding split value of %s, attribute %s", 
            self.export_value(), self.attribute
            )
        if self.to_value - self.from_value <= SMALLEST_SEG:
            self.splittable = False
            return
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
            self.LEFT: RecordCounter(class_list),
            self.RIGHT: RecordCounter(class_list),
            }
        for value in value_counter:
            part_counter[self.RIGHT] += value_counter[value]
        sorted_values = sorted(value_counter.keys())
        weights = []
        intervals = []
        pre_value = sorted_values[0]
        # Weight calculation
        for value in sorted_values[1:]:
            part_counter[self.LEFT] += value_counter[pre_value]
            part_counter[self.RIGHT] -= value_counter[pre_value]
            intervals.append((pre_value, value))
            score = UTILITY_FUNCTION(self.counter, part_counter)
            w = exp_mechanism(edp, sensi, score)\
                * (value-pre_value)
            weights.append(w)
            pre_value = value
        logging.info("List of splitting intervals: %s", str(intervals))
        logging.info("List of corresponding weights: %s", str(weights))
        # Exp choose
        while True:
            interval = random.choices(intervals, weights=weights)[0]
            if (interval != intervals[-1]) \
                or (interval[1]-interval[0] > SMALLEST_SEG):   # Okay
                break
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
            self.LEFT: RecordCounter(class_list),
            self.RIGHT: RecordCounter(class_list),
            }
        for value in sorted_values:
            if value < self.split_value:
                self.child_counter[self.LEFT] += value_counter[value]
            else:
                self.child_counter[self.RIGHT] += value_counter[value]

    def specialize(self, mapper:IntervalMapper) \
        -> List['IntervalCutCandidate']:
        assert self.split_value
        child_candidates = []
        interval = {
            self.LEFT: (self.from_value, self.split_value),
            self.RIGHT: (self.split_value, self.to_value)
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
