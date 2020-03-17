from settings import TAXO_ROOT, TAXO_FROM, TAXO_TO
from .CommonMapper import TaxonomyMapper, IntervalMapper, CommonMapper


class ValueMapperSet:
    mappers = {}
    def __init__(self, taxo_tree:dict):
        for att in taxo_tree:
            if TAXO_ROOT in taxo_tree[att]: # Category attribute
                root = taxo_tree[att][TAXO_ROOT]
                self.mappers[att] = TaxonomyMapper(root)
            else: # Float attribute
                self.mapper[att] = IntervalMapper(
                    taxo_tree[att][TAXO_FROM], taxo_tree[att][TAXO_TO]
                    )
                
    def get_mapper_by_att(self, att) -> CommonMapper:
        return self.mappers[att]

    def clean_up(self):
        for att in self.mappers:
            mappers[att].clean_up()

