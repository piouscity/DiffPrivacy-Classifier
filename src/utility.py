import math
from typing import Dict, Any


class RecordCounter:
    def __init__(self, class_list:list = None):
        self.count_all = 0
        if class_list:
            self.count = {
                cls: 0
                for cls in class_list
                }
        else:
            self.count = {}
    
    def record(self, cls):
        assert not (cls is None)
        self.count_all += 1
        if cls in self.count:
            self.count[cls] += 1
        else:
            self.count[cls] = 1

    def get_most_frequent_class(self):
        result = None
        for cls in self.count:
            if (result is None) or (self.count[cls] > self.count[result]):
                result = cls
        return result

    def get_max_frequency(self):
        cls = self.get_most_frequent_class()
        return self.count.get(cls, 0)

    def __add__(self, other:'RecordCounter') -> 'RecordCounter':
        result = RecordCounter()
        result.count_all = self.count_all + other.count_all
        result.count = {
            cls: self.count[cls] + other.count[cls]
            for cls in self.count
            }
        return result

    def __sub__(self, other:'RecordCounter') -> 'RecordCounter':
        result = RecordCounter()
        result.count_all = self.count_all - other.count_all
        result.count = {
            cls: self.count[cls] - other.count[cls]
            for cls in self.count
            }
        return result


def entropy(value: RecordCounter) -> float:
    assert value.count_all != 0
    result = 0
    for cls in value.count:
        prop = value.count[cls] / value.count_all
        if prop == 0:
            continue
        result -= prop*math.log2(prop)
    return result


def information_gain(value: RecordCounter, child: Dict[Any, RecordCounter]) \
    -> float:
    if value.count_all == 0:
        return 0
    result = entropy(value)
    for c_val in child:
        if child[c_val].count_all == 0:
            continue
        result -= child[c_val].count_all / value.count_all \
            * entropy(child[c_val])
    return result


def max_gain(value: RecordCounter, child: Dict[Any, RecordCounter]) -> float:
    result = 0
    for c_val in child:
        max_frequency = child[c_val].get_max_frequency()
        result += max_frequency
    return result


def exp_mechanism(edp:float, sensi:float, score:float) -> float:
    assert sensi != 0
    return math.exp(edp/(2*sensi)*score)


def interval_to_str(from_value:float, to_value:float) -> str:
    return "[{0},{1})".format(from_value, to_value)
