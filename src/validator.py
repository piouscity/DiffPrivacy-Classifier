from src.exceptions import TaxoTreeMissingAttributeException, \
    DatasetMissingAttributeException, DatasetAttributeMissingValueException, \
    TaxoTreeFloatAtttributeMissingRootException, TaxoNodeException, \
    TaxoTreeCategoryAttributeMissingRootException, TaxoTreeCoverageException, \
    TaxoTreeFloatAtttributeRootException, TaxoNodeMissingKeyException
from settings import MISSING_VALUE, TAXO_FROM, TAXO_TO, TAXO_ROOT, \
    TAXO_NODE_NAME, TAXO_NODE_CHILD, CLASS_ATTRIBUTE


PATH_SEP = "/"


def check_float_attribute(dataset, attribute):
    for item in dataset:
        if attribute not in item:
            raise DatasetMissingAttributeException(attribute)
        if item[attribute] == MISSING_VALUE:
            continue
        return isinstance(item[attribute], float)
    raise DatasetAttributeMissingValueException(attribute)


def count_float_attribute(dataset):
    res = 0
    for attribute in dataset[0]:
        if check_float_attribute(dataset, attribute):
            res += 1
    return res


def get_all_leaf_values(node, trace_path):
    if not isinstance(node, dict):
        raise TaxoNodeException(trace_path)
    if TAXO_NODE_NAME not in node:
        raise TaxoNodeMissingKeyException(trace_path, TAXO_NODE_NAME)
    if (TAXO_NODE_CHILD not in node) or \
        (not isinstance(node[TAXO_NODE_CHILD], list)):
        raise TaxoNodeMissingKeyException(trace_path, TAXO_NODE_CHILD)
    new_trace_path = trace_path + node[TAXO_NODE_NAME] + PATH_SEP
    result = []
    if not node[TAXO_NODE_CHILD]:  # Is leaf node
        result.append(node[TAXO_NODE_NAME])
    else: 
        for child_node in node[TAXO_NODE_CHILD]:
            result.extend(get_all_leaf_values(child_node, new_trace_path))
    return result


def check_valid_taxonomy_tree(taxo_tree, dataset):
    if len(dataset) < 1:
        return
    for attribute in dataset[0]:
        if attribute == CLASS_ATTRIBUTE:
            continue
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
            try:
                att_from_value = float(attribute_info[TAXO_FROM])
                att_to_value = float(attribute_info[TAXO_TO])
            except ValueError:
                raise TaxoTreeFloatAtttributeRootException(attribute)
            if att_from_value >= att_to_value:
                raise TaxoTreeFloatAtttributeRootException(attribute)
            # Integrity
            for item in dataset:
                item_att = item[attribute]
                if item_att == MISSING_VALUE:
                    continue
                if not (item_att>=att_from_value and item_att<att_to_value):
                    raise TaxoTreeCoverageException(attribute, item_att)
        else:   # Category attribute
            # Syntax
            if TAXO_ROOT not in attribute_info:
                raise TaxoTreeCategoryAttributeMissingRootException(attribute)
            att_root = attribute_info[TAXO_ROOT]
            trace_path = attribute + PATH_SEP
            leaf_values = get_all_leaf_values(att_root, trace_path)
            # Integrity
            leaf_value_record = {
                value: True
                for value in leaf_values
                }
            for item in dataset:
                item_att = item[attribute]
                if item_att == MISSING_VALUE:
                    continue
                if not leaf_value_record.get(item_att):
                    raise TaxoTreeCoverageException(attribute, item_att)
    redundant_atts = taxo_tree.keys() - dataset[0].keys()
    for att in redundant_atts:
        taxo_tree.pop(att)
