from validator import count_float_attribute
from settings import TAXO_ROOT, TAXO_NODE_NAME, TAXO_NODE_CHILD, TAXO_FROM, \
   TAXO_TO


class TaxonomyValueMapper:
    parent_list = {}
    leaf_list = {}

    def __init__(self, node):
        node_value = node[TAXO_NODE_NAME]
        leafs = self.__scan_tree(att, node)   
        self.leaf_list[node_value] = leafs

    def __scan_tree(self, node):
        node_value = node[TAXO_NODE_NAME]
        child_list = node[TAXO_NODE_CHILD]
        if not child_list:   # Is a leaf
            self.parent_list[node_value] = []
            return [node_value]
        leafs = []
        for child in child_list:
            new_leafs = self.__scan_tree(att, child)
            leafs.extend(new_leafs)
        for leaf in leafs:
            self.parent_list[leaf].append(node_value)
        return leafs


class TaxonomyValueMapperSet:
    mappers = {}
    def __init__(self, taxo_tree):
        for att in taxo_tree:
            if TAXO_ROOT in taxo_tree[att]: # Category attribute
                root = taxo_tree[att][TAXO_ROOT]
                self.mappers[att] = TaxonomyValueMapper(root)    


class RecordCounter:
    def __init__(self, class_list):
        self.count_all = 0
        self.count = {
            cls: 0
            for cls in class_list
            }
    
    def record(self, cls):
        self.count_all += 1
        self.count[cls] += 1

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
    
    def add_data_node(self, node):
        self.data_nodes.append(node)

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


class IntervalCutCandidate(CutCandidate):
    def __init__(self, att, from_value, to_value):
        super().__init__(att)
        self.from_value = from_value
        self.to_value = to_value
        self.existing_values = None


class CutCandidateSet:
    candidate_list = []
    new_float_candidates = []

    def __init__(self, taxo_tree):
        for att in taxo_tree:
            taxo_att = taxo_tree[att]
            if TAXO_ROOT in taxo_att: # Category attribute
                self.candidate_list.append(CategoryCutCandidate(
                    att, 
                    taxo_att[TAXO_ROOT]
                    ))
            else:   # Float attribute
                float_candidate = IntervalCutCandidate(
                    att,
                    taxo_att[TAXO_FROM], 
                    taxo_att[TAXO_TO]
                    )
                self.candidate_list.append(float_candidate)
                self.new_float_candidates.append(float_candidate)

    def pop_new_float_candidates(self):
        result = self.new_float_candidates
        self.new_float_candidates = []
        return result


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
        self.mapper_set = TaxonomyValueMapperSet(taxo_tree)
        self.cut_set = CutCandidateSet(taxo_tree)
        for candidate in self.cut_set:
            candidate.add_data_node(self.root)

    def determine_new_splits(self, edp):
        for candidate in self.cut_set.pop_new_float_candidates():
            if candidate.existing_values is None:
                values = []
                att = candidate.attribute
                for item in candidate.get_all_items():
                    values.append(item[att])
                candidate.existing_values = sorted(set(values))



def generate_dp_dataset(dataset, taxo_tree, edp, steps):
    float_att_cnt = count_float_attribute(dataset)
    single_edp = edp / 2 / (float_att_cnt + 2*steps)
    data_tree = DatasetTree(dataset)

