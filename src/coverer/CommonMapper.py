import logging
from typing import Tuple
from bisect import bisect

from settings import TAXO_NODE_NAME, TAXO_NODE_CHILD


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

