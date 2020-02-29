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


class CategoryCutCandidate:
    def __init__(self, taxo_node):
        self.node = taxo_node


class IntervalCutCandidate:
    def __init__(self, from_value, to_value):
        self.from_value = from_value
        self.to_value = to_value


class CutCandidateSet:
    cut_list = []

    def __init__(self, taxo_tree):
        for att in taxo_tree:
            taxo_att = taxo_tree[att]
            if TAXO_ROOT in taxo_att: # Category attribute
                self.cut_list.append(CategoryCutCandidate(taxo_att[TAXO_ROOT]))
            else:   # Float attribute
                self.cut_list.append(IntervalCutCandidate(
                    taxo_att[TAXO_FROM], 
                    taxo_att[TAXO_TO]
                    ))


class DatasetTree:
    def __init__(self, dataset):
        self.tree = dataset


def generate_dp_dataset(dataset, taxo_tree, edp, steps):
    float_att_cnt = count_float_attribute(dataset)
    single_edp = edp / 2 / (float_att_cnt + 2*steps)

