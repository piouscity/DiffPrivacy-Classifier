import math, random, numpy

from validator import count_float_attribute
from settings import TAXO_ROOT, TAXO_NODE_NAME, TAXO_NODE_CHILD, TAXO_FROM, \
   TAXO_TO, CLASS_ATTRIBUTE, DIGIT
from utility import information_gain, exp_mechanism, RecordCounter


class TaxonomyValueMapper:
    parent_list = {}
    leaf_list = {}

    def __init__(self, node:dict):
        assert node[TAXO_NODE_CHILD]
        for child in node[TAXO_NODE_CHILD]:
            node_value = child[TAXO_NODE_NAME]
            leafs = self.__scan_tree(child)   
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
        if not self.parent_list[value]:
            return value
        return self.parent_list[value][-1]

    def specialize(self, value):
        for leaf_value in self.leaf_list[value]:
            # If value has leafs, then it is not a leaf
            self.parent_list[leaf_value].pop()
            new_parent = self.get_general_value(leaf_value)
            if new_parent != leaf_value: # leaf value still has parent
                if not new_parent in self.leaf_list:
                    self.leaf_list[new_parent] = []
                self.leaf_list[new_parent].append(leaf_value)
        self.leaf_list[value] = []


class TaxonomyValueMapperSet:
    mappers = {}
    def __init__(self, taxo_tree):
        for att in taxo_tree:
            if TAXO_ROOT in taxo_tree[att]: # Category attribute
                root = taxo_tree[att][TAXO_ROOT]
                self.mappers[att] = TaxonomyValueMapper(root)
                
    def get_mapper_by_att(self, att):
        return self.mappers[att]


class CutCandidate:
    def __init__(self, att):
        self.attribute = att
        self.data_nodes = []
        self.counter = None
        self.splittable = True
        self.child_counter = {}
        self.score = None
    
    def add_data_node(self, node, counter=None):
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

    def get_all_items(self):
        self.refresh_data_nodes()
        for node in self.data_nodes:
            for item in node.get_all_items():
                yield item

    def calculate_score(self):
        self.score = information_gain(self.counter, self.child_counter)

    def export_value(self):
        raise NotImplementedError()

    def transfer_value(self):
        self.refresh_data_nodes()
        value = self.export_value()
        for node in self.data_nodes:
            node.insert_represent_value(self.attribute, value)


class CategoryCutCandidate(CutCandidate):
    def __init__(self, att, taxo_node):
        super().__init__(att)
        self.node = taxo_node

    def export_value(self):
        return self.node[TAXO_NODE_NAME]

    def child_count(self, class_list, mapper):
        if not self.node[TAXO_NODE_CHILD]:
            self.splittable = False
            return
        value_counter = {
            node[TAXO_NODE_NAME]: RecordCounter(class_list)
            for node in self.node[TAXO_NODE_CHILD]
            }
        for item in self.get_all_items():
            value = item[self.attribute]
            general_value = mapper.get_general_value(value)
            value_counter[general_value].record(item[CLASS_ATTRIBUTE])
        self.child_counter = value_counter

    def specialize(self, mapper):
        child_candidates = []
        for taxo_child in self.node[TAXO_NODE_CHILD]:
            candidate = CategoryCutCandidate(self.attribute, taxo_child)
            candidate.counter = self.child_counter[taxo_child[TAXO_NODE_NAME]]
            child_candidates.append(candidate)
        self.refresh_data_nodes()
        data_node_record = {
            taxo_child[TAXO_NODE_NAME]: None
            for taxo_child in self.node[TAXO_NODE_CHILD]
            }
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
                    data_node_record[candidate.node[TAXO_NODE_NAME]]
                    )
        for taxo_child in self.node[TAXO_NODE_CHILD]:
            mapper.specialize(taxo_child[TAXO_NODE_NAME])
        return child_candidates


class IntervalCutCandidate(CutCandidate):
    def __init__(self, att, from_value, to_value):
        super().__init__(att)
        self.from_value = from_value
        self.to_value = to_value
        self.split_value = None

    def export_value(self):
        return "[{0},{1})".format(self.from_value, self.to_value)

    def find_split_value(self, class_list, sensi, edp):
        if not self.splittable:
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
        else:
            # Prepare weight
            if not self.from_value in value_counter:
                value_counter[self.from_value] = RecordCounter(class_list)
            value_counter[self.to_value] = RecordCounter(class_list)
            part_counter = {
                "left": RecordCounter(class_list),
                "right": RecordCounter(class_list),
                }
            for value in value_counter:
                part_counter["right"] += value_counter[value]
            sorted_values = sorted(value_counter.keys())
            weights = []
            intervals = []
            pre_value = sorted_values[0]
            # Weight calculation
            for value in sorted_values[1:]:
                part_counter["left"] += value_counter[pre_value]
                part_counter["right"] -= value_counter[pre_value]
                intervals.append((pre_value, value))
                score = information_gain(self.counter, part_counter)
                w = exp_mechanism(edp, sensi, score)\
                    * (value-pre_value)
                weights.append(w)          
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
            # Re-count
            self.split_value = split_value
            self.child_counter = {
                "left": RecordCounter(class_list),
                "right": RecordCounter(class_list),
                }
            for value in sorted_values:
                if value < self.split_value:
                    self.child_counter["left"] += value_counter[value]
                else:
                    self.child_counter["right"] += value_counter[value]

    def specialize(self):
        child_candidates = []
        interval = {
            "left": (self.from_value, self.split_value),
            "right": (self.split_value, self.to_value)
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
        return child_candidates


class CutCandidateSet:
    unsplittable_list = []
    candidate_list = []
    new_float_cands = []
    new_category_cands = []

    def __init__(self, taxo_tree, root):
        self.mapper_set = TaxonomyValueMapperSet(taxo_tree)
        general_count = RecordCounter()
        for item in dataset:
            general_count.record(item[CLASS_ATTRIBUTE])
        self.class_list = list(general_count.count.keys())
        self.sensi = math.log2(len(self.class_list))
        for att in taxo_tree:
            taxo_att = taxo_tree[att]
            if TAXO_ROOT in taxo_att: # Category attribute
                candidate = CategoryCutCandidate(
                    att, 
                    taxo_att[TAXO_ROOT]
                    )
                self.new_category_cands.append(candidate)
            else:   # Float attribute
                candidate = IntervalCutCandidate(
                    att,
                    taxo_att[TAXO_FROM], 
                    taxo_att[TAXO_TO]
                    )
                self.new_float_cands.append(candidate)
            candidate.add_data_node(root, general_count)
        self.category_count_childs()

    def determine_new_splits(self, edp):
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
                self.candidate_list.append(candidate)
            else:
                self.unsplittable_list.append(candidate)
        self.new_category_cands = []
        self.new_float_cands = []
    
    def get_score_list(self):
        for candidate in self.candidate_list:
            yield candidate.score

    def select_candidate(self, edp):
        if not self.candidate_list:
            return -1
        weights = [
            exp_mechanism(edp, self.sensi, score) 
            for score in self.get_score_list()
            ]
        chosen_index = random.choices(
            list(range(len(weights))), 
            weights=weights
            )[0]
        return chosen_index

    def specialize_candidate(self, index):
        chosen_candidate = self.candidate_list[index]
        if index < len(self.candidate_list)-1:  # Not the last
            self.candidate_list[index] = self.candidate_list.pop()
        else:   # Is the last
            self.candidate_list.pop()
        if isinstance(chosen_candidate, CategoryCutCandidate):
            child_candidates = chosen_candidate.specialize(
                self.mapper_set.get_mapper_by_att(chosen_candidate.attribute)
                )
            self.new_category_cands.extend(child_candidates)
            self.category_count_childs()
        else:
            child_candidates = chosen_candidate.specialize()
            self.new_float_cands.extend(child_candidates)

    def transfer_candidate_values(self):
        for candidate in chain(self.candidate_list, self.unsplittable_list):
            candidate.transfer_value()


class DatasetNode:
    represent = {}
    def __init__(self, dataset=None):
        if not dataset:
            self.dataset = []
        else:
            assert isinstance(dataset, list)
            self.dataset = dataset
        self.childs = []

    def insert_item(self, item):
        self.dataset.append(item)

    def insert_child(self, child_node):
        self.childs.append(child_node)

    def clean_up(self):
        self.dataset = []

    def insert_represent_value(self, att, value):
        self.represent[att] = value

    def is_leaf(self):
        return not self.childs

    def get_all_leafs(self):
        if not self.childs:
            return self
        leafs = []
        for child in self.childs:
            leafs.extend(child.get_all_leafs())
        return leafs

    def get_all_items(self):
        for item in self.dataset:
            yield item

    def export_dataset(self, edp, class_list):
        ex_dataset = []
        leafs = self.get_all_leafs()
        for leaf in leafs:
            ex_item = self.represent.copy()
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
            

def generate_dp_dataset(dataset, taxo_tree, edp, steps):
    float_att_cnt = count_float_attribute(dataset)
    single_edp = edp / 2 / (float_att_cnt + 2*steps)
    data_root = DatasetNode(dataset)
    cut_set = CutCandidateSet(taxo_tree, data_root)
    cut_set.determine_new_splits(single_edp)
    cut_set.calculate_candidate_score()
    for i in range(steps):
        index = cut_set.select_candidate(single_edp)
        if index == -1:
            break
        cut_set.specialize_candidate(index)
        cut_set.determine_new_splits(single_edp)
        cut_set.calculate_candidate_score()
    cut_set.transfer_candidate_values()
    return data_root.export_dataset(edp/2, cut_set.class_list)
