from exceptions import TaxoTreeMissingAttributeException, \
    DatasetMissingAttributeException, DatasetAttributeMissingValueException, \
    TaxoTreeFloatAtttributeMissingRootException, \
    TaxoTreeCategoryAttributeMissingRootException, \
    TaxoTreeFloatAtttributeRootException, \
    TaxoTreeCategoryAttributeRootException
from settings import MISSING_VALUE, TAXO_FROM, TAXO_TO, TAXO_ROOT


def check_float_attribute(dataset, attribute):
    for item in dataset:
        if attribute not in item:
            raise DatasetMissingAttributeException(attribute)
        if item[attribute] == MISSING_VALUE:
            continue
        return isinstance(item[attribute], float)
    raise DatasetAttributeMissingValueException(attribute)


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
            if not att_root:
                raise TaxoTreeCategoryAttributeRootException(attribute)
