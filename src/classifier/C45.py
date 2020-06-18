import logging
from typing import List

from settings import CLASS_ATTRIBUTE, CLASS_COUNTER, PRUNING_RATE
from src.utility import RecordCounter, information_gain


class DecisionNode:
    def __init__(self, attribute, split_value, attr_value, decision):
        self.attribute = attribute
        self.split_value = split_value
        self.attr_value = attr_value
        self.decision = decision
        self.children = []


class C45:
    def __init__(self, dataset:List[dict]):
        self.data = dataset
        self.attributes = list(dataset[0].keys())
        self.attributes.remove(CLASS_ATTRIBUTE)
        self.attributes.remove(CLASS_COUNTER)
        self.attr_values = {
            attribute: set()
            for attribute in self.attributes
        }
        self.tree = None
        self.counter = None
        for row in dataset:
            for key, value in row.items():
                if not isinstance(value, float) and key != CLASS_ATTRIBUTE \
                        and key != CLASS_COUNTER:
                    self.attr_values[key].add(value)
        for attr in self.attributes:
            self.attr_values[attr] = list(self.attr_values[attr])

    def generate_decision_tree(self):
        self.tree = self.recursive_generate_tree(
            self.data, 
            self.attributes, 
            None,
            get_most_frequent_decision(self.data)
            )

    def find_split_attribute(self, cur_dataset, cur_attributes):
        selected_attr = None
        best_infogain = -float("inf")
        best_split_value = None
        split_data = []
        for attribute in cur_attributes:
            if not self.attr_values[attribute]:
                # float attribute
                cur_dataset = sorted(cur_dataset, key=lambda k: k[attribute])
                counter = RecordCounter()
                for item in cur_dataset:
                    counter.record(item[CLASS_ATTRIBUTE], item[CLASS_COUNTER])
                less_equal_counter = RecordCounter(list(counter.count.keys()))
                index = 0
                while index < len(cur_dataset)-1:
                    split_value = cur_dataset[index][attribute]
                    while index < len(cur_dataset) \
                        and cur_dataset[index][attribute] == split_value:
                        less_equal_counter.record(
                            cur_dataset[index][CLASS_ATTRIBUTE],
                            cur_dataset[index][CLASS_COUNTER]
                            )
                        index += 1
                    if index < len(cur_dataset):
                        greater_counter = counter - less_equal_counter
                        infogain_attr = information_gain(
                            counter, 
                            {
                                'left': less_equal_counter, 
                                'right': greater_counter
                            }
                        )
                        if infogain_attr > best_infogain:
                            best_infogain = infogain_attr
                            selected_attr = attribute
                            best_split_value = split_value
                less_equal = []
                greater = []
                if selected_attr == attribute:
                    for item in cur_dataset:
                        if item[attribute] <= best_split_value:
                            less_equal.append(item)
                        else:
                            greater.append(item)
                    split_data = [less_equal, greater]
            else:
                # category attribute
                infogain_attr, sub_data = self.calculate_infogain(
                    cur_dataset, attribute
                    )
                if infogain_attr > best_infogain:
                    selected_attr = attribute
                    best_infogain = infogain_attr
                    split_data = sub_data
                    best_split_value = None
        return selected_attr, split_data, best_split_value

    def recursive_generate_tree(
        self, cur_dataset, cur_attributes, cur_attr_value, 
        most_frequent_decision
        ):
        # current data is empty, return previous most frequent decision
        if len(cur_dataset) == 0:
            logging.info("Append decision ~: %s", most_frequent_decision)
            return DecisionNode(
                None, None, cur_attr_value, most_frequent_decision
                )
        # update most frequent decision
        most_frequent_decision = get_most_frequent_decision(cur_dataset)
        # current attributes is empty or all current attributes have the same values for all records
        # in current data, return current most frequent decision
        if len(cur_attributes) == 0 \
            or same_attribute_values(cur_dataset, cur_attributes):
            logging.info("Append decision: %s", most_frequent_decision)
            return DecisionNode(
                None, None, cur_attr_value, most_frequent_decision
                )
        decision = check_decision(cur_dataset)
        if decision:
            logging.info("Found decision: %s", decision)
            return DecisionNode(None, None, cur_attr_value, decision)
        split_attribute, split_data, split_value = self.find_split_attribute(
            cur_dataset, cur_attributes
            )
        logging.info(
            "Split attribute: %s, split_value: %s", 
            split_attribute, split_value
            )
        new_attributes = cur_attributes[:]
        node = DecisionNode(split_attribute, split_value, cur_attr_value, None)
        if split_value is None:
            new_attributes.remove(split_attribute)
            node.children = [
                self.recursive_generate_tree(
                    sub_data, 
                    new_attributes,
                    self.attr_values[split_attribute][index],
                    most_frequent_decision
                    )
                for index, sub_data in enumerate(split_data)
                ]
        else:
            if same_numeric_attribute_value(cur_dataset, split_attribute):
                new_attributes.remove(split_attribute)
            node.children = [
                self.recursive_generate_tree(
                    sub_data, 
                    new_attributes,
                    None, 
                    most_frequent_decision
                    )
                for sub_data in split_data
                ]
        return node

    def calculate_infogain(self, dataset, attribute):
        sub_data = [[] for i in range(len(self.attr_values[attribute]))]
        value_counter = RecordCounter()
        child_counter = {
            attr_value: RecordCounter()
            for attr_value in self.attr_values[attribute]
        }
        for item in dataset:
            cls = item[CLASS_ATTRIBUTE]
            cls_count = item[CLASS_COUNTER]
            value_counter.record(cls, cls_count)
            child_counter[item[attribute]].record(cls, cls_count)
            for i in range(len(self.attr_values[attribute])):
                if item[attribute] == self.attr_values[attribute][i]:
                    sub_data[i].append(item)
        return information_gain(value_counter, child_counter), sub_data

    def get_prediction(self, object):
        node = self.tree
        while not node.decision:
            attribute = node.attribute
            if node.split_value is None:
                for child in node.children:
                    if child.attr_value == object[attribute]:
                        node = child
                        break
            else:
                if object[attribute] < node.split_value:
                    node = node.children[0]
                else:
                    node = node.children[1]
        return node.decision


def same_attribute_values(cur_dataset, cur_attributes):
    first_item = cur_dataset[0]
    for row in cur_dataset:
        for attribute in cur_attributes:
            if row[attribute] != first_item[attribute]:
                return False
    return True


def same_numeric_attribute_value(cur_dataset, attribute):
    first_value = cur_dataset[0][attribute]
    for row in cur_dataset:
        if row[attribute] != first_value:
            return False
    return True


def get_most_frequent_decision(dataset):
    counter = RecordCounter()
    for item in dataset:
        counter.record(item[CLASS_ATTRIBUTE], item[CLASS_COUNTER])
    most_frequent_class = counter.get_most_frequent_class()
    return most_frequent_class


def check_decision(dataset):
    # check if the most frequent decision / total records >= PRUNING_RATE
    counter = RecordCounter()
    total_records = 0
    for item in dataset:
        total_records += item[CLASS_COUNTER]
        counter.record(item[CLASS_ATTRIBUTE], item[CLASS_COUNTER])
    for key, value in counter.count.items():
        if value / total_records >= PRUNING_RATE:
            return key
    return None
