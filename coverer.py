import math, random

from validator import count_float_attribute
from settings import TAXO_ROOT, TAXO_NODE_NAME, TAXO_NODE_CHILD, TAXO_FROM, \
   TAXO_TO, CLASS_ATTRIBUTE, DIGIT
from utility import information_gain, exp_mechanism


class TaxonomyValueMapper:
    parent_list = {}
    leaf_list = {}

    def __init__(self, node):
        for child in node[TAXO_NODE_CHILD]:
            node_value = child[TAXO_NODE_NAME]
            leafs = self.__scan_tree(node)   
            self.leaf_list[node_value] = leafs

    def __scan_tree(self, node):
        node_value = node[TAXO_NODE_NAME]
        child_list = node[TAXO_NODE_CHILD]
        if not child_list:   # Is a leaf
            self.parent_list[node_value] = []
            return [node_value]
        leafs = []
        for child in child_list:
            new_leafs = self.__scan_tree(child)
            leafs.extend(new_leafs)
        for leaf in leafs:
            self.parent_list[leaf].append(node_value)
        return leafs

    def get_general_value(self, value):
        return self.parent_list[value][-1]


class TaxonomyValueMapperSet:
    mappers = {}
    def __init__(self, taxo_tree):
        for att in taxo_tree:
            if TAXO_ROOT in taxo_tree[att]: # Category attribute
                root = taxo_tree[att][TAXO_ROOT]
                self.mappers[att] = TaxonomyValueMapper(root)
                
    def get_mapper_by_att(self, att):
        return self.mappers[att]


class RecordCounter:
    def __init__(self, class_list=None):
        self.count_all = 0
        if class_list:
            self.count = {
                cls: 0
                for cls in class_list
                }
        else:
            self.count = {}
    
    def record(self, cls):
        self.count_all += 1
        if cls in self.count:
            self.count[cls] += 1
        else:
            self.count[cls] = 1

    def __add__(self, other):
        result = RecordCounter()
        result.count_all = self.count_all + other.count_all
        result.count = {
            cls: self.count[cls] + other.count[cls]
            for cls in self.count
            }
        return result

    def __sub__(self, other):
        result = RecordCounter()
        result.count_all = self.count_all - other.count_all
        result.count = {
            cls: self.count[cls] - other.count[cls]
            for cls in self.count
            }
        return result


class CutCandidate:
    def __init__(self, att):
        self.attribute = att
        self.data_nodes = []
        self.counter = None
        self.splittable = True
    
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


class CategoryCutCandidate(CutCandidate):
    def __init__(self, att, taxo_node):
        super().__init__(att)
        self.node = taxo_node

    def first_class_count(self, class_list, mapper):
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


class IntervalCutCandidate(CutCandidate):
    def __init__(self, att, from_value, to_value):
        super().__init__(att)
        self.from_value = from_value
        self.to_value = to_value
        self.split_value = None

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
        if len(value_counter <= 1):
            self.splittable = False
        else:
            # Prepare weight
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
                if split_value > interval[0]:  # Okay
                    break
            self.split_value = split_value
            self.left_count = RecordCounter(class_list)
            self.right_count = RecordCounter(class_list)
            for value in sorted_values:
                if value < self.split_value:
                    self.left_count = self.left_count + value_counter[value]
                else:
                    self.right_count = self.right_count + value_counter[value]


class CutCandidateSet:
    candidate_list = []
    new_float_candidates = []
    new_category_candidates = []

    def __init__(self, taxo_tree, class_list, root, general_count):
        self.sensi = math.log2(len(class_list))
        self.class_list = class_list
        for att in taxo_tree:
            taxo_att = taxo_tree[att]
            if TAXO_ROOT in taxo_att: # Category attribute
                candidate = CategoryCutCandidate(
                    att, 
                    taxo_att[TAXO_ROOT]
                    )
                self.new_category_candidates.append(candidate)
            else:   # Float attribute
                candidate = IntervalCutCandidate(
                    att,
                    taxo_att[TAXO_FROM], 
                    taxo_att[TAXO_TO]
                    )
                self.new_float_candidates.append(candidate)
            candidate.add_data_node(root, general_count)     

    def determine_new_splits(self, edp):
        for candidate in self.new_float_candidates:
            if (candidate.splittable) and (not candidate.split_value):
                candidate.find_split_value(self.class_list, self.sensi, edp)

    def category_first_class_count(self, mapper_set):
        for candidate in self.new_category_candidates:
            candidate.first_class_count(
                self.class_list, 
                mapper_set.get_mapper_by_att(candidate.attribute)
                )


class DatasetNode:
    def __init__(self, dataset):
        self.dataset = dataset
        self.childs = []

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


class DatasetTree:
    def __init__(self, dataset, taxo_tree):
        self.root = DatasetNode(dataset)
        general_count = RecordCounter()
        for item in dataset:
            general_count.record(item[CLASS_ATTRIBUTE])
        class_list = list(general_count.count.keys())
        self.mapper_set = TaxonomyValueMapperSet(taxo_tree)
        self.cut_set = CutCandidateSet(
            taxo_tree, 
            class_list, 
            self.root, 
            general_count
            )
        self.cut_set.category_first_class_count(self.mapper_set)

    def determine_new_splits(self, edp):
        self.cut_set.determine_new_splits(edp)
            

def generate_dp_dataset(dataset, taxo_tree, edp, steps):
    float_att_cnt = count_float_attribute(dataset)
    single_edp = edp / 2 / (float_att_cnt + 2*steps)
    data_tree = DatasetTree(dataset)

