import logging
import numpy
from typing import List, Iterator

from settings import CLASS_ATTRIBUTE, LOG_NOISE_LEN
from src.utility import RecordCounter


class DatasetNode:
    def __init__(self, dataset:List[dict]=None):
        self.represent = {}
        self.childs = []
        if not dataset:
            self.dataset = []
        else:
            assert isinstance(dataset, list)
            self.dataset = dataset

    def insert_item(self, item:dict):
        self.dataset.append(item)

    def insert_child(self, child_node:'DatasetNode'):
        child_node.represent.update(self.represent)
        self.childs.append(child_node)

    def clean_up(self):
        self.dataset = []
        self.represent = {}

    def insert_represent_value(self, att, value):
        self.represent[att] = value

    def is_leaf(self) -> bool:
        return not self.childs

    def get_all_leafs(self) -> List['DatasetNode']:
        if not self.childs:
            return [self]
        leafs = []
        for child in self.childs:
            leafs.extend(child.get_all_leafs())
        return leafs

    def get_all_items(self) -> Iterator[dict]:
        for item in self.dataset:
            yield item

    def export_dataset(self, edp:float, class_list:list) -> List[dict]:
        noise_list = []
        ex_dataset = []
        leafs = self.get_all_leafs()
        for leaf in leafs:
            ex_item = leaf.represent.copy()
            counter = RecordCounter(class_list)
            for item in leaf.get_all_items():
                cls = item[CLASS_ATTRIBUTE]
                if not (cls in counter.count):
                    logging.warn(
                        "Classifying value %s not present in train dataset", 
                        cls
                        )
                counter.record(cls)
            zero_case = True
            for cls in counter.count:
                noise = numpy.random.laplace(scale=1/edp)
                if len(noise_list) < LOG_NOISE_LEN:
                    noise_list.append(noise)
                cnt = counter.count[cls] + noise
                if cnt < 0:
                    cnt = 0
                else:
                    cnt = round(cnt)
                header = "{att}:{val}".format(att=CLASS_ATTRIBUTE, val=cls)
                if cnt != 0:
                    zero_case = False
                ex_item[header] = cnt
            if not zero_case:
                ex_dataset.append(ex_item)
        logging.info("Laplacian noises: %s ...", str(noise_list))
        return ex_dataset
