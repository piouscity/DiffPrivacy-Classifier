import logging

from settings import CLASS_ATTRIBUTE, PRUNING_RATE
from src.coverer.utility import RecordCounter, information_gain


class Node:
    def __init__(self, attribute, split_value, attr_value, decision):
        self.attribute = attribute
        self.split_value = split_value
        self.attr_value = attr_value
        self.decision = decision
        self.children = []


class C45:
    def __init__(self, dataset):
        self.data = dataset
        self.attributes = list(dataset[0].keys())
        self.attributes.remove(CLASS_ATTRIBUTE)
        self.attrValues = {
            attribute: []
            for attribute in self.attributes
        }
        self.tree = None
        self.counter = None
        for row in dataset:
            for key, value in row.items():
                if not isinstance(value, float) and key != CLASS_ATTRIBUTE:
                    self.attrValues[key].append(value)

        for attribute in self.attributes:
            self.attrValues[attribute] = list(set(self.attrValues[attribute]))

    def generate_decision_tree(self):
        self.tree = self.recursive_generate_tree(self.data, self.attributes, None,
                                            self.get_most_frequent_decision(self.data))

    def find_split_attribute(self, cur_dataset, cur_attributes):
        selected_attr = None
        best_infogain = -1.0*float("inf")
        best_split_value = None
        split_data = []
        for attribute in cur_attributes:
            if not self.attrValues[attribute]:
                # float attribute
                cur_dataset = sorted(cur_dataset, key=lambda k: k[attribute])
                counter = RecordCounter()
                for item in cur_dataset:
                    counter.record(item[CLASS_ATTRIBUTE])

                less_equal_counter = RecordCounter(list(counter.count.keys()))
                index = 0

                while index < len(cur_dataset)-1:
                    split_value = cur_dataset[index][attribute]
                    while index < len(cur_dataset) and cur_dataset[index][attribute] == split_value:
                        less_equal_counter.record(cur_dataset[index][CLASS_ATTRIBUTE])
                        index += 1

                    if index < len(cur_dataset):
                        greater_counter = counter - less_equal_counter
                        infogain_attr = information_gain(
                            counter, {'left': less_equal_counter, 'right': greater_counter})
                        if infogain_attr > best_infogain:
                            best_infogain = infogain_attr
                            selected_attr = attribute
                            best_split_value = split_value
                    else:
                        break
                less_equal = []
                greater = []
                if best_split_value:
                    for item in cur_dataset:
                        if item[attribute] <= best_split_value:
                            less_equal.append(item)
                        else:
                            greater.append(item)
                    split_data = [less_equal, greater]
            else:
                # category attribute
                infogain_attr, sub_data = self.calculate_infogain(cur_dataset, attribute)
                if infogain_attr > best_infogain:
                    selected_attr = attribute
                    best_infogain = infogain_attr
                    split_data = sub_data
                    best_split_value = None
        return selected_attr, split_data, best_split_value

    def recursive_generate_tree(self, cur_dataset, cur_attributes, cur_attr_value, most_frequent_decision):
        # current data is empty, return previous most frequent decision
        if len(cur_dataset) == 0:
            return Node(None, None, cur_attr_value, most_frequent_decision)
        # update most frequent decision
        most_frequent_decision = self.get_most_frequent_decision(cur_dataset)
        # current attributes is empty or all current attributes have the same values for all records
        # in current data, return current most frequent decision
        if len(cur_attributes) == 0 or self.same_attribute_values(cur_dataset, cur_attributes):
            return Node(None, None, cur_attr_value, most_frequent_decision)
        decision = self.check_decision(cur_dataset)
        if decision:
            return Node(None, None, cur_attr_value, decision)

        split_attribute, split_data, split_value = \
            self.find_split_attribute(cur_dataset, cur_attributes)
        logging.info("Split attribute: {}, split_value: {}".format(split_attribute, split_value))
        logging.info("Split data: {}".format(split_data))
        new_attributes = cur_attributes[:]
        node = Node(split_attribute, split_value, cur_attr_value, None)
        if not split_value:
            new_attributes.remove(split_attribute)
            node.children = [self.recursive_generate_tree(sub_data, new_attributes,
                                                          self.attrValues[split_attribute][index],
                                                          most_frequent_decision)
                             for index, sub_data in enumerate(split_data)]
        else:
            if self.same_numeric_attribute_value(cur_dataset, split_attribute):
                new_attributes.remove(split_attribute)
            node.children = [self.recursive_generate_tree(sub_data, new_attributes,
                                                          None, most_frequent_decision)
                             for sub_data in split_data]
        return node

    def calculate_infogain(self, dataset, attribute):
        sub_data = [[] for i in range(len(self.attrValues[attribute]))]
        value_counter = RecordCounter()
        child_counter = {
            attrValue: RecordCounter()
            for attrValue in self.attrValues[attribute]
        }
        for item in dataset:
            value_counter.record(item[CLASS_ATTRIBUTE])
            child_counter[item[attribute]].record(item[CLASS_ATTRIBUTE])
            for i in range(len(self.attrValues[attribute])):
                if item[attribute] == self.attrValues[attribute][i]:
                    sub_data[i].append(item)

        return information_gain(value_counter, child_counter), sub_data

    def same_attribute_values(self, cur_dataset, cur_attributes):
        item = cur_dataset[0]
        for row in cur_dataset:
            for attribute in cur_attributes:
                if row[attribute] != item[attribute]:
                    return False
        return True

    def same_numeric_attribute_value(self, cur_dataset, attribute):
        value = cur_dataset[0][attribute]
        for row in cur_dataset:
            if row[attribute] != value:
                return False
        return True

    def get_most_frequent_decision(self, dataset):
        counter = RecordCounter()
        for item in dataset:
            counter.record(item[CLASS_ATTRIBUTE])

        max_frequent = 0
        decision = None
        for key, value in counter.count.items():
            if value > max_frequent:
                max_frequent = value
                decision = key

        return decision

    def check_decision(self, dataset):
        # check if the most frequent decision / total records >= PRUNING_RATE
        counter = RecordCounter()
        for item in dataset:
            counter.record(item[CLASS_ATTRIBUTE])

        total_records = len(dataset)
        for key, value in counter.count.items():
            if float(value) / total_records >= PRUNING_RATE:
                return key

        return None

    def get_prediction(self, object):
        node = self.tree
        while not node.decision:
            attribute = node.attribute
            if not node.split_value:
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
