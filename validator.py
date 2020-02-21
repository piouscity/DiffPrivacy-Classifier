from exceptions import TaxoTreeMissingAttributeException, \
    DatasetMissingAttributeException, DatasetAttributeMissingValueException, \
    TaxoTreeFloatAtttributeMissingRootException, TaxoNodeException, \
    TaxoTreeCategoryAttributeMissingRootException, \
    TaxoTreeFloatAtttributeRootException, TaxoNodeMissingKeyException
from settings import MISSING_VALUE, TAXO_FROM, TAXO_TO, TAXO_ROOT, \
    TAXO_NODE_NAME, TAXO_NODE_CHILD


PATH_SEP = "/"


def check_float_attribute(dataset, attribute):
    for item in dataset:
        if attribute not in item:
            raise DatasetMissingAttributeException(attribute)
        if item[attribute] == MISSING_VALUE:
            continue
        return isinstance(item[attribute], float)
    raise DatasetAttributeMissingValueException(attribute)


def check_valid_taxonomy_tree_node(node, trace_path):
    if not isinstance(node, dict):
        raise TaxoNodeException(trace_path)
    if TAXO_NODE_NAME not in node:
        raise TaxoNodeMissingKeyException(trace_path, TAXO_NODE_NAME)
    if (TAXO_NODE_CHILD not in node) or \
        (not isinstance(node[TAXO_NODE_CHILD], list)):
        raise TaxoNodeMissingKeyException(trace_path, TAXO_NODE_CHILD)
    new_trace_path = trace_path + node[TAXO_NODE_NAME] + PATH_SEP
    for child_node in node[TAXO_NODE_CHILD]:
        check_valid_taxonomy_tree_node(child_node, new_trace_path)


def check_valid_taxonomy_tree(taxo_tree, dataset):
    if len(dataset) < 1:
        return
    sample = dataset[0]
    for attribute in sample:
        if attribute not in taxo_tree:
            raise TaxoTreeMissingAttributeException(attribute)
        is_float_attribute = check_float_attribute(dataset, attribute)
        attribute_info = taxo_tree[attribute]
        if is_float_attribute:
            # Check if there is TAXO_FROM and TAXO_TO
            if (TAXO_FROM not in attribute_info) or \
                (TAXO_TO not in attribute_info):
                raise TaxoTreeFloatAtttributeMissingRootException(attribute)
            # Check if TAXO_FROM and TAXO_TO is valid
            att_from_value = attribute_info[TAXO_FROM]
            att_to_value = attribute_info[TAXO_TO]
            if (not isinstance(att_from_value, float)) or \
                (not isinstance(att_to_value, float)) or \
                (att_from_value >= att_to_value):
                raise TaxoTreeFloatAtttributeRootException(attribute)
        else:   # Category attribute
            if TAXO_ROOT not in attribute_info:
                raise TaxoTreeCategoryAttributeMissingRootException(attribute)
            att_root = attribute_info[TAXO_ROOT]
            trace_path = attribute + PATH_SEP
            check_valid_taxonomy_tree_node(att_root, trace_path)
