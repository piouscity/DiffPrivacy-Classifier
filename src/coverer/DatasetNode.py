import logging
import math
import numpy
from typing import List, Iterator

from settings import CLASS_ATTRIBUTE, LOG_NOISE_LEN
from src.utility import RecordCounter


class DatasetNode:
    def __init__(self, dataset:List[dict]=None):
        self.represent = {}
        self.childs = []
        self.counter = None
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
        self.counter = None

    def insert_represent_value(self, att, value):
        self.represent[att] = value

    def statistic(self, class_list:list) -> RecordCounter:
        if self.counter is None:
            self.counter = RecordCounter(class_list)
            for item in self.get_all_items():
                cls = item[CLASS_ATTRIBUTE]
                if not (cls in self.counter.count):
                    logging.warn(
                        "Classifying value %s not present in train dataset", 
                        cls
                        )
                self.counter.record(cls)
        return self.counter

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

    def predict_noise_impact(self, edp:float, class_list:list) -> float:
        if self.is_leaf():
            counter = self.statistic(class_list).count.copy()
            top_cls = max(counter, key=counter.get)
            for cls in counter:
                noise = numpy.random.laplace(scale=1/edp)
                cnt = counter[cls] + noise
                if cnt < 0:
                    cnt = 0
                else:
                    cnt = round(cnt)
                counter[cls] = cnt
            new_top_val = max(counter.values())
            return int(counter[top_cls] < new_top_val)
        leafs = self.get_all_leafs()
        sum_differ = 0
        items = 0
        for leaf in leafs:
            sum_differ += leaf.predict_noise_impact(edp, class_list)
            items += 1
        if items:
            sum_differ /= items
        return sum_differ

    def export_dataset(self, edp:float, class_list:list) -> List[dict]:
        noise_list = []
        ex_dataset = []
        leafs = self.get_all_leafs()
        for leaf in leafs:
            ex_item = leaf.represent.copy()
            counter = leaf.statistic(class_list)
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
