from exceptions import TaxoTreeMissingAttributeException, \
    DatasetMissingAttributeException, DatasetAttributeHasNoValueException, \
    TaxoTreeFloatAtttributeException, TaxoTreeCategoryAttributeException
from settings import MISSING_VALUE, TAXO_FROM, TAXO_TO, TAXO_ROOT


def check_float_attribute(dataset, attribute):
    for item in dataset:
        if attribute not in item:
            raise DatasetMissingAttributeException(attribute)
        if item[attribute] == MISSING_VALUE:
            continue
        return isinstance(item[attribute], float)
    raise DatasetAttributeHasNoValueException(attribute)


def check_valid_taxonomy_tree(taxo_tree, dataset):
    if len(dataset) < 1:
        return
    sample = dataset[0]
    for attribute in sample:
        if attribute not in taxo_tree:
            raise TaxoTreeMissingAttributeException(attribute)
        is_float_attribute = check_float_attribute(dataset, attribute)
        if is_float_attribute:
            if (TAXO_FROM not in taxo_tree[attribute]) or \
                (TAXO_TO not in taxo_tree[attribute]):
                raise TaxoTreeFloatAtttributeException(attribute)
        else:   # Category attribute
            if TAXO_ROOT not in taxo_tree[attribute]:
                raise TaxoTreeCategoryAttributeException(attribute)
